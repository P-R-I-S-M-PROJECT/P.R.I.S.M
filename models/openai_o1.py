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
    
    def generate_with_ai(self, prompt: str, skip_generation_prompt: bool = False, is_variation: bool = False, retry_count: int = 0) -> Optional[str]:
        """Generate code using OpenAI API with better error handling and retries"""
        try:
            if skip_generation_prompt:
                full_prompt = prompt
            else:
                # Check if this is a guided prompt (contains custom guidelines or specific requirements)
                is_guided = "=== IMPLEMENTATION REQUIREMENTS ===" in prompt or "Custom Requirements:" in prompt
                
                if is_guided:
                    # For guided mode, focus on user requirements
                    full_prompt = f"""=== PROCESSING SKETCH REQUIREMENTS ===
{prompt}

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

=== RETURN FORMAT ===
Return your code between these markers:
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE"""
                else:
                    # For non-guided mode, use the standard creative freedom prompt
                    full_prompt = self._build_generation_prompt(prompt)
            
            # If this is a retry, build error-specific prompt
            if retry_count > 0:
                full_prompt = self._build_error_prompt(prompt, self.last_error) if hasattr(self, 'last_error') else prompt
            
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
            
            # Process response and validate
            raw_content = response.choices[0].message.content
            self.log.debug(f"\n=== AI RESPONSE ===\n{raw_content}\n==================\n")
            
            code = self._extract_code_from_response(raw_content, is_variation)
            if not code:
                self.log.debug("Failed to extract code from response")
                return raw_content.strip()
            
            # Validate and store any error for retry context
            is_valid, error_msg = self.validate_creative_code(code, is_snippet=is_variation)
            if not is_valid:
                self.last_error = error_msg
                self.log.debug(f"\n=== VALIDATION ERROR ===\nCreative validation failed: {error_msg}\n==================\n")
                raise ValueError(f"Creative validation: {error_msg}")
            
            # Clear last error if successful
            if hasattr(self, 'last_error'):
                delattr(self, 'last_error')
            
            return code
            
        except Exception as e:
            self.log.error(f"AI generation error: {str(e)}")
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
        """Clean and prepare user code, ensuring proper structure"""
        try:
            # Fix common letterMask issues first
            code = re.sub(r'letterMask\s*\.\s*letterMask', 'letterMask', code)
            code = re.sub(r'letterMask\s*\.\s*$', 'letterMask.', code)
            code = re.sub(r'letterMask\s*\.\s*\n', 'letterMask.\n', code)
            
            # Auto-fix missing letterMask.background(0) if needed
            if 'letterMask.beginDraw()' in code and not re.search(r'letterMask\s*\.\s*background\s*\(\s*0\.?0?\s*\)', code):
                code = code.replace(
                    'letterMask.beginDraw();',
                    'letterMask.beginDraw();\n  letterMask.background(0);'
                )
            
            # Fix specific letterMask initialization sequence
            if 'letterMask.beginDraw()' in code:
                # Use the template with default text
                mask_init = self.TEXT_MASK_TEMPLATE.format(text="PRISM")
                # Indent properly
                mask_init = "\n".join("  " + line for line in mask_init.split("\n"))
                
                # Replace any existing letterMask initialization with the correct sequence
                code = re.sub(
                    r'letterMask\s*=\s*createGraphics\s*\([^)]*\)[^;]*;.*?letterMask\.endDraw\s*\(\s*\)\s*;',
                    mask_init,
                    code,
                    flags=re.DOTALL
                )
            
            # Remove any setup() or draw() functions
            code = re.sub(r'void\s+setup\s*\(\s*\)\s*{[^}]*}', '', code)
            code = re.sub(r'void\s+draw\s*\(\s*\)\s*{[^}]*}', '', code)
            
            # Remove system calls but preserve letterMask calls
            code = re.sub(r'(?<!letterMask\.)\bbackground\s*\([^)]*\);', '', code)  # Only remove non-letterMask background calls
            code = re.sub(r'\bsize\s*\([^)]*\);', '', code)
            code = re.sub(r'\bframeRate\s*\([^)]*\);', '', code)
            code = re.sub(r'\btranslate\s*\(\s*width\s*/\s*2[^)]*\);', '', code)
            code = re.sub(r'\btranslate\s*\(\s*height\s*/\s*2[^)]*\);', '', code)
            code = re.sub(r'\bsaveFrame\s*\([^)]*\);', '', code)
            code = re.sub(r'\bexit\s*\(\s*\);', '', code)
            
            # Clean up empty lines and whitespace
            code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
            code = code.strip()
            
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
        critical_forbidden = {
            r'(?<!\.)\bsize\s*\(': 'Contains size() call',
            r'(?<!letterMask\.)\bbackground\s*\(': 'Contains background() call',  # Allow letterMask.background()
            r'(?<!\.)\bframeRate\s*\(': 'Contains frameRate() call',
            r'(?<!\.)\bdraw\s*\(\s*\)': 'Contains draw() function',
        }
        
        # Check for critical forbidden elements
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
        
        # For text-based art, verify proper mask usage with more flexible patterns
        if 'text(' in code:
            # Check for missing mask elements with regex patterns
            missing_elements = []
            for pattern in self.TEXT_VALIDATION_PATTERNS:
                if not re.search(pattern, code, re.IGNORECASE | re.MULTILINE):
                    missing_elements.append(pattern)
            
            if missing_elements:
                # Auto-fix common issues in _clean_code before failing
                cleaned = self._clean_code(code)
                # Recheck after cleaning
                still_missing = []
                for pattern in self.TEXT_VALIDATION_PATTERNS:
                    if not re.search(pattern, cleaned, re.IGNORECASE | re.MULTILINE):
                        still_missing.append(pattern)
                
                if still_missing:
                    return False, f"Missing required mask elements: {', '.join(still_missing)}"
            
            # Check if text() is used directly on the canvas (not through mask)
            lines = code.split('\n')
            for line in lines:
                if 'text(' in line and not 'letterMask.text(' in line:
                    return False, "Text must only be drawn in the letterMask"
        
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

{f'Custom Requirements: {prompt_data["custom_guidelines"]}' if "custom_guidelines" in prompt_data and prompt_data["custom_guidelines"] else ''}

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

    def generate_code(self, prompt_data: dict, custom_guidelines: str = None) -> Optional[str]:
        """Generate code using the wizard prompt data"""
        try:
            creative_prompt = ""

            if custom_guidelines:
                creative_prompt = f"""{custom_guidelines}

=== IMPLEMENTATION REQUIREMENTS ==="""

                # Check if this is text art
                if prompt_data.get("is_text_art"):
                    text = prompt_data.get("text", "PRISM")
                    creative_prompt += "\n\n" + self._get_text_requirements(text)
            else:
                creative_prompt = """=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing animation that loops smoothly over 6 seconds.
Let your creativity guide the direction - feel free to explore and experiment.
It's better to do a few things well than try to include everything."""
            
            # Add selected techniques if any
            if prompt_data['techniques']:
                creative_prompt += f"\n\nRequired Techniques: {', '.join(prompt_data['techniques'])}"
            
            # Add other characteristics as supporting guidelines
            supporting_elements = []
            if prompt_data['motion_style']:
                supporting_elements.append(f"Motion Style: {prompt_data['motion_style']}")
            if prompt_data['shape_elements']:
                supporting_elements.append(f"Shape Elements: {prompt_data['shape_elements']}")
            if prompt_data['color_approach']:
                supporting_elements.append(f"Color Approach: {prompt_data['color_approach']}")
            if prompt_data['pattern_type']:
                supporting_elements.append(f"Pattern Type: {prompt_data['pattern_type']}")
            
            if supporting_elements:
                creative_prompt += "\n\nSupporting Characteristics:\n• " + "\n• ".join(supporting_elements)
            
            creative_prompt += """

Focus on smooth animation and visual harmony.
Use the progress variable (0.0 to 1.0) for animation timing.
Keep the code modular and efficient."""

            # Generate code using the creative prompt
            code = self.generate_with_ai(creative_prompt)
            
            return code
            
        except Exception as e:
            self.log.error(f"Error in code generation: {str(e)}")
            return None

    def _get_text_requirements(self, text: str = "PRISM") -> str:
        """Get formatted text requirements with proper mask initialization"""
        mask_code = self.TEXT_MASK_TEMPLATE.format(text=text)
        return self.TEXT_REQUIREMENTS.format(mask_code=mask_code)

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
        """Build error prompt for retry attempts with explicit requirements"""
        if 'letterMask.background(0)' in error_msg:
            return f"""
The previous code had the following error: {error_msg}

You MUST fix it by ensuring the code EXACTLY includes this line after letterMask.beginDraw():
    letterMask.background(0);

The complete required sequence is:
{self.TEXT_MASK_TEMPLATE.format(text="PRISM")}

Here is the previous code:
{code}

Return ONLY the creative code between the markers:
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE
"""
        elif 'text(' in error_msg:
            return f"""
The previous code had the following error: {error_msg}

You MUST use the PGraphics mask approach for text. Copy this EXACT sequence:
{self.TEXT_MASK_TEMPLATE.format(text="PRISM")}

Here is the previous code:
{code}

Return ONLY the creative code between the markers:
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE
"""
        else:
            return f"""
The previous code had the following error: {error_msg}

Please fix the error and ensure:
1. All code is between the markers
2. No setup() or draw() functions
3. No direct background() calls
4. No translate(width/2, height/2)
5. Proper Processing syntax

Here is the previous code:
{code}

Return ONLY the creative code between the markers:
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE
""" 