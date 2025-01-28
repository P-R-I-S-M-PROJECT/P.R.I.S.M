from typing import Optional, List, Dict, Tuple
import re
from openai import OpenAI
from logger import ArtLogger
from config import Config
import random

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
    
    def generate_with_ai(self, prompt: str, skip_generation_prompt: bool = False, is_variation: bool = False) -> Optional[str]:
        """Generate code using OpenAI API with better error handling"""
        try:
            if skip_generation_prompt:
                full_prompt = prompt
            else:
                # Add the O1-specific framework around the creative prompt
                full_prompt = f"""=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing animation that loops smoothly over 6 seconds.
Let your creativity guide the direction - feel free to explore and experiment.

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
{prompt}

=== RETURN FORMAT ===
Return your code between these markers:
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE"""
            
            # Log the full prompt being sent
            self.log.debug(f"\n=== SENDING TO AI ===\n{full_prompt}\n==================\n")
            
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
                self.log.error("No response generated from AI")
                return None
                
            # Log the raw response first (this is safe)
            raw_content = response.choices[0].message.content
            self.log.debug(f"\n=== AI RESPONSE ===\n{raw_content}\n==================\n")
            
            # Then try to log any available metadata
            self.log.debug("\n=== RESPONSE METADATA ===")
            try:
                self.log.debug(f"Model: {response.model}")
                self.log.debug(f"Usage: {response.usage}")
                self.log.debug(f"Created: {response.created}")
            except AttributeError as e:
                self.log.debug(f"Some metadata not available: {e}")
            self.log.debug("==================\n")
            
            code = self._extract_code_from_response(raw_content, is_variation)
            if not code:
                self.log.debug("Failed to extract code from response")
                return raw_content.strip()  # Return the raw content if no markers found
                
            # Log the extracted code
            self.log.debug(f"\n=== EXTRACTED CODE ===\n{code}\n==================\n")
            
            # Validate creative code first, using is_variation to determine validation type
            is_valid, error_msg = self.validate_creative_code(code, is_snippet=is_variation)
            if not is_valid:
                self.log.debug(f"\n=== VALIDATION ERROR ===\nCreative validation failed: {error_msg}\n==================\n")
                raise ValueError(f"Creative validation: {error_msg}")
            
            # Convert any remaining JavaScript syntax to Processing
            code = self._convert_to_processing(code)
            
            # Final safety check
            if not self._is_safe_code(code):
                self.log.debug("\n=== VALIDATION ERROR ===\nFailed final safety check\n==================\n")
                return None
                
            return code
            
        except Exception as e:
            self.log.error(f"AI generation error: {str(e)}")
            self.log.debug(f"Current model: {self.current_model}, Selected model ID: {selected_model if 'selected_model' in locals() else 'not selected yet'}")
            return None

    def _build_generation_prompt(self, techniques: str) -> str:
        """Build a focused creative prompt with clearer guidance"""
        # Get historical patterns to avoid repetition
        recent_patterns = self.config.db_manager.get_recent_patterns(limit=3)
        historical_techniques = self.config.db_manager.get_historical_techniques(limit=5)
        avoid_patterns = self._get_avoid_patterns(recent_patterns, historical_techniques)
        
        # Get random subset of techniques from each category for inspiration
        geometry_techniques = self._get_random_techniques_from_category('geometry', 3)
        motion_techniques = self._get_random_techniques_from_category('motion', 3)
        pattern_techniques = self._get_random_techniques_from_category('patterns', 3)
        
        return f"""=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing animation that loops smoothly over 6 seconds.
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

=== TECHNIQUES & APPROACHES ===
Form & Structure:
• {', '.join(geometry_techniques)}

Movement & Flow:
• {', '.join(motion_techniques)}

Pattern & Texture:
• {', '.join(pattern_techniques)}

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
        """Clean and prepare user code, ensuring proper structure"""
        try:
            # Remove any setup() or draw() functions
            code = re.sub(r'void\s+setup\s*\(\s*\)\s*{[^}]*}', '', code)
            code = re.sub(r'void\s+draw\s*\(\s*\)\s*{[^}]*}', '', code)
            
            # Remove any system calls that are handled by the framework
            code = re.sub(r'\bbackground\s*\([^)]*\);', '', code)
            code = re.sub(r'\bsize\s*\([^)]*\);', '', code)
            code = re.sub(r'\bframeRate\s*\([^)]*\);', '', code)
            code = re.sub(r'\btranslate\s*\(\s*width\s*/\s*2[^)]*\);', '', code)
            code = re.sub(r'\btranslate\s*\(\s*height\s*/\s*2[^)]*\);', '', code)
            code = re.sub(r'\bsaveFrame\s*\([^)]*\);', '', code)
            code = re.sub(r'\bexit\s*\(\s*\);', '', code)
            
            # Fix common syntax issues
            code = re.sub(r'(\w+)\s*\.\s*(\w+)', r'\1.\2', code)  # Fix spaced dots
            code = re.sub(r'for\s*\(\s*int\s+(\w+)\s*=\s*0\s*;\s*\1\s*<\s*(\w+)\s*\.\s*(\w+)\s*;', r'for (int \1 = 0; \1 < \2.\3;', code)  # Fix for loop syntax
            
            # Fix malformed function declarations where comments merge with function
            code = re.sub(r'([^\n]+)void\s+(\w+)\s*\(', r'\1\nvoid \2(', code)
            
            # Clean up empty lines and whitespace
            code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
            code = code.strip()
            
            # Only add missing functions for non-variation code
            if not is_variation:
                if not re.search(r'\bvoid\s+initSketch\s*\(\s*\)', code):
                    code += '\n\nvoid initSketch() {\n  // Initialize sketch\n}'
                if not re.search(r'\bvoid\s+runSketch\s*\(\s*float\s+\w+\s*\)', code):
                    code += '\n\nvoid runSketch(float progress) {\n  // Update sketch\n}'
            
            return code
            
        except Exception as e:
            self.log.error(f"Error cleaning code: {e}")
            return code

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
        """Validate creative code for forbidden elements"""
        if not code.strip():
            return False, "Empty code"
        
        # Check for critical system-level functions that would break the sketch
        # Use more precise patterns to avoid false positives
        critical_forbidden = {
            r'(?<!\.)\bsize\s*\(': 'Contains size() call',  # Negative lookbehind to avoid matching list.size()
            r'(?<!\.)\bbackground\s*\(': 'Contains background() call',
            r'(?<!\.)\bframeRate\s*\(': 'Contains frameRate() call',
            r'(?<!\.)\bdraw\s*\(\s*\)': 'Contains draw() function',  # Match function definition
        }
        
        # Check for critical forbidden elements with better pattern matching
        for pattern, error in critical_forbidden.items():
            if re.search(pattern, code):
                return False, error
        
        # Check for absolute translations that would re-center the origin
        translation_patterns = [
            r'translate\s*\(\s*width\s*/\s*2',
            r'translate\s*\(\s*height\s*/\s*2',
        ]
        
        for line in code.split('\n'):
            line = line.strip()
            if any(re.search(pattern, line) for pattern in translation_patterns):
                return False, "Contains origin re-centering - coordinates are already centered"
        
        # For non-snippets, ensure required functions exist with proper signatures
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

Focus on smooth animation and visual harmony.
Use the progress variable (0.0 to 1.0) for animation timing.
Keep the code modular and efficient."""

        # Add O1-specific framework
        full_prompt = f"""=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing animation that loops smoothly over 6 seconds.
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