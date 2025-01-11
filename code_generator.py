from typing import Dict, List, Optional
import subprocess
from pathlib import Path
import re
from models.openai_4o import OpenAI4OGenerator
from models.openai_o1 import OpenAIO1Generator
from models.data_models import Pattern, Technique
from logger import ArtLogger
from pattern_analyzer import PatternAnalyzer
from config import Config
import json
import time
import random
import shutil

class ProcessingGenerator:
    def __init__(self, config: Config, logger: ArtLogger = None):
        self.config = config
        self.db = config.db_manager
        self.log = logger or ArtLogger()
        self.analyzer = PatternAnalyzer(config, self.log)
        # Initialize current state tracking
        self._current_techniques = []
        self._current_complexity = 0.7  # Default values
        self._current_innovation = 0.5  # Default values
        # Initialize AI generators
        self.ai_generators = {
            'o1': OpenAIO1Generator(config, self.log),
            'o1-mini': OpenAIO1Generator(config, self.log),
            '4o': OpenAI4OGenerator(config, self.log)
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
            
            # Get next version from config (which scans renders directory)
            next_version = self.config.get_next_version()
            code = self._attempt_code_generation(technique_names, next_version)
            if code:
                # Save and test the code
                self._save_code(code, next_version)
                render_path = Path(f"render_v{next_version}")
                if self.run_sketch(render_path):
                    return code
            
            self.log.error("Failed to generate stable code")
            return None
                
        except Exception as e:
            self.log.error(f"Error in code generation: {e}")
            return None
    
    def validate_processing_code(self, code: str) -> tuple[bool, str]:
        """Public validation interface"""
        print("Validating Processing code syntax...")
        
        required_parts = [
            'void setup()',
            'size(800, 800)',
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
    def _attempt_code_generation(self, prompt: str, version: int, max_attempts: int = 3) -> str:
        """Attempt to generate valid code with retries"""
        last_code = None
        last_error = None
        original_prompt = prompt
        
        for attempt in range(max_attempts):
            try:
                self.log.debug(f"\n=== GENERATION ATTEMPT {attempt + 1} ===")
                if last_error:
                    self.log.debug(f"Previous error: {last_error}")
                    
                generator = self.ai_generators[self._current_model]
                if generated_code := self._try_single_generation(generator, prompt, attempt, version):
                    return generated_code
                    
            except ValueError as e:
                last_error = str(e)
                self.log.error(f"Generation attempt {attempt + 1} failed: {e}")
                
                # Build error prompt with last code and error
                if "Model returned no code" in str(e):
                    # If no code was returned, try a simpler prompt
                    prompt = self._build_simpler_prompt(original_prompt)
                    self.log.debug(f"\n=== SIMPLIFIED PROMPT ===\n{prompt}\n==================\n")
                else:
                    # Otherwise use the error prompt with the last code
                    prompt = self._build_error_prompt(last_code, last_error)
                    self.log.debug(f"\n=== ERROR PROMPT ===\n{prompt}\n==================\n")
                    
            except Exception as e:
                last_error = str(e)
                self.log.error(f"Unexpected error in attempt {attempt + 1}: {e}")
                prompt = self._build_error_prompt(last_code, str(e))
                self.log.debug(f"\n=== ERROR PROMPT ===\n{prompt}\n==================\n")
                
            finally:
                if 'generated_code' in locals():
                    last_code = generated_code
        
        self.log.error("Failed to generate valid code after all attempts")
        return None
    
    def _try_single_generation(self, generator, prompt: str, attempt: int, version: int) -> Optional[str]:
        """Single attempt at code generation with validation"""
        try:
            temperature = 0.85 + (attempt * 0.05)
            if isinstance(generator, OpenAI4OGenerator):
                raw_code = generator.generate_with_ai(prompt, temperature)
            else:
                raw_code = generator.generate_with_ai(prompt)
            
            if not raw_code:
                self.log.warning(f"Attempt {attempt + 1}: AI returned no code")
                raise ValueError("Model returned no code")  # Convert to ValueError to trigger retry
            
            # Validate creative code
            is_valid, error_msg = self._validate_creative_code(raw_code)
            if not is_valid:
                self.log.warning(f"Attempt {attempt + 1}: Creative code validation failed - {error_msg}")
                raise ValueError(f"Creative validation: {error_msg}")
            
            # Clean and merge code
            merged_code = self._clean_code(raw_code, version)
            if not merged_code:
                self.log.warning(f"Attempt {attempt + 1}: Code cleaning failed")
                raise ValueError("Failed to clean and merge code")
            
            # Validate core requirements
            core_valid, core_error = self._validate_core_requirements(merged_code)
            if not core_valid:
                self.log.warning(f"Attempt {attempt + 1}: Core validation failed - {core_error}")
                raise ValueError(f"Core validation: {core_error}")
            
            self.log.success(f"Code generated successfully on attempt {attempt + 1}")
            return merged_code
            
        except ValueError:
            # Re-raise ValueError to trigger retry with error message
            raise
        except Exception as e:
            self.log.error(f"Unexpected error in generation attempt {attempt + 1}: {e}")
            raise ValueError(f"Generation error: {e}")
    
    def _validate_creative_code(self, code: str) -> tuple[bool, str]:
        """Validate creative code for forbidden elements"""
        return self.ai_generators[self._current_model].validate_creative_code(code)
    
    def _validate_core_requirements(self, code: str) -> tuple[bool, str]:
        """Validate only essential Processing code requirements"""
        return self.ai_generators[self._current_model].validate_core_requirements(code)
    
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
        """Build error prompt for retry attempts"""
        specific_guidance = self._get_error_guidance(error_msg)
        
        error_context = f"""Previous attempt had issues that need to be fixed:
ERROR: {error_msg if error_msg else 'Unknown error'}

GUIDANCE:
{specific_guidance}

Previous code for reference:
{code if code else '(No code was generated)'}

REQUIREMENTS:
1. Return ONLY the creative code between the markers
2. DO NOT include setup(), draw(), or other framework code
3. Use only the provided progress variable (0.0 to 1.0) for animation
4. Keep code focused and efficient

Please fix these issues and return the corrected code."""
        
        return error_context
    
    def _get_error_guidance(self, error_msg: str) -> str:
        """Get specific guidance based on error type"""
        if not error_msg:
            return "• Try a simpler approach with cleaner code structure"
        
        if "Contains translate()" in error_msg:
            return """• DO NOT use translate() - all positioning should be relative to canvas center (0,0)
• Use direct x,y coordinates: x = width/2 + offset
• For rotations, use rotate() with pushMatrix/popMatrix
• Remember the canvas is already centered"""
        
        if "Creative validation" in error_msg:
            return """• Remove any setup/draw function declarations
• Ensure no background or translate calls
• Use only the provided progress variable
• Keep code focused on the creative elements"""
        
        if "Core validation" in error_msg:
            return """• Ensure code fits within the template structure
• Check for proper loop completion
• Verify all variables are properly scoped
• Remove any conflicting declarations"""
        
        return """• Simplify the implementation
• Focus on core functionality
• Ensure clean mathematical relationships
• Remove any potential conflicts"""
    
    # === File Operations ===
    def _save_code(self, code: str, version: int) -> None:
        """Save generated code to auto.pde"""
        try:
            # Save to auto.pde
            template_path = self.config.paths['template']
            with open(template_path, 'w') as f:
                f.write(code)
            
            # Verify auto.pde was saved
            if not template_path.exists():
                self.log.error(f"Failed to save {template_path}")
                return
                
            self.log.success(f"Saved code to {template_path}")
            
        except Exception as e:
            self.log.error(f"Failed to save code: {e}")
    
    def _build_template_with_config(self, version: int) -> str:
        """Build Processing template with proper code structure"""
        return f"""// === USER'S CREATIVE CODE ===
// YOUR CREATIVE CODE GOES HERE
// END OF YOUR CREATIVE CODE

// === SYSTEM FRAMEWORK ===
void setup() {{
    size(800, 800);
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
    
    def run_sketch(self, render_path: Path) -> tuple[bool, str]:
        """Run Processing sketch and generate frames"""
        try:
            script_path = self.config.base_path / "scripts" / "run_sketches.ps1"
            
            # Create metadata object with model info
            metadata = {
                "version": render_path.name.replace("render_v", ""),
                "techniques": [t.name for t in self._current_techniques],
                "timestamp": int(time.time() * 1000),
                "model": self._current_model,  # Use actual selected model
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
            
            # Run PowerShell with metadata and correct sketch name
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
            
            if result.returncode == 0 and "Video saved as:" in result.stdout:
                self.log.success("Sketch execution and video generation successful")
                self.log.info(result.stdout)
                return True, "Success"
            else:
                # Improve error reporting
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                if not error_msg:
                    error_msg = "Unknown Processing execution error"
                self.log.error(f"Sketch execution failed: {error_msg}")
                return False, error_msg
            
        except subprocess.TimeoutExpired:
            error_msg = "Sketch execution timed out after 6 minutes"
            self.log.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error running sketch: {str(e)}"
            self.log.error(error_msg)
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