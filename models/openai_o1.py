from typing import Optional, List, Dict, Tuple
import re
from openai import OpenAI
from logger import ArtLogger
from config import Config
import random

class OpenAIO1Generator:
    # Class constants for text art
    TEXT_MASK_TEMPLATE = """PGraphics letterMask;
letterMask = createGraphics(1080, 1080);
letterMask.beginDraw();
letterMask.background(0);
letterMask.fill(255);
letterMask.textAlign(CENTER, CENTER);
letterMask.textSize(200);  // Adjust size as needed
letterMask.text("{text}", letterMask.width/2, letterMask.height/2);
letterMask.endDraw();"""

    TEXT_REQUIREMENTS = """=== CRITICAL: Text Integration Requirements ===
You MUST follow these requirements EXACTLY to create organic text that emerges from patterns:

1. Create Text Mask:
   REQUIRED - Copy this initialization code exactly:
{mask_code}

2. Pattern Integration:
   • Create an ArrayList of pattern elements (circles, particles, etc.)
   • Use letterMask.get(x, y) to check if a point is inside text
   • Only place/grow patterns where letterMask.get(x, y) brightness > 0
   • Let the text emerge naturally from pattern behavior

3. Animation:
   • Use the progress variable to animate pattern elements
   • Maintain smooth transitions and looping
   • Keep the text readable but organic"""

    # Required patterns for text art validation
    TEXT_VALIDATION_PATTERNS = [
        r'PGraphics\s+letterMask\s*;',
        r'letterMask\s*=\s*createGraphics\s*\(\s*1080\s*,\s*1080\s*\)',
        r'letterMask\s*\.\s*beginDraw\s*\(\s*\)',
        r'letterMask\s*\.\s*background\s*\(\s*0\.?0?\s*\)',
        r'letterMask\s*\.\s*fill\s*\(\s*255\s*\)',
        r'letterMask\s*\.\s*textAlign\s*\(\s*CENTER\s*,\s*CENTER\s*\)',
        r'letterMask\s*\.\s*textSize\s*\(\s*\d+',
        r'letterMask\s*\.\s*text\s*\(',
        r'letterMask\s*\.\s*endDraw\s*\(\s*\)'
    ]

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
            # Build the prompt based on context
            if retry_count > 0 and last_code and last_error:
                full_prompt = self._build_error_prompt(last_code, last_error)
            elif skip_generation_prompt:
                full_prompt = prompt
            else:
                # Check if this is a guided prompt
                is_guided = "=== IMPLEMENTATION REQUIREMENTS ===" in prompt or "Custom Requirements:" in prompt
                full_prompt = self._build_generation_prompt(prompt) if not is_guided else prompt
            
            # Log the attempt
            self.log.debug(f"\n=== SENDING TO AI (Attempt {retry_count + 1}/{max_retries}) ===\n{full_prompt}\n==================\n")
            
            # Use the model that was selected
            selected_model = self._select_o1_model(self.current_model)
            self.log.debug(f"Using model ID: {selected_model} (from {self.current_model})")
            
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            if not response.choices:
                raise ValueError("No response generated from AI")
            
            # Process response and validate
            raw_content = response.choices[0].message.content
            self.log.debug(f"\n=== AI RESPONSE ===\n{raw_content}\n==================\n")
            
            code = self._extract_code_from_response(raw_content, is_variation)
            if not code:
                raise ValueError("Failed to extract code from response")
            
            # Validate the generated code
            is_valid, error_msg = self.validate_creative_code(code, is_snippet=is_variation)
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

    def _build_generation_prompt(self, techniques: str) -> str:
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
• {', '.join(pattern_techniques)}"""
        
        return f"""=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing processing animation that loops smoothly over 6 seconds.
Let your creativity guide the direction - feel free to explore and experiment.
It's better to do a few things well than try to include everything.

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
Consider exploring these techniques: {techniques}
{f"Try something different than: {', '.join(avoid_patterns)}" if avoid_patterns else ""}
{additional_guidance}

=== RETURN FORMAT ===
Return your code between these markers:
// YOUR CREATIVE CODE GOES HERE
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

    def _clean_code(self, code: str, is_variation: bool = False) -> str:
        """Clean and prepare user code, with minimal interference to valid Processing code"""
        try:
            # Only clean up basic formatting issues
            lines = code.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Preserve indentation
                leading_space = len(line) - len(line.lstrip())
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith("//"):
                    cleaned_lines.append(" " * leading_space + line)
                    continue
                
                # Only remove explicitly forbidden system calls
                if any(call in line for call in [
                    "size(", 
                    "frameRate(", 
                    "saveFrame(", 
                    "exit()",
                    "translate(width/2",
                    "translate(height/2"
                ]):
                    continue
                
                # Keep the line with original indentation
                cleaned_lines.append(" " * leading_space + line)
            
            code = "\n".join(cleaned_lines)
            
            # Clean up multiple blank lines
            code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
            code = code.strip()
            
            return code
            
        except Exception as e:
            self.log.error(f"Error cleaning code: {e}")
            return code

    def _convert_arrays_to_arraylists(self, code: str) -> str:
        """Convert Java array syntax to ArrayList syntax"""
        # Find array declarations and initializations
        array_pattern = r'(\w+)\[\]\s+(\w+)\s*=\s*new\s+\1\[([^\]]+)\]'
        code = re.sub(array_pattern, r'ArrayList<\1> \2 = new ArrayList<\1>()', code)
        
        # Replace array access with ArrayList methods
        code = re.sub(r'(\w+)\[(\d+)\]', r'\1.get(\2)', code)
        code = re.sub(r'(\w+)\[(\w+)\]', r'\1.get(\2)', code)
        
        # Replace array assignments with ArrayList methods
        code = re.sub(r'(\w+)\[(\d+)\]\s*=\s*([^;]+)', r'\1.set(\2, \3)', code)
        code = re.sub(r'(\w+)\[(\w+)\]\s*=\s*([^;]+)', r'\1.set(\2, \3)', code)
        
        # Fix array length references
        code = re.sub(r'(\w+)\.length', r'\1.size()', code)
        
        return code

    def _fix_sort_implementation(self, sort_code: str) -> str:
        """Convert Java 8 style sort to Processing-compatible sort"""
        # Extract the list being sorted
        list_name = sort_code.split('.sort')[0].strip()
        
        # Create a Processing-compatible bubble sort implementation
        return f"""// Custom sort implementation
for (int i = 0; i < {list_name}.size() - 1; i++) {{
  for (int j = 0; j < {list_name}.size() - i - 1; j++) {{
    if ({list_name}.get(j).y > {list_name}.get(j + 1).y) {{
      PVector temp = {list_name}.get(j);
      {list_name}.set(j, {list_name}.get(j + 1));
      {list_name}.set(j + 1, temp);
    }}
  }}
}}"""

    def _extract_code_from_response(self, content: str, is_variation: bool = False) -> Optional[str]:
        """Extract and clean user code from AI response without template wrapping"""
        try:
            # Clean special characters and ensure ASCII compatibility
            content = content.encode('ascii', 'ignore').decode()
            content = re.sub(r'[^\x00-\x7F]+', '', content)
            
            # Remove ALL backticks and language markers
            content = re.sub(r'```\w*\n?', '', content)
            content = content.replace('```', '')
            
            # Extract code between markers
            code = self._extract_between_markers(
                content,
                "// YOUR CREATIVE CODE GOES HERE",
                "// END OF YOUR CREATIVE CODE"
            )
            
            # Clean and prepare code
            return self._clean_code(code, is_variation=is_variation)
            
        except Exception as e:
            self.log.error(f"Error extracting code: {str(e)}")
            return None

    def _extract_between_markers(self, code: str, start_marker: str, end_marker: str) -> str:
        """Extract code between markers for validation"""
        try:
            parts = code.split(start_marker)
            if len(parts) < 2:
                return code
            code = parts[1]
            parts = code.split(end_marker)
            if len(parts) < 1:
                return code
            return parts[0].strip()
        except Exception as e:
            self.log.error(f"Error extracting between markers: {e}")
            return code

    def validate_creative_code(self, code: str, is_snippet: bool = False) -> tuple[bool, str]:
        """Validate creative code with minimal interference, focusing only on critical issues"""
        if not code.strip():
            return False, "Empty code"
        
        # Check only for critical system-level functions that would break the sketch
        critical_forbidden = {
            r'\bsize\s*\(': 'Contains size() call - this is handled by the system',
            r'\bframeRate\s*\(': 'Contains frameRate() call - this is handled by the system',
            r'\bsaveFrame\s*\(': 'Contains saveFrame() call - this is handled by the system',
            r'\bexit\s*\(': 'Contains exit() call - this is handled by the system',
            r'\btranslate\s*\(\s*width\s*/\s*2': 'Contains origin re-centering - coordinates are already centered',
            r'\btranslate\s*\(\s*height\s*/\s*2': 'Contains origin re-centering - coordinates are already centered'
        }
        
        # Only check for truly forbidden elements
        for pattern, error in critical_forbidden.items():
            if re.search(pattern, code):
                return False, error
        
        # For text-based art, verify only critical mask requirements
        if 'text(' in code and not 'letterMask' in code:
            return False, "Text art requires letterMask for proper rendering"
        
        # For non-snippets, ensure only the absolutely required functions exist
        if not is_snippet:
            if not re.search(r'\bvoid\s+initSketch\s*\(\s*\)', code):
                return False, "Missing initSketch() function"
            if not re.search(r'\bvoid\s+runSketch\s*\(\s*float\s+\w+\s*\)', code):
                return False, "Missing runSketch(float progress) function"
        
        return True, None

    def _convert_to_processing(self, code: str) -> str:
        """Convert JavaScript syntax to Processing syntax"""
        # Replace variable declarations
        code = re.sub(r'\b(let|const|var)\s+(\w+)\s*=', r'float \2 =', code)
        
        # Fix for loop syntax
        code = re.sub(r'for\s*\(\s*(let|const|var)\s+(\w+)', r'for (int \2', code)
        
        # Replace forEach/map with for loops
        code = re.sub(r'\.forEach\s*\(\s*\w+\s*=>\s*{', r') {', code)
        code = re.sub(r'\.map\s*\(\s*\w+\s*=>\s*{', r') {', code)
        
        # Fix color syntax if needed
        code = re.sub(r'#([0-9a-fA-F]{6})', lambda m: f'color({int(m.group(1)[:2], 16)}, {int(m.group(1)[2:4], 16)}, {int(m.group(1)[4:], 16)})', code)
        
        # Fix Math functions
        math_funcs = {
            'Math.PI': 'PI',
            'Math.sin': 'sin',
            'Math.cos': 'cos',
            'Math.random': 'random',
            'Math.abs': 'abs',
            'Math.min': 'min',
            'Math.max': 'max'
        }
        for js, proc in math_funcs.items():
            code = code.replace(js, proc)
        
        return code 

    def _is_safe_code(self, code: str) -> bool:
        """Less strict validation of Processing syntax, focusing on critical issues"""
        errors = []
        
        # Extract just the user's code portion
        user_code = self._extract_between_markers(
            code,
            "// YOUR CREATIVE CODE GOES HERE",
            "// END OF YOUR CREATIVE CODE"
        )
        
        # Check for basic syntax errors
        syntax_errors = [
            (r'for\s*\([^)]*\.\s*\w+\)', "Invalid for loop syntax"),
            (r'while\s*\([^)]*\.\s*\w+\)', "Invalid while loop syntax"),
            (r'\w+\s+\.\s*\w+\s*\(', "Invalid method call syntax with space before dot"),
            (r'\w+\s*\.\s*$', "Incomplete object reference"),
            (r'\w+\s*\.\s*\)', "Invalid object reference in parentheses")
        ]
        
        for pattern, error in syntax_errors:
            if re.search(pattern, user_code):
                errors.append(error)
        
        # Check for critical JavaScript syntax that can't be auto-fixed
        critical_js_patterns = [
            (r'color\(([\'"]#[0-9a-fA-F]+[\'"]\))', "Use RGB values instead of hex codes: color(255, 0, 0)"),
            (r'\b(push|pop)\s*\(\s*\)', "Use pushMatrix()/popMatrix() instead of push()/pop()"),
            (r'createVector\s*\(', "Use 'new PVector()' instead of createVector()"),
        ]
        
        for pattern, error in critical_js_patterns:
            if re.search(pattern, user_code):
                errors.append(error)
        
        if errors:
            error_msg = "\n• ".join(errors)
            self.log.error(f"Code validation errors found:\n• {error_msg}")
            return False
        
        return True

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

    def build_processing_template(self, code: str, version: int) -> str:
        """Build the complete Processing template with the given code.
        
        Args:
            code: The creative code to insert
            version: The version number for the render path
            
        Returns:
            The complete Processing template with the code inserted
        """
        return f"""// === USER'S CREATIVE CODE ===
{code}
// END OF YOUR CREATIVE CODE

// === SYSTEM FRAMEWORK ===
void setup() {{
    size(1080, 1080);
    frameRate(60);
    smooth();
    initSketch();  // Initialize user's sketch
}}

final int totalFrames = 360;
boolean hasError = false;

void draw() {{
    try {{
        background(0);
        stroke(255);  // Default stroke but can be changed
        float progress = float(frameCount % totalFrames) / totalFrames;
        translate(width/2, height/2);
        
        runSketch(progress);  // Run user's sketch with current progress
        
        String renderPath = "renders/render_v{version}";
        saveFrame(renderPath + "/frame-####.png");
        if (frameCount >= totalFrames) {{
            exit();
        }}
    }} catch (Exception e) {{
        println("Error in draw(): " + e.toString());
        hasError = true;
        exit();
    }}
}}"""  # Note: Added closing triple quote and removed trailing space 

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
        return (
            "=== TEXT ART REQUIREMENTS ===\n"
            f"• Create art using the text: {text}\n"
            "• Text should be clearly visible and readable\n"
            "• Animate the text in an engaging way\n"
            "• Consider using multiple instances or layers\n"
            "• Experiment with scale, rotation, and opacity\n"
            "• Add complementary visual elements\n"
            "• Ensure smooth transitions between states"
        )

    def _build_creative_prompt(self, motion: str, shapes: str, colors: str, pattern: str, custom_guidelines: str = "") -> dict:
        """Build the creative prompt from selected options"""
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
        is_text_requirement = custom_guidelines and any(word in custom_guidelines.lower() for word in ['text', 'spell', 'word', 'letter'])
        
        # If text requirement, add specific mask-based guidance
        if is_text_requirement:
            prompt["text_requirements"] = self.TEXT_REQUIREMENTS.format(mask_code=self.TEXT_MASK_TEMPLATE.format(text=custom_guidelines))
            
        return prompt 

    def _build_error_prompt(self, code: str, error_msg: str = None) -> str:
        """Build error prompt focusing on actual Processing compilation errors"""
        base_context = (
            "The previous code generated an error. Please fix the issues while maintaining the core functionality.\n\n"
            "=== PREVIOUS ERROR ===\n"
            f"{error_msg}\n\n"
            "=== PROCESSING REQUIREMENTS ===\n"
            "• Must define initSketch() and runSketch(progress)\n"
            "• The system handles setup(), draw(), size(), and frameRate\n"
            "• The canvas is already centered at (0,0)\n"
            "• All animations must use the progress variable (0.0 to 1.0)\n"
        )

        # Add specific guidance only for actual Processing errors
        specific_guidance = ""
        
        if error_msg:
            if "text" in error_msg.lower():
                specific_guidance += (
                    "\n=== TEXT REQUIREMENTS ===\n"
                    "• Use letterMask for text rendering\n"
                    "• Initialize letterMask properly\n"
                    f"{self.TEXT_MASK_TEMPLATE.format(text='PRISM')}\n"
                )
            elif "missing" in error_msg.lower() and ";" in error_msg:
                specific_guidance += (
                    "\n=== SYNTAX GUIDE ===\n"
                    "• Check for missing semicolons at the end of statements\n"
                    "• Ensure proper function and class declarations\n"
                    "• Verify bracket matching and closure\n"
                )

        return f"""{base_context}{specific_guidance}

=== PREVIOUS CODE ===
{code}

Please fix the issues and return ONLY the corrected code between these markers:
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE""" 