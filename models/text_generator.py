from typing import Optional, List, Dict, Tuple
import re
from logger import ArtLogger

class TextGenerator:
    # Core text mask template - foundation for all text effects
    TEXT_MASK_TEMPLATE = """PGraphics letterMask;
letterMask = createGraphics(1080, 1080);
letterMask.beginDraw();
letterMask.background(0);
letterMask.fill(255);
letterMask.textAlign(CENTER, CENTER);
letterMask.textFont(createFont("Arial Unicode MS", 200));  // Support for non-English characters
letterMask.textSize(200);  // Adjust size as needed
letterMask.text("{text}", letterMask.width/2, letterMask.height/2);
letterMask.endDraw();"""

    # Comprehensive text art guidelines and techniques
    TEXT_ART_GUIDELINES = """=== TEXT ART CREATION GUIDE ===
1. Text Visibility & Structure
   • Keep text clearly readable while being creative
   • Use masks to maintain text boundaries and shape
   • Consider layering multiple effects for depth
   • Balance between legibility and artistic expression

2. Core Techniques
   A. Mask-Based Effects
      • Use letterMask to define text boundaries
      • Sample mask pixels to check text areas
      • Create clean edges with mask boundaries
      • Layer multiple masks for complex effects

   B. Particle Systems
      • Distribute particles within/around text
      • Control particle behavior with forces
      • Use velocity and acceleration for motion
      • Consider particle life cycles and spawning

   C. Pattern Generation
      • Fill text with geometric or organic patterns
      • Use grids, lines, or shapes as elements
      • Apply noise for natural variations
      • Create flowing, dynamic pattern motion

   D. Shape Morphing
      • Transform between text states smoothly
      • Sample points for shape interpolation
      • Use vectors for precise control
      • Maintain visual continuity in transitions

3. Animation Guidelines
   • Use progress (0.0 to 1.0) for smooth timing
   • Create seamless loops with matching start/end
   • Apply easing for natural motion
   • Layer multiple animation techniques
   • Consider speed and rhythm variations

4. Advanced Effects
   • Combine multiple techniques creatively
   • Layer different effects for complexity
   • Use masks to blend between effects
   • Create interactions between elements
   • Apply transformations (scale, rotate, etc.)
   • Experiment with opacity and blending

5. Implementation Notes
   • Initialize all systems in setup
   • Use classes for complex behaviors
   • Maintain clean, efficient code
   • Consider performance with many elements
   • Handle edge cases and boundaries"""

    # Required patterns for text art validation
    TEXT_VALIDATION_PATTERNS = [
        r'PGraphics\s+letterMask\s*;',
        r'letterMask\s*=\s*createGraphics\s*\(\s*1080\s*,\s*1080\s*\)',
        r'letterMask\s*\.\s*beginDraw\s*\(\s*\)',
        r'letterMask\s*\.\s*background\s*\(\s*0\.?0?\s*\)',
        r'letterMask\s*\.\s*fill\s*\(\s*255\s*\)',
        r'letterMask\s*\.\s*textAlign\s*\(\s*CENTER\s*,\s*CENTER\s*\)',
        r'letterMask\s*\.\s*textFont\s*\(\s*createFont\s*\(\s*["\']Arial Unicode MS["\']\s*,\s*\d+\s*\)\s*\)',  # Added font validation
        r'letterMask\s*\.\s*textSize\s*\(\s*\d+',
        r'letterMask\s*\.\s*text\s*\(',
        r'letterMask\s*\.\s*endDraw\s*\(\s*\)'
    ]

    def __init__(self, logger: ArtLogger = None):
        self.log = logger or ArtLogger()

    def get_text_requirements(self, text: str, custom_guidelines: str = None) -> str:
        """Get comprehensive text art requirements with custom guidelines"""
        base_requirements = (
            f"=== TEXT ART OBJECTIVE ===\n"
            f"Create dynamic art using the text: {text}\n\n"
        )

        # Add non-English text support if requested
        if custom_guidelines and "language other then english" in custom_guidelines.lower():
            base_requirements += (
                "=== NON-ENGLISH TEXT SUPPORT ===\n"
                "• Use Arial Unicode MS font for proper character rendering\n"
                "• Consider text layout and spacing for different writing systems\n"
                "• Ensure proper character alignment and scaling\n"
                "• Test with various font sizes for readability\n\n"
            )

        base_requirements += self.TEXT_ART_GUIDELINES

        if custom_guidelines:
            base_requirements += f"\n=== CUSTOM REQUIREMENTS ===\n{custom_guidelines}"

        return base_requirements

    def get_text_mask_template(self, text: str) -> str:
        """Get the text mask template"""
        return self.TEXT_MASK_TEMPLATE.format(text=text)

    def validate_text_code(self, code: str) -> tuple[bool, str]:
        """Validate text-specific code requirements"""
        if 'text(' in code and not 'letterMask' in code:
            return False, "Text art requires letterMask for proper rendering"

        # For text art, verify mask requirements
        if 'letterMask' in code:
            missing_patterns = []
            for pattern in self.TEXT_VALIDATION_PATTERNS:
                if not re.search(pattern, code):
                    missing_patterns.append(pattern)
            if missing_patterns:
                return False, "Missing required text mask initialization patterns"

        return True, None

    def build_text_error_guidance(self) -> str:
        """Build text-specific error guidance"""
        return (
            "\n=== TEXT IMPLEMENTATION REQUIREMENTS ===\n"
            "• Use letterMask for text rendering\n"
            "• Initialize letterMask properly\n"
            "• Ensure proper text boundaries\n"
            "• Validate mask initialization\n"
            f"{self.TEXT_MASK_TEMPLATE.format(text='PRISM')}\n"
        )

    def is_text_requirement(self, guidelines: str) -> bool:
        """Check if the guidelines contain text-related requirements"""
        if not guidelines:
            return False
        return any(word in guidelines.lower() for word in ['text', 'spell', 'word', 'letter'])

    def build_text_prompt(self, text: str, custom_guidelines: str = None) -> dict:
        """Build comprehensive text art prompt"""
        return {
            "is_text_art": True,
            "text": text,
            "text_template": self.get_text_mask_template(text),
            "text_requirements": self.get_text_requirements(text, custom_guidelines),
            "custom_guidelines": custom_guidelines
        }

    def build_wizard_text_prompt(self, text: str, suggested_techniques: List[str] = None, custom_guidelines: str = None) -> dict:
        """Build a complete text prompt for the wizard interface"""
        # Build technique suggestions if provided
        technique_guidance = ""
        if suggested_techniques:
            technique_guidance = "\n=== SUGGESTED TECHNIQUES ===\n"
            technique_guidance += "Consider incorporating these effects:\n"
            technique_guidance += "\n".join(f"• {tech}" for tech in suggested_techniques)

        # Combine all guidelines
        full_guidelines = custom_guidelines or ""
        if technique_guidance:
            full_guidelines = technique_guidance + "\n\n" + full_guidelines

        return self.build_text_prompt(text, full_guidelines) 