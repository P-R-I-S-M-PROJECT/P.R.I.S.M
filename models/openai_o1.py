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
        # Define available models and their weights
        self.o1_models = {
            'o1-mini': 0.99,
            'o1': 0.01  
        }
    
    def _select_o1_model(self) -> str:
        """Randomly select between o1-mini and o1 models"""
        models = list(self.o1_models.keys())
        weights = list(self.o1_models.values())
        return random.choices(models, weights=weights, k=1)[0]
    
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
            
            # Select which O1 model to use
            selected_model = self._select_o1_model()
            self.log.info(f"Using model: {selected_model}")
            
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            if not response.choices:
                self.log.error("No response generated from AI")
                return None
            
            code = self._extract_code_from_response(response.choices[0].message.content)
            if code:
                # Convert any remaining JavaScript syntax to Processing
                code = self._convert_to_processing(code)
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

Let your creativity guide you—these are just starting points for your exploration."""

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
        """Check for forbidden elements in generated code"""
        forbidden = ['void', 'setup(', 'draw(', 'background(', 
                    'translate(', 'size(', 'framerate(']
        return not any(forbidden in code.lower() for forbidden in forbidden)

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