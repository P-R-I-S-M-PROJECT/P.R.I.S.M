from typing import Dict, List, Optional
import subprocess
from pathlib import Path
import re
from models.openai_4o import OpenAI4OGenerator
from models.data_models import Pattern, Technique
from logger import ArtLogger
from pattern_analyzer import PatternAnalyzer
from config import Config
import json
import time
import random
from models.flux import FluxGenerator
from models.validation import CodeValidator

class ProcessingGenerator:
    def __init__(self, config: Config, logger: ArtLogger = None):
        """Initialize the code generator with configuration"""
        self.config = config
        self.log = logger or ArtLogger()
        
        # Initialize model generators
        from models.openai_o1 import OpenAIO1Generator
        from models.openai_4o import OpenAI4OGenerator
        from models.claude_generator import ClaudeGenerator
        from models.flux import FluxGenerator
        
        # Create single instances
        self.o1_generator = OpenAIO1Generator(config, self.log)
        self.o4_generator = OpenAI4OGenerator(config, self.log)
        self.claude_generator = ClaudeGenerator(config, self.log)
        self.flux_generator = FluxGenerator(config, self.log)
        
        # Initialize pattern analyzer and validator
        self.analyzer = PatternAnalyzer(config, self.log)
        self.validator = CodeValidator(logger=self.log)
        
        # Initialize current state tracking
        self._current_techniques = []
        self._current_complexity = 0.7  # Default values
        self._current_innovation = 0.5  # Default values
        
        # Initialize AI generators dictionary using existing instances
        self.ai_generators = {
            'o1': self.o1_generator,
            'o1-mini': self.o1_generator,  # Same instance for both O1 variants
            '4o': self.o4_generator,
            'claude-3-opus': self.claude_generator,  # Same instance for both Claude variants
            'claude-3.5-sonnet': self.claude_generator,
            'flux': self.flux_generator
        }
        self._current_model = None
    
    # === Public Interface ===
    def generate_new_iteration(self, selected_techniques: List[Technique], version: int) -> str:
        """Main public method to generate new Processing code"""
        try:
            # Convert techniques to string list for the model
            technique_names = [str(t.name) for t in selected_techniques]
            self._current_techniques = selected_techniques
            
            # Select model for this iteration
            self._current_model = self._select_model()
            self.log.info(f"Using model: {self._current_model}")
            
            # Store selected model in metadata
            if 'generation' not in self.config.metadata['parameters']:
                self.config.metadata['parameters']['generation'] = {}
            if 'ai_parameters' not in self.config.metadata['parameters']['generation']:
                self.config.metadata['parameters']['generation']['ai_parameters'] = {}
            
            self.config.metadata['parameters']['generation']['ai_parameters']['last_used_model'] = self._current_model
            self.config.save_metadata()
            
            # Get generator and set model
            generator = self.ai_generators[self._current_model]
            if hasattr(generator, '_select_claude_model'):
                generator._select_claude_model(self._current_model)
            
            # Special handling for Flux model
            if self._current_model == 'flux':
                # For Flux, we just need to generate the image
                prompt = ", ".join(technique_names)
                result = generator.generate_with_ai(prompt)
                if result:
                    return "Image generated successfully"  # Dummy code for Flux model
                return None
            
            # Get next version from config (which scans renders directory)
            next_version = self.config.get_next_version()
            
            # Try code generation with compilation and frame generation feedback
            for attempt in range(3):  # Max 3 attempts
                self.log.debug(f"\n=== GENERATION ATTEMPT {attempt + 1} ===")
                
                code = self._attempt_code_generation(technique_names, next_version)
                if not code:
                    continue
                    
                # Save and test the code
                self._save_code(code, next_version)
                render_path = Path(f"render_v{next_version}")
                success, error = self.run_sketch(render_path)
                
                if success:
                    # Verify frames were actually generated
                    frames_path = self.config.base_path / "renders" / str(render_path)
                    frame_files = list(frames_path.glob("frame-*.png"))
                    if frame_files:
                        return code
                    else:
                        self.log.warning(f"No frames generated on attempt {attempt + 1}, retrying...")
                        if error:
                            technique_names = f"{technique_names}\n\nPrevious attempt failed to generate frames. Error: {error}\nPlease ensure the code generates visible output.\nRemember: DO NOT include any system functions (setup, draw, etc). Focus on the creative code only."
                            continue
                
                # If compilation failed, feed error back into generation
                if error and "Error:" in error:
                    error_msg = error.split("Error:")[1].strip()
                    self.log.warning(f"Compilation error on attempt {attempt + 1}: {error_msg}")
                    technique_names = f"{technique_names}\n\nPrevious attempt had a compilation error: {error_msg}\nPlease fix the code and ensure proper type handling.\nRemember: DO NOT include any system functions (setup, draw, etc). Focus on the creative code only."
                else:
                    self.log.warning(f"Unknown error on attempt {attempt + 1}, retrying...")
                    technique_names = f"{technique_names}\n\nPrevious attempt failed. Please simplify the code and ensure it generates visible output.\nRemember: DO NOT include any system functions (setup, draw, etc). Focus on the creative code only."
            
            self.log.error("Failed to generate stable code after all attempts")
            return None
                
        except Exception as e:
            self.log.error(f"Error in code generation: {e}")
            return None
    
    def validate_processing_code(self, code: str) -> tuple[bool, str]:
        """Public validation interface"""
        print("Validating Processing code syntax...")
        
        required_parts = [
            'void setup()',
            'size(1080, 1080)',
            'frameRate(60)',
            'void draw()',
            'background(0)',
            'float progress',
            'saveFrame('
        ]
        
        for part in required_parts:
            if part not in code:
                return False, f"Missing required part: {part}"
        
        return True, None
    
    def score_pattern(self, pattern: Pattern) -> Dict[str, float]:
        """Public scoring interface"""
        try:
            render_path = self.config.base_path / "renders" / f"render_v{pattern.version}"
            scores = self.analyzer.analyze_pattern(pattern, render_path)
            
            # Update model statistics in metadata
            ai_params = self.config.metadata['parameters']['generation']['ai_parameters']
            if self._current_model and self._current_model in ai_params['generation_stats']:
                stats = ai_params['generation_stats'][self._current_model]
                stats['uses'] += 1
                # Update running average
                stats['avg_score'] = (
                    (stats['avg_score'] * (stats['uses'] - 1) + scores['overall']) 
                    / stats['uses']
                )
                self.config.save_metadata()
            
            return scores
            
        except Exception as e:
            self.log.error(f"Error scoring pattern: {e}")
            return {
                'overall': 75.0,
                'complexity': 75.0,
                'innovation': 75.0,
                'aesthetic': 75.0,
                'motion': 75.0
            }
    
    # === Core Generation Logic ===
    def _attempt_code_generation(self, technique_names: str, next_version: int) -> Optional[str]:
        """Single attempt at code generation with validation"""
        try:
            # Get generator and set model
            generator = self.ai_generators[self._current_model]
            if hasattr(generator, '_select_claude_model'):
                generator._select_claude_model(self._current_model)
            
            # Special handling for Flux model
            if self._current_model == 'flux':
                # For Flux, we just need to generate the image
                prompt = ", ".join(technique_names)
                result = generator.generate_with_ai(prompt)
                if result:
                    return "Image generated successfully"  # Dummy code for Flux model
                return None
            
            # Build generation prompt with proper markers
            prompt = f"""// Required function stubs - fill with your code
void initSketch() {{
    // Initialize variables and setup here
}}

void runSketch(float progress) {{
    // Animation code using progress (0.0 to 1.0) here
}}


=== PROCESSING SKETCH GENERATOR ===
Create a visually appealing processing animation that loops smoothly over 6 seconds.
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
• Required Techniques: {technique_names}

=== ANIMATION GUIDELINES ===
• Use the progress variable (0.0 to 1.0) for ALL animations
• Ensure smooth looping by matching start/end states
• Use map() to convert progress to specific ranges
• Use lerp() or lerpColor() for smooth transitions
• Avoid sudden jumps or discontinuities
• Consider easing functions for natural motion
• Test values at progress = 0.0, 0.5, and 1.0

=== IMPORTANT RULES ===
1. DO NOT define duplicate methods with the same signature
2. Each method overload must have different parameter types
3. Use descriptive method names to avoid conflicts
4. Return your code between these exact markers:
// YOUR CREATIVE CODE GOES HERE
[your code here]
// END OF YOUR CREATIVE CODE"""

            # Generate code with the model
            raw_code = generator.generate_with_ai(prompt)
            if not raw_code:
                return None
            
            # Clean and validate the code
            cleaned_code = self.validator.clean_code(raw_code)
            if not cleaned_code:
                return None
            
            # Check for duplicate method signatures
            if self._has_duplicate_methods(cleaned_code):
                self.log.warning("Detected duplicate method signatures, retrying with simpler code")
                return None
            
            return cleaned_code
            
        except Exception as e:
            self.log.error(f"Error in code generation attempt: {e}")
            if self.config.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())
            return None
    
    def _has_duplicate_methods(self, code: str) -> bool:
        """Check for duplicate method signatures in the code"""
        try:
            # Extract method signatures using regex
            method_pattern = r'(?:public\s+|private\s+)?(?:static\s+)?(\w+)\s+(\w+)\s*\(([\w\s,<>[\]]*)\)'
            methods = re.finditer(method_pattern, code)
            
            # Store signatures for comparison
            signatures = set()
            for match in methods:
                return_type = match.group(1)
                method_name = match.group(2)
                params = match.group(3).strip()
                
                # Create normalized signature
                signature = f"{method_name}({params})"
                
                # Check if we've seen this signature before
                if signature in signatures:
                    return True
                signatures.add(signature)
            
            return False
            
        except Exception as e:
            self.log.error(f"Error checking for duplicate methods: {e}")
            return False
    
    # === Code Processing and Validation ===
    def _clean_code(self, code: str, version: int) -> str:
        """Clean and insert code into template with proper structure"""
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
            
            # Extract just the user's creative code
            user_code = self._extract_user_code(code)
            if not user_code:
                self.log.error("Failed to extract user code")
                return None
            
            # Debug log the cleaned code
            self.log.debug(f"\nCleaned code before template insertion:\n{user_code}\n")
            
            # Basic validation
            is_valid, error = self._validate_creative_code(user_code)
            if not is_valid:
                self.log.error(f"Invalid code: {error}")
                return None
            
            # Get template and log it
            template = self._build_template_with_config(version)
            self.log.debug(f"\nTemplate before insertion:\n{template}\n")
            
            # Insert user code at the correct location
            final_code = template.replace("// YOUR CREATIVE CODE GOES HERE", user_code)
            
            # Debug log the final merged code
            self.log.debug(f"\nFinal merged code:\n{final_code}\n")
            
            return final_code
            
        except Exception as e:
            self.log.error(f"Error cleaning code: {e}")
            return None
            
    def _extract_user_code(self, code: str) -> Optional[str]:
        """Extract user's creative code from between markers"""
        try:
            # Split on markers
            parts = code.split("// YOUR CREATIVE CODE GOES HERE")
            if len(parts) < 2:
                return code.strip()  # Return whole code if no markers
            
            code = parts[1]
            parts = code.split("// END OF YOUR CREATIVE CODE")
            if len(parts) < 1:
                return code.strip()
                
            return parts[0].strip()
            
        except Exception as e:
            self.log.error(f"Error extracting user code: {e}")
            return None
    
    # === Prompt Building ===
    def _build_error_prompt(self, code: str, error_msg: str = None) -> str:
        """Build error prompt for retry attempts with improved guidance"""
        specific_guidance = self._get_error_guidance(error_msg)
        
        # Extract key error patterns
        error_patterns = {
            "NullPointerException": "• Check all variables are initialized before use\n• Verify object creation in initSketch()",
            "ArrayIndexOutOfBounds": "• Verify array indices are within bounds\n• Check array initialization sizes",
            "cannot find symbol": "• Ensure all variables are declared\n• Check for typos in variable names",
            "incompatible types": "• Verify variable type assignments\n• Check function return types",
            "Missing semicolon": "• Add missing semicolons at line ends\n• Check statement termination",
            "letterMask": "• Initialize letterMask in initSketch()\n• Follow text rendering sequence",
            "translate": "• Remove translate() calls\n• Use relative coordinates from (0,0)",
            "setup": "• Remove setup() and draw()\n• Use only initSketch() and runSketch()",
        }
        
        # Build targeted guidance based on error patterns
        targeted_guidance = []
        if error_msg:
            for pattern, guidance in error_patterns.items():
                if pattern.lower() in error_msg.lower():
                    targeted_guidance.append(guidance)
        
        error_context = f"""Previous attempt had issues that need to be fixed:
ERROR: {error_msg if error_msg else 'Unknown error'}

SPECIFIC GUIDANCE:
{specific_guidance}

{f'TARGETED FIXES:\\n{chr(10).join(targeted_guidance)}' if targeted_guidance else ''}

GENERAL REQUIREMENTS:
1. Return ONLY the creative code between the markers
2. DO NOT include setup(), draw(), or other framework code
3. Use only the provided progress variable (0.0 to 1.0) for animation
4. Keep code focused and efficient
5. Initialize all variables in initSketch()
6. Use proper Processing syntax and functions

Previous code for reference:
{code if code else '(No code was generated)'}

Please fix these issues and return the corrected code."""
        
        return error_context
    
    def _get_error_guidance(self, error_msg: str) -> str:
        """Get specific guidance based on error type with improved patterns"""
        if not error_msg:
            return "• Try a simpler approach with cleaner code structure\n• Focus on core functionality"
        
        # Common error patterns and their specific guidance
        error_patterns = {
            "translate": """• DO NOT use translate() - all positioning should be relative to canvas center (0,0)
• Use direct x,y coordinates: x = width/2 + offset
• For rotations, use rotate() with pushMatrix/popMatrix
• Remember the canvas is already centered""",
            
            "Creative validation": """• Remove any setup/draw function declarations
• Ensure no background or translate calls
• Use only the provided progress variable
• Keep code focused on the creative elements
• Initialize all variables in initSketch()""",
            
            "Core validation": """• Ensure code fits within the template structure
• Check for proper loop completion
• Verify all variables are properly scoped
• Remove any conflicting declarations
• Use Processing-specific syntax""",
            
            "letterMask": """• Declare PGraphics letterMask at the top
• Initialize in initSketch() with createGraphics()
• Use proper text rendering sequence
• Check text positioning and size""",
            
            "NullPointerException": """• Initialize all variables before use
• Check object creation in initSketch()
• Verify array/list initialization
• Debug variable scope issues""",
            
            "ArrayIndexOutOfBounds": """• Check array size calculations
• Verify index bounds in loops
• Initialize arrays with proper size
• Use array.length or list.size() for bounds""",
        }
        
        # Find matching patterns and combine guidance
        guidance = []
        for pattern, specific_guidance in error_patterns.items():
            if pattern.lower() in error_msg.lower():
                guidance.append(specific_guidance)
        
        if guidance:
            return "\n\n".join(guidance)
        
        # Default guidance for unknown errors
        return """• Simplify the implementation
• Focus on core functionality
• Ensure clean mathematical relationships
• Remove any potential conflicts
• Check variable initialization
• Verify Processing syntax"""
    
    # === File Operations ===
    def _save_code(self, code: str, version: int) -> None:
        """Save generated code to file"""
        try:
            # Use validator to build complete template
            full_code = self.validator.build_processing_template(code, version)
            
            # Ensure renders directory exists
            render_path = self.config.base_path / "renders" / f"render_v{version}"
            render_path.mkdir(parents=True, exist_ok=True)
            
            # Save the code file
            code_file = render_path / "sketch.pde"
            code_file.write_text(full_code)
            
        except Exception as e:
            self.log.error(f"Error saving code: {str(e)}")
            raise
    
    def _build_template_with_config(self, version: int) -> str:
        """Build Processing template with proper code structure"""
        return f"""// === USER'S CREATIVE CODE ===
// YOUR CREATIVE CODE GOES HERE
[your code here]
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
    
    def _update_render_path(self, code: str, version: int) -> str:
        """Update render path in code"""
        return re.sub(
            r'(String\s+renderPath\s*=\s*)"[^"]*"',
            fr'\1"renders/render_v{version}"',
            code
        )
    
    def run_sketch(self, render_path: Path) -> tuple[bool, Optional[str]]:
        """Run Processing sketch and generate frames"""
        try:
            script_path = self.config.base_path / "scripts" / "run_sketches.ps1"
            
            # Create metadata object with model info
            metadata = {
                "version": render_path.name.replace("render_v", ""),
                "techniques": [t.name for t in self._current_techniques],
                "timestamp": int(time.time() * 1000),
                "model": self._current_model,
                "parameters": {
                    "complexity": self._current_complexity,
                    "innovation": self._current_innovation
                },
                "creative_approach": {
                    "geometry_techniques": self._get_random_techniques_from_category('geometry', 3),
                    "motion_techniques": self._get_random_techniques_from_category('motion', 3),
                    "pattern_techniques": self._get_random_techniques_from_category('patterns', 3)
                }
            }
            
            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata, ensure_ascii=False)
            
            # Print final PDE code before running
            if self.config.debug_mode:
                template_path = self.config.paths['template']
                with open(template_path, 'r') as f:
                    final_code = f.read()
                self.log.debug("\n=== FINAL PDE CODE TO BE RUN ===")
                self.log.debug(final_code)
                self.log.debug("=================================\n")
            
            # Run PowerShell with metadata and capture output
            result = subprocess.run(
                [
                    "powershell.exe",
                    "-ExecutionPolicy", "Bypass",
                    "-NoProfile",
                    "-File",
                    str(script_path.absolute()),
                    "-RenderPath",
                    str(render_path.absolute()),
                    "-Metadata",
                    metadata_json
                ],
                capture_output=True,
                text=True,
                cwd=str(self.config.base_path),
                timeout=360
            )
            
            # Always log full Processing output in debug mode
            if self.config.debug_mode:
                self.log.debug("\n=== PROCESSING STDOUT ===")
                self.log.debug(result.stdout)
                self.log.debug("\n=== PROCESSING STDERR ===")
                self.log.debug(result.stderr)
                self.log.debug("========================\n")
            
            # Check for compilation errors using validator's error patterns
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                guidance = self.validator.build_error_guidance(error_msg)
                if guidance:
                    self.log.debug(f"\n=== ERROR GUIDANCE ===\n{guidance}\n==================\n")
                return False, error_msg
            
            # Check if frames were generated
            frames_path = self.config.base_path / "renders" / str(render_path)
            frame_files = list(frames_path.glob("frame-*.png"))
            if not frame_files:
                # If no frames but also no error, check output for clues
                if "Error:" in result.stdout or "error:" in result.stdout.lower():
                    error_lines = [line for line in result.stdout.splitlines() if "error" in line.lower()]
                    error_msg = "\n".join(error_lines)
                else:
                    error_msg = "No frames were generated and no error was reported. This might indicate a runtime error or infinite loop."
                
                self.log.error(f"No frame files found in {frames_path}")
                return False, error_msg
            
            # Check for video generation success
            if "Video saved as:" in result.stdout:
                self.log.success("Sketch execution and video generation successful")
                return True, None
            
            return True, None
            
        except subprocess.TimeoutExpired:
            error_msg = "Sketch execution timed out after 6 minutes"
            self.log.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Error running sketch: {str(e)}"
            self.log.error(error_msg)
            if self.config.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())
            return False, error_msg
    
    def _get_random_techniques_from_category(self, category: str, count: int = 3) -> List[str]:
        """Get random techniques from a specific category in config"""
        if category not in self.config.technique_categories:
            return []
        techniques = self.config.technique_categories[category]
        count = min(count, len(techniques))
        return random.sample(techniques, count)
    
    def _select_model(self) -> str:
        """Select a model based on config weights"""
        model_config = self.config.get_model_config()
        if model_config['model_selection'] != 'random':
            return model_config['model_selection']
        
        weights = model_config['model_weights']
        models = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(models, weights=probabilities, k=1)[0]
    
    def _build_simpler_prompt(self, original_prompt: str) -> str:
        """Build a simpler prompt when model returns no code"""
        return f"""Let's try a simpler approach. Create a basic Processing animation using just one or two techniques.
Focus on creating something minimal but effective.

Original techniques to consider: {original_prompt}

Return the code between the markers."""
    
    def _get_next_version(self) -> int:
        """Determine next version number by scanning renders directory"""
        try:
            renders_path = self.config.base_path / "renders"
            if not renders_path.exists():
                return 1
                
            # Find all render_v* directories and extract version numbers
            versions = []
            for dir_path in renders_path.glob("render_v*"):
                try:
                    version_str = dir_path.name.replace("render_v", "")
                    version = int(version_str)
                    versions.append(version)
                except ValueError:
                    continue
                    
            return max(versions, default=0) + 1
        except Exception as e:
            self.log.error(f"Error determining next version: {e}")
            return 1
    
    def generate_with_model(self, model: str, techniques: List[str]) -> Optional[str]:
        """Generate code using a specific model"""
        self.log.debug(f"Generating with model: {model}")
        
        # Convert techniques to string if they're not already
        technique_str = techniques if isinstance(techniques, str) else ', '.join(techniques)
        
        # Set the current model before generation
        self._current_model = model
        
        # Use the generator from ai_generators dictionary
        if model in self.ai_generators:
            generator = self.ai_generators[model]
            # Explicitly set the model on the generator instance
            if hasattr(generator, 'current_model'):
                generator.current_model = model
            return generator.generate_with_ai(technique_str)
        else:
            self.log.error(f"Unknown model: {model}")
            return None