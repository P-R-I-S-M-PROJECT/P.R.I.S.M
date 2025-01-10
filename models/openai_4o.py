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
        self.client = OpenAI(api_key=config.api_key)
    
    def generate_with_ai(self, prompt: str, temperature: float = 0.85) -> Optional[str]:
        """Generate code using OpenAI API with better error handling"""
        try:
            structured_prompt = self._build_generation_prompt(prompt)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a Processing (Java-based) code generator.
                        CRITICAL: You must use Processing syntax (based on Java), NOT JavaScript/p5.js.
                        
                        CORRECT SYNTAX:
                        ```processing
                        int totalShapes = 50;
                        float maxRadius = 300;
                        float speed = 2 * PI;
                        
                        for (int i = 0; i < totalShapes; i++) {
                            float angle = TWO_PI * i / totalShapes + progress * speed;
                            float radius = maxRadius * (1 + sin(progress * TWO_PI));
                            float x = radius * cos(angle);
                            float y = radius * sin(angle);
                            
                            stroke(255, 100, 100);
                            ellipse(x, y, 10, 10);
                        }
                        ```
                        
                        INCORRECT (JavaScript) SYNTAX:
                        ```javascript
                        // DO NOT USE THIS STYLE:
                        const totalShapes = 50;  // NO const
                        let radius = 300;        // NO let
                        for (let i = 0;...)      // NO let in loops
                        ```
                        
                        Return ONLY Processing-compatible code between the markers."""
                    },
                    {"role": "user", "content": structured_prompt}
                ],
                temperature=temperature,
                max_tokens=3500,
            )
            
            if not response.choices:
                self.log.error("No response generated from AI")
                return None
            
            code = self._extract_code_from_response(response.choices[0].message.content)
            return code if self._is_safe_code(code) else None
            
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
Create an evolving visual artwork that explores form, motion, and pattern.
Choose your approach thoughtfully - not every piece needs to use every technique.

=== CRITICAL SYNTAX RULES ===
• REQUIRED: Use Processing (Java) syntax, NOT JavaScript
• Variables MUST be declared as:
    float radius = 200;
    int count = 10;
    float[] angles;  // Arrays
• NO JavaScript keywords (const, let, var)
• NO JavaScript functions (push, pop, createVector)
• Color must use RGB values:
    stroke(255, 0, 0);  // Red
    fill(0, 255, 0);    // Green
• Example of correct code:
    float numShapes = 100;
    float maxRadius = 400;
    float angleOffset = TWO_PI * progress;
    
    for (int i = 0; i < numShapes; i++) {{
        float angle = map(i, 0, numShapes, 0, TWO_PI) + angleOffset;
        float radius = maxRadius * sin(PI * progress);
        float x = radius * cos(angle);
        float y = radius * sin(angle);
        
        stroke(255);
        ellipse(x, y, 20, 20);
    }}

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

Return ONLY the creative code between these markers:
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE

=== ESSENTIAL FRAMEWORK ===
• Seamless 6-second loop (360 frames at 60fps)
• Canvas: 800x800, origin at center (0,0)
• Use the provided 'progress' variable (0.0 to 1.0) for all animations
• Background and transforms handled outside
• Keep elements under ~1000 and nesting shallow (≤2 loops)
• DO NOT declare: progress, setup(), draw(), background(), translate(), size(), frameRate()

=== DRAWING REQUIREMENTS ===
• Use stroke() or fill() to set colors (white stroke by default)
• Draw shapes using rect(), ellipse(), line(), beginShape(), etc.
• Ensure shapes have non-zero size
• Create visible elements against black background

=== TECHNIQUES & APPROACHES ===
Consider these starting points or just examples for your creative exploration.
Choose techniques that support your main creative direction:

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

Remember: The canvas is black by default - you must draw visible shapes!
Use stroke() or fill() with color values, and ensure your shapes have size."""

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
        """Extract and clean code from AI response"""
        if "// YOUR CREATIVE CODE GOES HERE" not in content:
            return content.strip()
        
        try:
            code_parts = content.split("// YOUR CREATIVE CODE GOES HERE")[1]
            code_parts = code_parts.split("// END OF YOUR CREATIVE CODE")[0]
            return code_parts.strip()
        except IndexError:
            return None

    def _is_safe_code(self, code: str) -> bool:
        """Strict validation of Processing syntax"""
        errors = []
        
        # Check for JavaScript syntax
        js_patterns = [
            (r'\b(const|let|var)\s+\w+\s*=', "Use 'float' or 'int' instead of JavaScript keywords (const/let/var)"),
            (r'for\s*\(\s*(let|const)\s+\w+', "Use 'int' or 'float' in for loops, not JavaScript keywords"),
            (r'color\(([\'"]#[0-9a-fA-F]+[\'"]\))', "Use RGB values instead of hex codes: color(255, 0, 0)"),
            (r'\b(push|pop)\s*\(\s*\)', "Use pushMatrix()/popMatrix() instead of push()/pop()"),
            (r'createVector\s*\(', "Use 'new PVector()' instead of createVector()"),
            (r'function\s+\w+\s*\(', "Functions must be declared outside creative code block")
        ]
        
        for pattern, error in js_patterns:
            if re.search(pattern, code):
                errors.append(error)
        
        if errors:
            # Return detailed error for retry prompt
            error_msg = "\n• ".join(errors)
            self.log.error(f"JavaScript syntax found:\n• {error_msg}")
            return False  # Return False instead of raising error to trigger retry
        
        return True

    def validate_creative_code(self, code: str) -> tuple[bool, str]:
        """Validate creative code for forbidden elements"""
        if not code.strip():
            return False, "Empty code"
        
        forbidden = {
            'void': 'Contains function definition',
            'setup(': 'Contains setup()',
            'draw(': 'Contains draw()',
            'background(': 'Contains background()',
            'translate(': 'Contains translate()',
            'size(': 'Contains size()',
            'frameRate(': 'Contains frameRate()',
            'final ': 'Contains final declaration'
        }
        
        for term, error in forbidden.items():
            if term in code:
                return False, error
        
        return True, None

    def validate_core_requirements(self, code: str) -> tuple[bool, str]:
        """Validate only essential Processing code requirements"""
        required_structure = [
            (r'void setup\(\)\s*{[^}]*size\(800,\s*800\)[^}]*}', "setup() function modified"),
            (r'void draw\(\)\s*{.*background\(0\).*translate\(width/2,\s*height/2\)', "draw() function header modified"),
            (r'String\s+renderPath\s*=\s*"renders/render_v\d+"', "renderPath declaration missing/modified"),
            (r'saveFrame\(renderPath\s*\+\s*"/frame-####\.png"\)', "saveFrame call missing/modified"),
            (r'// YOUR CREATIVE CODE GOES HERE.*// END OF YOUR CREATIVE CODE', "Creative code markers missing")
        ]
        
        for pattern, error in required_structure:
            if not re.search(pattern, code, re.DOTALL):
                return False, error
            
        return True, None 

    def _transform_js_to_processing(self, code: str) -> str:
        """Transform JavaScript syntax to Processing syntax"""
        # Replace variable declarations
        code = re.sub(r'let\s+(\w+)\s*=', r'float \1 =', code)