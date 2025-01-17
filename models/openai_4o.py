from typing import Optional, List, Dict, Tuple
import re
from openai import OpenAI
from logger import ArtLogger
from config import Config
import random

class OpenAI4OGenerator:
    def __init__(self, config: Config, logger: ArtLogger = None):
        self.config = config
        self.log = logger or ArtLogger()
        self.client = OpenAI(api_key=config.openai_key)
        
        # Track current model
        self.current_model = None
    
    def generate_with_ai(self, prompt: str, temperature: float = 0.85) -> Optional[str]:
        """Generate code using OpenAI API with better error handling"""
        try:
            structured_prompt = self._build_generation_prompt(prompt)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a creative coder crafting generative art with Processing.
Your task is to write ONLY the creative code that will be inserted into a template.
DO NOT write setup() or draw() functions - these are handled by the template.
DO NOT use translate(), background(), size(), or frameRate() - these are handled by the template.

The template provides:
- Canvas setup (1080x1080)
- Origin translation to center
- Background clearing
- Frame rate control
- Progress variable (0.0 to 1.0)

Focus on writing the actual creative code that will be inserted into the draw() function.
Return ONLY the code that creates the visual elements."""
                    },
                    {"role": "user", "content": structured_prompt}
                ],
                temperature=temperature,
                max_tokens=3500,
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
            
            # Validate creative code first
            is_valid, error_msg = self.validate_creative_code(code)
            if not is_valid:
                self.log.debug(f"\n=== VALIDATION ERROR ===\nCreative validation failed: {error_msg}\n==================\n")
                raise ValueError(f"Creative validation: {error_msg}")
            
            # Final safety check
            if not self._is_safe_code(code):
                self.log.debug("\n=== VALIDATION ERROR ===\nFailed final safety check\n==================\n")
                return None
                
            return code
            
        except Exception as e:
            self.log.error(f"AI generation error: {e}")
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
Create a visually appealing animation that loops smoothly over 6 seconds.
Let your creativity guide the direction - feel free to explore and experiment.

=== SYSTEM FRAMEWORK (Already Handled) ===
The following is automatically handled by the system - DO NOT include these in your code:
• Canvas setup: size(1080, 1080)
• Frame rate: 60 FPS
• Animation duration: 6 seconds (360 frames)
• Origin translation: translate(width/2, height/2)
• Background clearing: background(0)
• Progress variable: float progress = frameCount/totalFrames (0.0 to 1.0)
• Frame saving and exit handling

=== YOUR CODE REQUIREMENTS ===
Your code will be inserted into a template that handles the framework above.
In your code snippet:
• Use the provided 'progress' variable (0.0 to 1.0) for animations
• Initialize all variables when declaring them
• Use RGB values for colors (e.g., stroke(255, 0, 0) for red)
• Use ASCII characters only

=== WHAT NOT TO INCLUDE ===
These are handled by the system - do not declare or use them in your snippet:
• void setup() or draw()
• size(), frameRate()
• background()
• translate() - coordinates are already centered
• The 'progress' variable (already provided)

=== CREATIVE DIRECTION ===
• Consider exploring these techniques: {techniques}
{f"• Try something different than: {', '.join(avoid_patterns)}" if avoid_patterns else ""}

=== TECHNIQUES & APPROACHES ===
Form & Structure:
• {', '.join(geometry_techniques)}
• Explore shape relationships and transformations

Movement & Flow:
• {', '.join(motion_techniques)}
• Discover unexpected animation patterns

Pattern & Texture:
• {', '.join(pattern_techniques)}
• Build evolving pattern systems

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
        count = min(count, len(techniques))
        return random.sample(techniques, count)

    def _extract_code_from_response(self, content: str) -> Optional[str]:
        """Extract and clean code from AI response with proper structure"""
        try:
            # Clean special characters and ensure ASCII compatibility first
            content = content.encode('ascii', 'ignore').decode()
            content = re.sub(r'[^\x00-\x7F]+', '', content)
            
            # Remove markdown code block markers
            content = re.sub(r'```\w*\s*', '', content)
            content = re.sub(r'```\s*$', '', content)
            
            # Extract code between markers
            code = self._extract_between_markers(
                content,
                "// YOUR CREATIVE CODE GOES HERE",
                "// END OF YOUR CREATIVE CODE"
            )
            
            # Look for function definitions and class definitions
            global_code = []
            draw_code = []
            
            lines = code.split('\n')
            in_function = False
            function_buffer = []
            
            for line in lines:
                stripped = line.strip()
                # Skip empty lines and comment markers
                if not stripped or stripped in ["// YOUR CREATIVE CODE GOES HERE", "// END OF YOUR CREATIVE CODE"]:
                    continue
                    
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
            
            # Combine code with proper structure
            final_code = []
            
            # Add classes and global variables first
            if global_code:
                final_code.extend(global_code)
                final_code.append('')  # Empty line for spacing
            
            # Add draw code inside runSketch
            if draw_code:
                if not any('void runSketch(float progress)' in line for line in global_code):
                    final_code.append('void runSketch(float progress) {')
                    final_code.extend('  ' + line for line in draw_code)
                    final_code.append('}')
            
            # Add initSketch if not present
            if not any('void initSketch()' in line for line in global_code):
                final_code.extend([
                    '',
                    'void initSketch() {',
                    '  // Initialize sketch',
                    '}'
                ])
            
            return '\n'.join(final_code)
            
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

    def _is_safe_code(self, code: str) -> bool:
        """Less strict validation of Processing syntax, focusing on critical issues"""
        errors = []
        
        # Only check for critical JavaScript syntax that can't be auto-fixed
        critical_js_patterns = [
            (r'color\(([\'"]#[0-9a-fA-F]+[\'"]\))', "Use RGB values instead of hex codes: color(255, 0, 0)"),
            (r'\b(push|pop)\s*\(\s*\)', "Use pushMatrix()/popMatrix() instead of push()/pop()"),
            (r'createVector\s*\(', "Use 'new PVector()' instead of createVector()"),
        ]
        
        for pattern, error in critical_js_patterns:
            if re.search(pattern, code):
                errors.append(error)
        
        if errors:
            error_msg = "\n• ".join(errors)
            self.log.error(f"Critical JavaScript syntax found:\n• {error_msg}")
            return False
        
        return True

    def validate_creative_code(self, code: str) -> tuple[bool, str]:
        """Validate creative code for forbidden elements"""
        if not code.strip():
            return False, "Empty code"
        
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
            if term in code:
                return False, error
        
        # Check for absolute translations that would re-center the origin
        for line in code.split('\n'):
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
            (r'void setup\(\)\s*{[^}]*size\(1080,\s*1080\)[^}]*}', "setup() function modified"),
            (r'void draw\(\)\s*{.*background\(0\).*translate\(width/2,\s*height/2\)', "draw() function header modified"),
            (r'String\s+renderPath\s*=\s*"renders/render_v\d+"', "renderPath declaration missing/modified"),
            (r'saveFrame\(renderPath\s*\+\s*"/frame-####\.png"\)', "saveFrame call missing/modified")
        ]
        
        for pattern, error in required_structure:
            if not re.search(pattern, code, re.DOTALL):
                return False, error
        
        return True, None

    def _transform_js_to_processing(self, code: str) -> str:
        """Transform JavaScript syntax to Processing syntax"""
        # Replace variable declarations
        code = re.sub(r'let\s+(\w+)\s*=', r'float \1 =', code)