from typing import Optional, List, Dict, Tuple
import re
from logger import ArtLogger
from .text_generator import TextGenerator

class CodeValidator:
    # Processing template for sketch framework
    PROCESSING_TEMPLATE = """// === USER'S CREATIVE CODE ===
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
}}"""

    # Processing requirements and guidelines
    PROCESSING_REQUIREMENTS = """=== PROCESSING SKETCH REQUIREMENTS ===
1. Required Functions
   • void initSketch() - Called once at start
   • void runSketch(float progress) - Called each frame with progress (0.0 to 1.0)

2. System Framework (DO NOT INCLUDE)
   • void setup() or draw() functions
   • size(1080, 1080) and frameRate settings
   • background(0) or any background clearing
   • translate(width/2, height/2) for centering
   • Frame saving and program exit

3. Code Structure
   • Define classes at the top
   • Declare global variables
   • Define initSketch() for setup
   • Define runSketch(progress) for animation
   • Canvas is centered at (0,0)
   • Initialize all variables with values
   • Use RGB values for colors

4. Animation Guidelines
   • Use progress (0.0 to 1.0) for ALL animations
   • Ensure smooth looping by matching start/end states
   • Use map() to convert progress to specific ranges
   • Use lerp() or lerpColor() for smooth transitions
   • Avoid sudden jumps or discontinuities
   • Consider easing functions for natural motion
   • Test values at progress = 0.0, 0.5, and 1.0"""

    # Critical validation patterns
    CRITICAL_VALIDATION_PATTERNS = {
        r'\bsize\s*\(': 'Contains size() call - this is handled by the system',
        r'\bframeRate\s*\(': 'Contains frameRate() call - this is handled by the system',
        r'\bsaveFrame\s*\(': 'Contains saveFrame() call - this is handled by the system',
        r'\bexit\s*\(': 'Contains exit() call - this is handled by the system',
        r'\btranslate\s*\(\s*width\s*/\s*2': 'Contains origin re-centering - coordinates are already centered',
        r'\btranslate\s*\(\s*height\s*/\s*2': 'Contains origin re-centering - coordinates are already centered'
    }

    # Required function patterns
    REQUIRED_FUNCTIONS = {
        'initSketch': r'\bvoid\s+initSketch\s*\(\s*\)',
        'runSketch': r'\bvoid\s+runSketch\s*\(\s*float\s+\w+\s*\)'
    }

    # Required system components
    REQUIRED_SYSTEM_COMPONENTS = [
        ('void setup()', 'Missing setup() function'),
        ('size(1080, 1080)', 'Missing size(1080, 1080) call'),
        ('frameRate(60)', 'Missing frameRate(60) call'),
        ('void draw()', 'Missing draw() function'),
        ('background(0)', 'Missing background(0) call'),
        ('float progress', 'Missing progress variable'),
        ('saveFrame(', 'Missing saveFrame() call')
    ]

    # Common error patterns and guidance
    ERROR_PATTERNS = {
        r"Cannot find symbol.*letterMask\.letterMask": "Double letterMask reference - use just letterMask instead",
        r"cannot find symbol.*class PGraphics": "Missing PGraphics import or declaration",
        r"cannot find symbol.*ArrayList": "Missing ArrayList import or declaration",
        r"NullPointerException": "Null object reference - check initialization",
        r"ArrayIndexOutOfBounds": "Array index out of bounds",
        r"error: incompatible types:": "Type mismatch in variable assignment",
        r"error: cannot find symbol": "Undefined variable or method",
        r"error: ';' expected": "Missing semicolon",
        r"the method (.*) is undefined": "Undefined method call",
        r"error: reached end of file while parsing": "Missing closing brace or parenthesis",
        r"Contains translate\(\)": """• DO NOT use translate() - all positioning should be relative to canvas center (0,0)
• Use direct x,y coordinates: x = width/2 + offset
• For rotations, use rotate() with pushMatrix/popMatrix
• Remember the canvas is already centered""",
        r"Creative validation": """• Remove any setup/draw function declarations
• Ensure no background or translate calls
• Use only the provided progress variable
• Keep code focused on the creative elements""",
        r"Core validation": """• Ensure code fits within the template structure
• Check for proper loop completion
• Verify all variables are properly scoped
• Remove any conflicting declarations"""
    }

    # Auto-fix templates
    AUTO_FIX_TEMPLATES = {
        'initSketch': """void initSketch() {
    // Initialize variables and setup
}""",
        'runSketch': """void runSketch(float progress) {
    // Animation code using progress (0.0 to 1.0)
}""",
        'letterMask': """// Initialize letterMask
letterMask = createGraphics(1080, 1080);
letterMask.beginDraw();
letterMask.background(0);
letterMask.fill(255);
letterMask.textAlign(CENTER, CENTER);
letterMask.textSize(200);
letterMask.text("{text}", letterMask.width/2, letterMask.height/2);
letterMask.endDraw();"""
    }

    # Simplified text art requirements
    TEXT_ART_REQUIREMENTS = """=== TEXT ART REQUIREMENTS ===
• MUST define letterMask in initSketch()
• MUST use letterMask for text(...) calls
• MUST initialize letterMask with proper size and settings
• MUST call letterMask.beginDraw() and endDraw()"""

    # Looser letterMask validation patterns
    TEXT_VALIDATION_PATTERNS = [
        (r'PGraphics\s+letterMask', r'letterMask\s*=\s*createGraphics'),  # Declaration and creation
        (r'letterMask\s*\.\s*beginDraw\s*\(\s*\)', r'beginDraw'),  # Begin draw (more flexible)
        (r'letterMask\s*\.\s*text\s*\(', r'\.text\s*\('),  # Text call (more flexible)
        (r'letterMask\s*\.\s*endDraw\s*\(\s*\)', r'endDraw')  # End draw (more flexible)
    ]

    # Base code stubs for auto-injection
    BASE_STUBS = {
        'initSketch': """void initSketch() {
    // Initialize variables and setup
}""",
        'runSketch': """void runSketch(float progress) {
    // Animation code using progress (0.0 to 1.0)
}""",
        'textMask': """PGraphics letterMask;

void initSketch() {
    // Initialize letterMask
    letterMask = createGraphics(1080, 1080);
    letterMask.beginDraw();
    letterMask.background(0);
    letterMask.fill(255);
    letterMask.textAlign(CENTER, CENTER);
    letterMask.textSize(200);
    letterMask.text("{text}", letterMask.width/2, letterMask.height/2);
    letterMask.endDraw();
}"""
    }

    # Minimal text validation patterns (more flexible)
    MINIMAL_TEXT_PATTERNS = [
        r'letterMask\s*=\s*createGraphics',  # Basic initialization
        r'\.beginDraw\s*\(\s*\)',  # Begin draw
        r'\.text\s*\(',  # Any text call
        r'\.endDraw\s*\(\s*\)'  # End draw
    ]

    # Base stubs for pre-emptive injection
    MINIMAL_STUBS = """// Required function stubs - fill with your code
void initSketch() {
    // Initialize variables and setup here
}

void runSketch(float progress) {
    // Animation code using progress (0.0 to 1.0) here
}
"""

    # Text art stubs for pre-emptive injection
    TEXT_STUBS = """// Required text art stubs - fill with your code
PGraphics letterMask;

void initSketch() {
    // Initialize letterMask
    letterMask = createGraphics(1080, 1080);
    letterMask.beginDraw();
    letterMask.background(0);
    letterMask.fill(255);
    letterMask.textAlign(CENTER, CENTER);
    letterMask.textSize(200);
    letterMask.text("{text}", letterMask.width/2, letterMask.height/2);
    letterMask.endDraw();
    
    // Add your additional initialization here
}

void runSketch(float progress) {
    // Animation code using progress (0.0 to 1.0) here
    // Use letterMask for text rendering
}
"""

    def __init__(self, logger: ArtLogger = None, text_generator: TextGenerator = None):
        self.log = logger or ArtLogger()
        self.text_generator = text_generator

    def validate_creative_code(self, code: str, is_snippet: bool = False, is_text_art: bool = False) -> tuple[bool, str]:
        """Validate creative code with minimal interference"""
        if not code.strip():
            return False, "Empty code"
        
        # Check for critical forbidden patterns
        for pattern, error in self.CRITICAL_VALIDATION_PATTERNS.items():
            if re.search(pattern, code):
                return False, error

        # Only validate text requirements if this is text art
        if is_text_art:
            missing_patterns = []
            for pattern in self.MINIMAL_TEXT_PATTERNS:
                if not re.search(pattern, code):
                    missing_patterns.append(pattern)
            
            if missing_patterns:
                # Try auto-injection first
                fixed_code = self.inject_base_code(code, is_text_art=True)
                if fixed_code != code:
                    return self.validate_creative_code(fixed_code, is_snippet, is_text_art)
                return False, "Missing required text patterns"

        # For non-snippets, ensure required functions exist
        if not is_snippet:
            # Try auto-injection first
            fixed_code = self.inject_base_code(code, is_text_art)
            if fixed_code != code:
                return self.validate_creative_code(fixed_code, is_snippet, is_text_art)
            
            # If still missing after injection, return error
            for func_name, pattern in self.REQUIRED_FUNCTIONS.items():
                if not re.search(pattern, code):
                    return False, f"Missing {func_name}() function"

        return True, None

    def clean_code(self, code: str, is_variation: bool = False) -> str:
        """Clean and prepare user code, with minimal interference to valid Processing code"""
        try:
            # Remove markdown artifacts
            code = re.sub(r'^```.*?\n', '', code)
            code = re.sub(r'\n```.*?$', '', code)
            code = code.strip()
            
            # Clean special characters and ensure ASCII compatibility
            code = code.encode('ascii', 'ignore').decode()  # Remove non-ASCII chars
            code = re.sub(r'[^\x00-\x7F]+', '', code)  # Additional non-ASCII cleanup
            
            # Fix common letterMask issues
            code = re.sub(r'letterMask\.letterMask', 'letterMask', code)  # Fix double reference
            code = re.sub(r'letterMask\s*\.\s*letterMask', 'letterMask', code)  # Fix with spaces
            
            # Extract code between markers
            lines = code.split('\n')
            cleaned_lines = []
            in_code_block = False
            
            for line in lines:
                # Skip empty lines at start/end
                if not in_code_block and not line.strip():
                    continue
                    
                # Check for code block markers
                if "YOUR CREATIVE CODE GOES HERE" in line:
                    in_code_block = True
                    continue
                elif "END OF YOUR CREATIVE CODE" in line:
                    break
                
                if in_code_block:
                    cleaned_lines.append(line)
            
            code = "\n".join(cleaned_lines)
            
            # Clean up multiple blank lines
            code = re.sub(r'\n\s*\n\s*\n', '\n\n', code)
            return code.strip()
            
        except Exception as e:
            self.log.error(f"Error cleaning code: {str(e)}")
            return code

    def extract_code_from_response(self, response: str, is_variation: bool = False) -> Optional[str]:
        """Extract code from AI response and clean it"""
        try:
            # Find code between markers
            start_marker = "YOUR CREATIVE CODE GOES HERE"
            end_marker = "END OF YOUR CREATIVE CODE"
            
            start_idx = response.find(start_marker)
            end_idx = response.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                return None
                
            # Extract and clean the code
            raw_code = response[start_idx:end_idx + len(end_marker)]
            return self.clean_code(raw_code, is_variation)
            
        except Exception as e:
            self.log.error(f"Error extracting code: {str(e)}")
            return None

    def build_processing_template(self, code: str, version: int) -> str:
        """Build the complete Processing template with the given code"""
        return self.PROCESSING_TEMPLATE.format(code=code, version=version)

    def get_processing_requirements(self) -> str:
        """Get the standard Processing requirements"""
        return self.PROCESSING_REQUIREMENTS

    def build_error_guidance(self, error_msg: str = None) -> str:
        """Build error guidance for Processing code"""
        guidance = [
            "=== PROCESSING ERROR GUIDANCE ===",
            "• Check for missing semicolons",
            "• Verify all variables are declared and initialized",
            "• Ensure proper function declarations",
            "• Check bracket matching and closure",
            "• Verify color values are in valid ranges",
            "• Ensure all used variables are properly scoped"
        ]
        
        if error_msg:
            # Check for specific error patterns first
            for pattern, specific_guidance in self.ERROR_PATTERNS.items():
                if re.search(pattern, error_msg, re.IGNORECASE):
                    guidance.extend(["", "=== SPECIFIC GUIDANCE ==="])
                    guidance.extend(specific_guidance.split('\n'))
                    break
            
            # Add general error type guidance
            if "cannot find anything named" in error_msg.lower():
                guidance.extend([
                    "",
                    "=== UNDEFINED VARIABLE GUIDANCE ===",
                    "• Declare all variables before use",
                    "• Check for typos in variable names",
                    "• Verify variable scope"
                ])
            elif "expecting" in error_msg.lower():
                guidance.extend([
                    "",
                    "=== SYNTAX ERROR GUIDANCE ===",
                    "• Check for missing parentheses",
                    "• Verify function parameter types",
                    "• Ensure proper statement termination"
                ])
        
        return "\n".join(guidance)

    def convert_arrays_to_arraylists(self, code: str) -> str:
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

    def fix_sort_implementation(self, sort_code: str) -> str:
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

    def convert_to_processing(self, code: str) -> str:
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

    def is_safe_code(self, code: str) -> bool:
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

    def validate_processing_code(self, code: str, check_system: bool = True) -> tuple[bool, str]:
        """Comprehensive Processing code validation"""
        try:
            # First validate creative code
            is_valid, error = self.validate_creative_code(code)
            if not is_valid:
                return False, error

            # Check for system components if required
            if check_system:
                for component, error in self.REQUIRED_SYSTEM_COMPONENTS:
                    if component not in code:
                        return False, error

            # Check for basic syntax issues
            if not self.is_safe_code(code):
                return False, "Code contains unsafe or invalid syntax"

            return True, None

        except Exception as e:
            self.log.error(f"Error in Processing validation: {str(e)}")
            return False, f"Validation error: {str(e)}"

    def validate_with_retry(self, code: str, attempt: int = 0, max_attempts: int = 3) -> tuple[bool, str, Optional[str]]:
        """Validate code with retry logic and error guidance"""
        try:
            # Basic validation first
            is_valid, error = self.validate_processing_code(code)
            if not is_valid:
                # Build error guidance
                guidance = self.build_error_guidance(error)
                if attempt < max_attempts:
                    return False, error, guidance
                else:
                    return False, f"Max attempts ({max_attempts}) exceeded. Last error: {error}", None

            # Additional safety checks
            if not self.is_safe_code(code):
                return False, "Code contains unsafe patterns", self.build_error_guidance("unsafe patterns detected")

            return True, None, None

        except Exception as e:
            self.log.error(f"Error in validation with retry: {str(e)}")
            return False, str(e), None

    def attempt_auto_fix(self, code: str, error_msg: str) -> tuple[bool, str, str]:
        """Attempt to automatically fix common issues without requiring LLM retry"""
        fixed_code = code
        fix_applied = ""

        # Missing initSketch function
        if "Missing initSketch() function" in error_msg:
            if "void initSketch()" not in code:
                fixed_code = self.AUTO_FIX_TEMPLATES['initSketch'] + "\n\n" + code
                fix_applied = "Added initSketch() stub"

        # Missing runSketch function
        elif "Missing runSketch(float progress) function" in error_msg:
            if "void runSketch" not in code:
                fixed_code = code + "\n\n" + self.AUTO_FIX_TEMPLATES['runSketch']
                fix_applied = "Added runSketch() stub"

        # Missing letterMask initialization
        elif any(phrase in error_msg for phrase in ["Missing text initialization", "Missing required text patterns"]):
            if "letterMask = createGraphics" not in code and "void initSketch" in code:
                # Extract text content if possible
                text = "PRISM"  # Default
                text_match = re.search(r'letterMask\.text\s*\(\s*"([^"]+)"', code)
                if text_match:
                    text = text_match.group(1)
                
                # Insert letterMask template into initSketch
                letter_mask_init = self.AUTO_FIX_TEMPLATES['letterMask'].format(text=text)
                
                # More flexible insertion into initSketch
                if re.search(r'void\s+initSketch\s*\(\s*\)\s*\{', code):
                    fixed_code = re.sub(
                        r'(void\s+initSketch\s*\(\s*\)\s*\{[^\}]*)(})',
                        fr'\1\n    {letter_mask_init}\n\2',
                        code
                    )
                else:
                    # If no initSketch, create it with letterMask
                    fixed_code = f"""void initSketch() {{
    {letter_mask_init}
}}

{code}"""
                fix_applied = "Added letterMask initialization"

        # Return whether a fix was applied and the potentially fixed code
        return bool(fix_applied), fixed_code, fix_applied

    def build_retry_prompt(self, code: str, error_msg: str, attempt: int) -> str:
        """Build a focused retry prompt based on the specific error"""
        if any(phrase in error_msg for phrase in ["Missing text initialization", "Missing required text patterns"]):
            return f"""The code needs letterMask for text art. Add these EXACT lines in initSketch():

letterMask = createGraphics(1080, 1080);
letterMask.beginDraw();
letterMask.background(0);
letterMask.fill(255);
letterMask.textAlign(CENTER, CENTER);
letterMask.textSize(200);
letterMask.text("PRISM", letterMask.width/2, letterMask.height/2);
letterMask.endDraw();

Previous code:
{code}

Return ONLY the corrected code between markers."""

        elif "Missing initSketch() function" in error_msg:
            return f"""Add initSketch() to initialize your variables:

void initSketch() {{
    // Initialize variables and setup
}}

Previous code:
{code}

Return ONLY the corrected code between markers."""

        # Default retry prompt with minimal guidance
        return f"""Fix this specific error and return the corrected code:
Error: {error_msg}

Previous code:
{code}

Return ONLY the corrected code between markers."""

    def inject_base_code(self, code: str, is_text_art: bool = False, text: str = "PRISM") -> str:
        """Inject necessary base code stubs"""
        result = code

        # Add initSketch if missing
        if "void initSketch" not in result:
            if is_text_art:
                # Use text-specific template with proper escaping
                safe_template = self.BASE_STUBS['textMask'].replace("{", "{{").replace("}", "}}")
                safe_template = safe_template.replace("{{text}}", "{text}")
                result = safe_template.format(text=text)
            else:
                result = self.BASE_STUBS['initSketch'] + "\n\n" + result

        # Add runSketch if missing
        if "void runSketch" not in result:
            result += "\n\n" + self.BASE_STUBS['runSketch']

        # If text art but no letterMask in initSketch, inject it
        if is_text_art and "letterMask = createGraphics" not in result:
            # Try to inject into existing initSketch
            if re.search(r'void\s+initSketch\s*\(\s*\)\s*\{', result):
                mask_init = f"""    // Initialize letterMask
    letterMask = createGraphics(1080, 1080);
    letterMask.beginDraw();
    letterMask.background(0);
    letterMask.fill(255);
    letterMask.textAlign(CENTER, CENTER);
    letterMask.textSize(200);
    letterMask.text("{text}", letterMask.width/2, letterMask.height/2);
    letterMask.endDraw();"""
                
                result = re.sub(
                    r'(void\s+initSketch\s*\(\s*\)\s*\{[^\}]*)(})',
                    fr'\1\n{mask_init}\n\2',
                    result
                )

        return result

    def inject_minimal_stubs(self, is_text_art: bool = False, text: str = "PRISM") -> str:
        """Get minimal stubs that should be present before LLM generation"""
        if is_text_art:
            # Escape curly braces in the template before formatting
            safe_template = self.TEXT_STUBS.replace("{", "{{").replace("}", "}}")
            # Add back the format placeholder
            safe_template = safe_template.replace("{{text}}", "{text}")
            return safe_template.format(text=text)
        return self.MINIMAL_STUBS 