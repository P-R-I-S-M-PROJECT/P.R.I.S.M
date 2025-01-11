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
        self.client = OpenAI(api_key=config.api_key)
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
            
        # Default to o1 if not specified
        self.current_model = 'o1'
        return self.model_ids['o1']
    
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
        """Build a focused creative prompt"""
        # Get historical patterns to avoid repetition
        recent_patterns = self.config.db_manager.get_recent_patterns(limit=3)
        historical_techniques = self.config.db_manager.get_historical_techniques(limit=5)
        avoid_patterns = self._get_avoid_patterns(recent_patterns, historical_techniques)
        
        # Get random subset of techniques from each category for inspiration
        geometry_techniques = self._get_random_techniques_from_category('geometry', 3)
        motion_techniques = self._get_random_techniques_from_category('motion', 3)
        pattern_techniques = self._get_random_techniques_from_category('patterns', 3)
        
        return f"""=== PROCESSING SKETCH GENERATOR ===
Create an evolving visual artwork that explores form, motion, pattern.
Choose your approach thoughtfully - not every piece needs to use every technique.

=== SYSTEM FRAMEWORK (Already Handled) ===
The following is automatically handled by the system - DO NOT include these in your code:
• Canvas setup: size(800, 800)
• Frame rate: 60fps for 6-second loop
• Origin translation: translate(width/2, height/2)
• Background clearing: background(0)
• Progress variable: float progress = frameCount/totalFrames
• Frame saving and exit handling

=== YOUR CODE REQUIREMENTS ===
Your code will be inserted into a template that handles the framework above.
In your code snippet:
• Use the provided 'progress' variable (0.0 to 1.0) for animations
• Keep elements under ~1000 and nesting shallow (≤2 loops)
• Initialize all variables when declaring them
• Use RGB values for colors (e.g., stroke(255, 0, 0) for red)
• Use ASCII characters only (no special characters like °, ©, etc.)

=== WHAT NOT TO INCLUDE ===
These are handled by the system - do not declare or use them in your snippet:
• void setup() or draw()
• size(), frameRate()
• background()
• translate() - coordinates are already centered
• The 'progress' variable (already provided)

=== CREATIVE DIRECTION ===
• Pick a clear creative direction for this piece
• Focus on executing a few techniques well rather than combining everything
• Consider exploring these techniques: {techniques}
• Consider the impact you want to achieve (examples):
  - A bold, minimal statement
  - A complex, detailed pattern
  - A clean, geometric composition
  - A flowing, organic system
  - Or your own unique approach
• Let your chosen direction guide your technical choices
{f"• Try something different than: {', '.join(avoid_patterns)}" if avoid_patterns else ""}

=== CANVAS TREATMENT ===
Feel free to fill the entire canvas with your artwork. While the background starts black, you can:
• Create full-canvas patterns and textures
• Fill large areas with colors, gradients, or patterns
• Use both positive and negative space intentionally
• Layer elements to create rich, filled compositions
• Build dense pattern systems that cover the canvas
• Treat the background as an active part of the composition

=== SHAPE & FORM ===
Explore the full spectrum of visual expression:

Bold & Simple:
• Create strong, memorable silhouettes
• Use minimal shapes for maximum impact
• Work with bold geometric primitives
• Embrace clean, iconic forms
• Play with negative space deliberately
• Make powerful single-element statements

Complex & Detailed:
• Build intricate geometric patterns
• Create nested design systems
• Use mathematical curves for smooth forms
• Generate symmetrical compositions
• Develop detailed iconographic elements
• Layer shapes for depth and complexity

Remember: Sometimes the most impactful designs come from finding the perfect balance between simplicity and complexity.

=== TECHNIQUES & APPROACHES ===
Consider these starting points or just examples for your creative exploration.
Choose techniques that support your main creative direction - or you don't need to use them all:

Form & Structure:
• {', '.join(geometry_techniques)}
• Explore shape relationships and transformations
• Play with scale, repetition, and variation

Movement & Flow:
• {', '.join(motion_techniques)}
• Discover unexpected animation patterns
• Create dynamic relationships between elements

Pattern & Texture:
• {', '.join(pattern_techniques)}
• Build evolving pattern systems
• Create layered visual textures
Let your creativity guide you—these are just starting points for your exploration.*
=== IMPORTANT: CODE FORMAT ===
Return ONLY your creative code between these markers:
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

    def _extract_code_from_response(self, content: str) -> Optional[str]:
        """Extract and clean code from AI response, separating global and draw code"""
        try:
            # Clean special characters and ensure ASCII compatibility first
            content = content.encode('ascii', 'ignore').decode()
            content = re.sub(r'[^\x00-\x7F]+', '', content)
            
            # Remove ALL backticks and language markers
            content = re.sub(r'```\w*\n?', '', content)
            content = content.replace('```', '')
            
            # Extract code between markers
            code = content
            
            # Look for function definitions and class definitions
            global_code = []
            draw_code = []
            
            lines = code.split('\n')
            in_function = False
            function_buffer = []
            
            for line in lines:
                stripped = line.strip()
                # Check for function or class definition start
                if re.match(r'\s*(void|class)\s+\w+.*{?\s*$', stripped):
                    in_function = True
                    function_buffer = [line]
                    continue
                
                if in_function:
                    function_buffer.append(line)
                    if '}' in line and line.strip() == '}':
                        in_function = False
                        global_code.extend(function_buffer)
                        function_buffer = []
                else:
                    if stripped and not stripped.startswith('//'):
                        draw_code.append(line)
            
            # Format the final code blocks
            global_block = '\n'.join(global_code)
            draw_block = '\n'.join(draw_code)
            
            return f"""// YOUR GLOBAL CODE GOES HERE
{global_block}
// END OF GLOBAL CODE

// YOUR DRAW CODE GOES HERE
{draw_block}
// END OF DRAW CODE"""
            
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
        """Validate creative code for forbidden elements"""
        if not code.strip():
            return False, "Empty code"
        
        # Extract just the user's code portion
        user_code = self._extract_between_markers(
            code,
            "// YOUR CREATIVE CODE GOES HERE",
            "// END OF YOUR CREATIVE CODE"
        )
        
        # Only forbid system-level functions and declarations
        forbidden = {
            'setup(': 'Contains setup()',
            'draw(': 'Contains draw()',
            'background(': 'Contains background()',
            'size(': 'Contains size()',
            'frameRate(': 'Contains frameRate()',
            'final ': 'Contains final declaration'
        }
        
        # Only check for absolute translations that would re-center the origin
        for line in user_code.split('\n'):
            line = line.strip()
            if 'translate(width/2' in line or 'translate( width/2' in line or 'translate(width / 2' in line:
                return False, "Contains origin re-centering - coordinates are already centered"
            if 'translate(height/2' in line or 'translate( height/2' in line or 'translate(height / 2' in line:
                return False, "Contains origin re-centering - coordinates are already centered"
        
        for term, error in forbidden.items():
            if term in user_code:
                return False, error
        
        return True, None

    def validate_core_requirements(self, code: str) -> tuple[bool, str]:
        """Validate only essential Processing code requirements"""
        # Only validate the template structure, not the user code portion
        required_structure = [
            (r'void setup\(\)\s*{[^}]*size\(800,\s*800\)[^}]*}', "setup() function modified"),
            (r'// YOUR GLOBAL CODE GOES HERE.*// END OF GLOBAL CODE', "Global code markers missing"),
            (r'void draw\(\)\s*{.*background\(0\).*translate\(width/2,\s*height/2\)', "draw() function header modified"),
            (r'// YOUR DRAW CODE GOES HERE.*// END OF DRAW CODE', "Draw code markers missing"),
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
        """Strict validation of Processing syntax"""
        errors = []
        
        # Extract just the user's code portion
        user_code = self._extract_between_markers(
            code,
            "// YOUR CREATIVE CODE GOES HERE",
            "// END OF YOUR CREATIVE CODE"
        )
        
        # Check for JavaScript syntax only in user's code portion
        js_patterns = [
            (r'\b(const|let|var)\s+\w+\s*=', "Use 'float' or 'int' instead of JavaScript keywords (const/let/var)"),
            (r'for\s*\(\s*(let|const)\s+\w+', "Use 'int' or 'float' in for loops, not JavaScript keywords"),
            (r'color\(([\'"]#[0-9a-fA-F]+[\'"]\))', "Use RGB values instead of hex codes: color(255, 0, 0)"),
            (r'\b(push|pop)\s*\(\s*\)', "Use pushMatrix()/popMatrix() instead of push()/pop()"),
            (r'createVector\s*\(', "Use 'new PVector()' instead of createVector()"),
            (r'function\s+\w+\s*\(', "Functions must be declared outside creative code block"),
            (r'\bstatic\s+\w+', "Do not use static variables inside draw() - declare them at global scope"),
            (r'(float|int)\s+\w+(?:\s*,\s*\w+)*\s*;', "All variables must be initialized when declared"),
            (r'void\s+\w+\s*\([^\)]*\)\s*{', "Functions must be declared at global scope, not inside draw()")
        ]
        
        for pattern, error in js_patterns:
            if re.search(pattern, user_code):
                errors.append(error)
        
        if errors:
            # Return detailed error for retry prompt
            error_msg = "\n• ".join(errors)
            self.log.error(f"JavaScript syntax found:\n• {error_msg}")
            return False  # Return False instead of raising error to trigger retry
        
        return True 