from typing import Optional, List, Dict, Tuple
import re
from openai import OpenAI
from logger import ArtLogger
from config import Config
import random
from .text_generator import TextGenerator
from .validation import CodeValidator

class OpenAIO1Generator:
    def __init__(self, config: Config, logger: ArtLogger = None):
        self.config = config
        self.log = logger or ArtLogger()
        self.client = OpenAI(api_key=config.openai_key)
        # Track current model
        self.current_model = None
        # Model ID mapping
        self.model_ids = {
            'o1': 'o1',  # Correct model ID
            'o1-mini': 'o1-mini'  # Correct model ID
        }
        # Initialize text generator and validator
        self.text_generator = TextGenerator(logger=self.log)
        self.validator = CodeValidator(logger=self.log, text_generator=self.text_generator)
        # Initialize selected techniques
        self.selected_techniques = []
    
    def _select_o1_model(self, model: str = None) -> str:
        """Get the appropriate O1 model to use"""
        if model in ['o1', 'o1-mini']:
            self.current_model = model
            return self.model_ids[model]
            
        # If no model specified and we have a current model, keep using it
        if self.current_model in ['o1', 'o1-mini']:
            return self.model_ids[self.current_model]
        
        # Only default to o1-mini if we have no current model
        self.current_model = 'o1-mini'
        return self.model_ids['o1-mini']
    
    def generate_with_ai(self, prompt: str, skip_generation_prompt: bool = False, is_variation: bool = False, retry_count: int = 0, max_retries: int = 3, last_code: str = None, last_error: str = None) -> Optional[str]:
        """Generate code using OpenAI API with improved error handling and retries"""
        try:
            # Check if this is text art and extract text if present
            is_text_art = self.text_generator.is_text_requirement(prompt)
            text = "PRISM"  # Default text
            if is_text_art:
                text_match = re.search(r'text\s+[\'"]([^\'"]+)[\'"]', prompt)
                if text_match:
                    text = text_match.group(1)
            
            # Build the prompt based on context
            if retry_count > 0 and last_code and last_error:
                # Try auto-injection first
                fixed_code = self.validator.inject_base_code(last_code, is_text_art, text)
                if fixed_code != last_code:
                    self.log.info("Auto-injected missing code stubs")
                    return fixed_code
                
                # If can't auto-fix, build focused retry prompt
                full_prompt = self.validator.build_retry_prompt(last_code, last_error, retry_count)
            elif skip_generation_prompt:
                # Even for skipped prompts, ensure stubs are present
                full_prompt = f"{self.validator.inject_minimal_stubs(is_text_art, text)}\n\n{prompt}"
            else:
                # Check if this is a guided prompt
                is_guided = "=== IMPLEMENTATION REQUIREMENTS ===" in prompt or "Custom Requirements:" in prompt
                full_prompt = self._build_generation_prompt(prompt, is_text_art, text) if not is_guided else prompt
            
            # Log the attempt
            self.log.debug(f"\n=== SENDING TO AI (Attempt {retry_count + 1}/{max_retries}) ===\n{full_prompt}\n==================\n")
            
            # Use the model that was selected
            selected_model = self._select_o1_model(self.current_model)
            self.log.debug(f"Using model ID: {selected_model} (from {self.current_model})")
            
            # Escape any curly braces in the prompt
            safe_prompt = full_prompt.replace("{", "{{").replace("}", "}}")
            
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "user", "content": safe_prompt}
                ]
            )
            
            if not response.choices:
                raise ValueError("No response generated from AI")
                
            # Process response and validate
            raw_content = response.choices[0].message.content
            self.log.debug(f"\n=== AI RESPONSE ===\n{raw_content}\n==================\n")
            
            code = self.validator.extract_code_from_response(raw_content, is_variation)
            if not code:
                raise ValueError("Failed to extract code from response")
                
            # Auto-inject required code before validation
            code = self.validator.inject_base_code(code, is_text_art, text)
            
            # Validate the generated code
            is_valid, error_msg = self.validator.validate_creative_code(code, is_snippet=is_variation, is_text_art=is_text_art)
            if not is_valid:
                self.log.debug(f"\n=== VALIDATION ERROR ===\nCreative validation failed: {error_msg}\n==================\n")
                
                # Attempt retry if we haven't exceeded max retries
                if retry_count < max_retries:
                    self.log.debug(f"Attempting retry {retry_count + 1}/{max_retries}")
                    return self.generate_with_ai(
                        prompt=prompt,
                        skip_generation_prompt=skip_generation_prompt,
                        is_variation=is_variation,
                        retry_count=retry_count + 1,
                        max_retries=max_retries,
                        last_code=code,  # Pass the failed code
                        last_error=error_msg  # Pass the error message
                    )
                else:
                    raise ValueError(f"Max retries ({max_retries}) exceeded. Last error: {error_msg}")
                
            return code
            
        except Exception as e:
            self.log.error(f"AI generation error: {str(e)}")
            
            # Attempt retry if we haven't exceeded max retries
            if retry_count < max_retries:
                self.log.debug(f"Attempting retry {retry_count + 1}/{max_retries} after error: {str(e)}")
                return self.generate_with_ai(
                    prompt=prompt,
                    skip_generation_prompt=skip_generation_prompt,
                    is_variation=is_variation,
                    retry_count=retry_count + 1,
                    max_retries=max_retries,
                    last_code=last_code,  # Preserve any previous code
                    last_error=str(e)  # Use the exception message as error
                )
            
            return None

    def _build_generation_prompt(self, techniques: str, is_text_art: bool = False, text: str = "PRISM") -> str:
        """Build a focused creative prompt with clearer guidance"""
        # Get historical patterns to avoid repetition
        recent_patterns = self.config.db_manager.get_recent_patterns(limit=3)
        historical_techniques = self.config.db_manager.get_historical_techniques(limit=5)
        avoid_patterns = self._get_avoid_patterns(recent_patterns, historical_techniques)
        
        # Only get random techniques if none were provided
        additional_guidance = ""
        if not techniques:
            geometry_techniques = self._get_random_techniques_from_category('geometry', 3)
            motion_techniques = self._get_random_techniques_from_category('motion', 3)
            pattern_techniques = self._get_random_techniques_from_category('patterns', 3)
            
            additional_guidance = f"""
=== SUGGESTED TECHNIQUES ===
Form & Structure:
• {', '.join(geometry_techniques)}

Movement & Flow:
• {', '.join(motion_techniques)}

Pattern & Texture:
• {', '.join(pattern_techniques)}
"""
        
        # Get base Processing requirements
        processing_requirements = self.validator.get_processing_requirements()
        
        # Add text art requirements if needed
        if is_text_art:
            processing_requirements += "\n\n" + self.validator.TEXT_ART_REQUIREMENTS
        
        # Get minimal stubs that must be present
        code_stubs = self.validator.inject_minimal_stubs(is_text_art, text)
        
        return f"""=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing processing animation that loops smoothly over 6 seconds.
Let your creativity guide the direction - feel free to explore and experiment.
It's better to do a few things well than try to include everything.

{processing_requirements}

=== STARTING CODE STUBS ===
Start with these required function stubs and modify them:

{code_stubs}

=== CREATIVE DIRECTION ===
Consider exploring these techniques: {techniques}
{f"Try something different than: {', '.join(avoid_patterns)}" if avoid_patterns else ""}
{additional_guidance}

=== RETURN FORMAT ===
Return your code between these markers:
// YOUR CREATIVE CODE GOES HERE
[your code here]
// END OF YOUR CREATIVE CODE"""

    def _get_avoid_patterns(self, recent_patterns, historical_techniques, max_avoid=5) -> List[str]:
        """Helper method to build list of patterns to avoid"""
        avoid_patterns = []
        
        # Add techniques from recent patterns
        if recent_patterns:
            recent_techniques = [tech for pattern in recent_patterns for tech in pattern.techniques]
            avoid_patterns.extend(recent_techniques)
        
        # Add commonly used historical techniques
        if historical_techniques:
            recent_combos = [tech for pattern in historical_techniques for tech in pattern]
            from collections import Counter
            common_techniques = Counter(recent_combos).most_common(3)
            avoid_patterns.extend(tech for tech, _ in common_techniques)
        
        # Remove duplicates and limit
        return list(dict.fromkeys(avoid_patterns))[:max_avoid]

    def _get_random_techniques_from_category(self, category: str, count: int = 3) -> List[str]:
        """Get random techniques from a specific category in config"""
        if category not in self.config.technique_categories:
            return []
        
        techniques = self.config.technique_categories[category]
        # Ensure we don't try to get more items than available
        count = min(count, len(techniques))
        return random.sample(techniques, count)

    def build_processing_template(self, code: str, version: int) -> str:
        """Build the complete Processing template with the given code"""
        return self.validator.build_processing_template(code, version)

    def create_variation(self, original_code: str, modification: str, retry_count: int = 0) -> Optional[str]:
        """Create a variation of existing Processing code using O1 model."""
        # Build simple, focused prompt
        base_prompt = f"""Modify this Processing code according to the user's request.
Keep the core animation logic but apply the changes.

Original code:
{original_code}

Requested changes: {modification}

Rules:
- Keep the animation smooth and looping
- Keep the progress variable (0.0 to 1.0)
- Keep initSketch() and runSketch(progress) functions
- Don't include setup() or draw()
- Keep coordinates relative to (0,0)

Return ONLY the modified code between these markers:
// YOUR CREATIVE CODE GOES HERE
[your code here]
// END OF YOUR CREATIVE CODE"""

        # Add minimal retry context if needed
        if retry_count > 0:
            base_prompt += "\n\nPrevious attempt failed. Ensure code is between markers and uses Processing syntax."

        # Generate variation
        self._select_o1_model('o1')
        # Pass is_variation=True to handle validation correctly
        response = self.generate_with_ai(base_prompt, skip_generation_prompt=True, is_variation=True)
        
        # generate_with_ai already handles extraction, cleaning, and validation
        return response

    def generate_with_wizard(self, prompt_data: dict) -> Optional[str]:
        """Generate code using wizard-provided parameters"""
        techniques_str = ", ".join(prompt_data["techniques"])
        
        # Build creative direction section
        creative_direction = f"""Create a dynamic Processing animation with these characteristics:

Base Techniques: {techniques_str}
Motion Style: {prompt_data["motion_style"]}
Shape Elements: {prompt_data["shape_elements"]}
Color Approach: {prompt_data["color_approach"]}
Pattern Type: {prompt_data["pattern_type"]}

{f'Custom Requirements: {prompt_data["custom_guidelines"]}' if "custom_guidelines" in prompt_data and prompt_data["custom_guidelines"] else ''}

Focus on smooth animation and visual harmony.
Use the progress variable (0.0 to 1.0) for animation timing.
Keep the code modular and efficient."""

        # Add O1-specific framework
        full_prompt = f"""=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing processing based animation that loops smoothly over 6 seconds.
Let your creativity guide the direction - feel free to experiment and innovate.

=== REQUIRED FUNCTIONS ===
You MUST define these two functions:
1. void initSketch() - Called once at start
2. void runSketch(float progress) - Called each frame with progress (0.0 to 1.0)

=== SYSTEM FRAMEWORK ===
The system automatically handles these - DO NOT include them:
• void setup() or draw() functions
• size(1080, 1080) and frameRate settings
• background(0) or any background clearing
• translate(width/2, height/2) for centering
• Frame saving and program exit

=== CODE STRUCTURE ===
1. Define any classes at the top
2. Declare global variables
3. Define initSketch() for setup
4. Define runSketch(progress) for animation
• The canvas is already centered at (0,0)
• Initialize all variables with values
• Use RGB values for colors (e.g., stroke(255, 0, 0) for red)

=== CREATIVE DIRECTION ===
{creative_direction}

=== RETURN FORMAT ===
Return your code between these markers:
// YOUR CREATIVE CODE GOES HERE
[your code here]
// END OF YOUR CREATIVE CODE"""

        # Use the standard generation pipeline with the wizard prompt
        return self.generate_with_ai(full_prompt, skip_generation_prompt=True)

    def generate_code(self, prompt_data: dict, custom_guidelines: str = None, retry_count: int = 0) -> Optional[str]:
        """Generate code using the wizard prompt data"""
        try:
            # Build base prompt with Processing requirements
            base_prompt = (
                "=== PROCESSING SKETCH GENERATOR ===\n"
                "Create a visually appealing processing animation that loops smoothly over 6 seconds.\n"
                "Let your creativity guide the direction - feel free to explore and experiment.\n\n"
                "=== REQUIRED FUNCTIONS ===\n"
                "You MUST define these two functions:\n"
                "1. void initSketch() - Called once at start\n"
                "2. void runSketch(float progress) - Called each frame with progress (0.0 to 1.0)\n\n"
                "=== SYSTEM FRAMEWORK ===\n"
                "The system automatically handles these - DO NOT include them:\n"
                "• void setup() or draw() functions\n"
                "• size(1080, 1080) and frameRate settings\n"
                "• background(0) or any background clearing\n"
                "• translate(width/2, height/2) for centering\n"
                "• Frame saving and program exit\n\n"
                "=== CODE STRUCTURE ===\n"
                "1. Define any classes at the top\n"
                "2. Declare global variables\n"
                "3. Define initSketch() for setup\n"
                "4. Define runSketch(progress) for animation\n"
                "• The canvas is already centered at (0,0)\n"
                "• Initialize all variables with values\n"
                "• Use RGB values for colors (e.g., stroke(255, 0, 0) for red)\n"
            )

            # Add creative direction from prompt data
            creative_direction = []
            if prompt_data.get('techniques'):
                creative_direction.append(f"Required Techniques: {', '.join(prompt_data['techniques'])}")
            if prompt_data.get('motion_style'):
                creative_direction.append(f"Motion Style: {prompt_data['motion_style']}")
            if prompt_data.get('shape_elements'):
                creative_direction.append(f"Shape Elements: {prompt_data['shape_elements']}")
            if prompt_data.get('color_approach'):
                creative_direction.append(f"Color Approach: {prompt_data['color_approach']}")
            if prompt_data.get('pattern_type'):
                creative_direction.append(f"Pattern Type: {prompt_data['pattern_type']}")

            if creative_direction:
                base_prompt += "\n\n=== CREATIVE DIRECTION ===\n• " + "\n• ".join(creative_direction)

            # Add mode-specific requirements
            if prompt_data.get("illusion_categories"):
                base_prompt += f"\n\n=== OPTICAL ILLUSION REQUIREMENTS ===\nCreate a dynamic optical illusion using these categories: {', '.join(prompt_data['illusion_categories'])}\nFocus on strong perceptual impact and smooth execution."

            # Add custom guidelines from either source
            guidelines = prompt_data.get("custom_guidelines") or custom_guidelines
            if guidelines:
                base_prompt += f"\n\n=== CUSTOM REQUIREMENTS ===\n{guidelines}"

            # Add text-specific requirements if needed
            if prompt_data.get("is_text_art"):
                text = prompt_data.get("text", "PRISM")
                base_prompt += "\n\n" + self._get_text_requirements(text)

            # Add animation guidelines
            base_prompt += (
                "\n\n=== ANIMATION GUIDELINES ===\n"
                "• Use the progress variable (0.0 to 1.0) for ALL animations\n"
                "• Ensure smooth looping by matching start/end states\n"
                "• Use map() to convert progress to specific ranges\n"
                "• Use lerp() or lerpColor() for smooth transitions\n"
                "• Avoid sudden jumps or discontinuities\n"
                "• Consider easing functions for natural motion\n"
                "• Test values at progress = 0.0, 0.5, and 1.0\n\n"
                "=== RETURN FORMAT ===\n"
                "Return your code between these markers:\n"
                "// YOUR CREATIVE CODE GOES HERE\n"
                "[your code here]\n"
                "// END OF YOUR CREATIVE CODE"
            )
            
            # Generate code using the enhanced prompt
            code = self.generate_with_ai(base_prompt, skip_generation_prompt=True, retry_count=retry_count)
            return code
            
        except Exception as e:
            self.log.error(f"Error in code generation: {str(e)}")
            return None

    def _get_text_requirements(self, text: str) -> str:
        """Get text-specific requirements for text art generation"""
        return self.text_generator.get_text_requirements(text)

    def _build_creative_prompt(self, motion: str, shapes: str, colors: str, pattern: str, custom_guidelines: str = "") -> dict:
        """Build the creative prompt from selected options"""
        # If no techniques selected, get them from config
        if not self.selected_techniques:
            self.selected_techniques = self._get_random_techniques_from_category('all', 3)

        prompt = {
            "techniques": self.selected_techniques,
            "motion_style": motion,
            "shape_elements": shapes,
            "color_approach": colors,
            "pattern_type": pattern,
        }
        
        if custom_guidelines:
            prompt["custom_guidelines"] = custom_guidelines
            
        # Check if this is a text-based requirement
        if self.text_generator.is_text_requirement(custom_guidelines):
            prompt.update(self.text_generator.build_text_prompt(custom_guidelines))
            
        return prompt

    def _build_error_prompt(self, code: str, error_msg: str = None) -> str:
        """Build error prompt focusing on actual Processing compilation errors"""
        base_context = (
            "The previous code generated an error. Please fix the issues while maintaining the core functionality.\n\n"
            "=== PREVIOUS ERROR ===\n"
            f"{error_msg}\n\n"
            f"{self.validator.get_processing_requirements()}\n\n"
            f"{self.validator.build_error_guidance(error_msg)}\n"
        )

        # Add text-specific guidance if needed
        if error_msg and "text" in error_msg.lower():
            base_context += self.text_generator.build_text_error_guidance()

        return f"""{base_context}

=== PREVIOUS CODE ===
{code}

Please fix the issues and return ONLY the corrected code between these markers:
// YOUR CREATIVE CODE GOES HERE
[your code here]
// END OF YOUR CREATIVE CODE""" 