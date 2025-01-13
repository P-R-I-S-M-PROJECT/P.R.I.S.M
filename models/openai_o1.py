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
            
        # Default to o1-mini if not specified
        self.current_model = 'o1-mini'
        return self.model_ids['o1-mini']
    
    def generate_with_ai(self, prompt: str) -> Optional[str]:
        """Generate code using OpenAI API with better error handling"""
        try:
            # Build a focused creative prompt
            structured_prompt = self._build_generation_prompt(prompt)
            
            # Add artistic context prefix
            context = """You're a creative coder crafting generative art with Processing. 
Express your artistic vision through code - feel free to experiment and innovate.
Just remember to use Processing's Java-style syntax as your medium."""
            
            full_prompt = context + "\n\n" + structured_prompt
            
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
            
            code = self._extract_code_from_response(raw_content)
            if not code:
                self.log.debug("Failed to extract code from response")
                return raw_content.strip()  # Return the raw content if no markers found
                
            # Log the extracted code
            self.log.debug(f"\n=== EXTRACTED CODE ===\n{code}\n==================\n")
            
            # Validate creative code first
            is_valid, error_msg = self.validate_creative_code(code)
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
• size(800, 800) and frameRate settings
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

    def _clean_code(self, code: str) -> str:
        """Clean and prepare user code, ensuring proper structure"""
        try:
            # Remove any setup() or draw() functions
            code = re.sub(r'void\s+setup\s*\(\s*\)\s*{[^}]*}', '', code)
            code = re.sub(r'void\s+draw\s*\(\s*\)\s*{[^}]*}', '', code)
            
            # Remove any system calls that are handled by the framework
            code = re.sub(r'\s*background\([^)]*\);', '', code)
            code = re.sub(r'\s*size\([^)]*\);', '', code)
            code = re.sub(r'\s*frameRate\([^)]*\);', '', code)
            code = re.sub(r'\s*translate\(width/2[^)]*\);', '', code)
            code = re.sub(r'\s*translate\(height/2[^)]*\);', '', code)
            code = re.sub(r'\s*saveFrame\([^)]*\);', '', code)
            code = re.sub(r'\s*exit\(\);', '', code)
            
            # Ensure class definitions are at top level
            code = re.sub(r'(class\s+\w+\s*{[^}]*})\s*void', r'\1\n\nvoid', code)
            
            # Clean up empty lines and whitespace
            code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
            code = code.strip()
            
            # Ensure required functions exist with proper structure
            if 'void initSketch()' not in code:
                code += '\n\nvoid initSketch() {\n  // Initialize sketch\n}'
            if 'void runSketch(float progress)' not in code:
                code += '\n\nvoid runSketch(float progress) {\n  // Update sketch\n}'
            
            return code
            
        except Exception as e:
            self.log.error(f"Error cleaning code: {e}")
            return code

    def _extract_code_from_response(self, content: str) -> Optional[str]:
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
            return self._clean_code(code)
            
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

    def validate_creative_code(self, code: str) -> tuple[bool, str]:
        """Validate creative code for forbidden elements, being more lenient with fixable issues"""
        if not code.strip():
            return False, "Empty code"
        
        # Extract just the user's code portion
        user_code = self._extract_between_markers(
            code,
            "// YOUR CREATIVE CODE GOES HERE",
            "// END OF YOUR CREATIVE CODE"
        )
        
        # Only check for critical system-level functions that would break the sketch
        critical_forbidden = {
            'setup(': 'Contains setup()',
            'draw(': 'Contains draw()',
            'background(': 'Contains background()',
            'size(': 'Contains size()',
            'frameRate(': 'Contains frameRate()',
        }
        
        # Check for critical forbidden elements
        for term, error in critical_forbidden.items():
            if term in user_code:
                return False, error
        
        # Check for absolute translations that would re-center the origin
        for line in user_code.split('\n'):
            line = line.strip()
            if any(x in line for x in [
                'translate(width/2', 'translate( width/2', 'translate(width / 2',
                'translate(height/2', 'translate( height/2', 'translate(height / 2'
            ]):
                return False, "Contains origin re-centering - coordinates are already centered"
        
        return True, None

    def validate_core_requirements(self, code: str) -> tuple[bool, str]:
        """Validate only essential Processing code requirements, being more lenient"""
        # Only validate the critical template structure
        required_structure = [
            (r'void setup\(\)\s*{[^}]*size\(800,\s*800\)[^}]*}', "setup() function modified"),
            (r'void draw\(\)\s*{.*background\(0\).*translate\(width/2,\s*height/2\)', "draw() function header modified"),
            (r'String\s+renderPath\s*=\s*"renders/render_v\d+"', "renderPath declaration missing/modified"),
            (r'saveFrame\(renderPath\s*\+\s*"/frame-####\.png"\)', "saveFrame call missing/modified")
        ]
        
        for pattern, error in required_structure:
            if not re.search(pattern, code, re.DOTALL):
                return False, error
        
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
        
        # Only check for critical JavaScript syntax that can't be auto-fixed
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
            self.log.error(f"Critical JavaScript syntax found:\n• {error_msg}")
            return False
        
        return True 