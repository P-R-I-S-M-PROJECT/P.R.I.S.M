import re
import subprocess
from pathlib import Path
from datetime import datetime
import openai
from models import Pattern
from logger import ArtLogger
from config import Config
from code_generator import ProcessingGenerator
from models.flux import FluxGenerator

class VariationManager:
    def __init__(self, config: Config, log: ArtLogger, generator: ProcessingGenerator, db):
        self.config = config
        self.log = log
        self.generator = generator
        self.db = db
        self.flux_generator = None

    def show_variation_flow(self):
        """Show variation mode interface"""
        self.log.title("VARIATION MODE")
        
        # Get list of render directories
        render_path = self.config.base_path / "renders"
        if not render_path.exists():
            self.log.error("No existing renders found")
            return
            
        # List available renders
        renders = sorted([d for d in render_path.glob("render_v*") if d.is_dir()], 
                        key=lambda x: int(str(x).split("_v")[-1]))
        
        if not renders:
            self.log.error("No renders found to create variations from")
            return
            
        print("\nAvailable pieces:")
        for i, render in enumerate(renders, 1):
            version = str(render).split("_v")[-1]
            png_files = list(render.glob("*.png"))
            if png_files:
                json_files = list(render.glob(f"image_v{version}*.json"))
                if json_files:
                    print(f"{i}. render_v{version} (Static)")
                else:
                    print(f"{i}. render_v{version} (Static)")
            else:
                print(f"{i}. render_v{version} (Dynamic)")
        
        print(f"{len(renders) + 1}. Back to Main Menu")
        
        while True:
            try:
                choice = input("\nSelect piece to create variation from (1-{}): ".format(len(renders) + 1))
                if not choice.isdigit():
                    print("Please enter a number")
                    continue
                    
                choice = int(choice)
                if choice == len(renders) + 1:
                    return
                    
                if 1 <= choice <= len(renders):
                    selected_render = renders[choice - 1]
                    version = str(selected_render).split("_v")[-1]
                    
                    png_files = list(selected_render.glob("*.png"))
                    if png_files:
                        json_files = list(selected_render.glob(f"image_v{version}*.json"))
                        if json_files:
                            self._create_static_variation(json_files[0])
                        else:
                            self.log.error("Metadata file not found for static image")
                    else:
                        self._create_dynamic_variation(selected_render)
                    break
                else:
                    print("Invalid choice")
            except ValueError:
                print("Please enter a valid number")
            except Exception as e:
                self.log.error(f"Error in variation flow: {e}")
                if self.config.debug_mode:
                    import traceback
                    self.log.debug(traceback.format_exc())
                break

    def _create_static_variation(self, metadata_file: Path):
        """Create variation of a static Flux piece"""
        try:
            if not self.flux_generator:
                self.flux_generator = FluxGenerator(self.config, self.log)
            
            self.flux_generator.create_variation(metadata_file)
            
        except Exception as e:
            self.log.error(f"Error creating static variation: {e}")
            if self.config.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())
    
    def _create_dynamic_variation(self, render_dir: Path):
        """Create variation of a dynamic Processing piece"""
        try:
            version = str(render_dir).split("_v")[-1]
            
            # Try to find original PDE file
            pde_file = render_dir / f"prism_v{version}.pde"
            if not pde_file.exists():
                pde_file = self.config.base_path / "prism.pde"
            
            if not pde_file.exists():
                self.log.error("Could not find original PDE file")
                return
            
            # Read original code
            with open(pde_file) as f:
                original_code = f.read()
            
            # Extract user code section
            user_code_match = re.search(r"// === USER'S CREATIVE CODE ===\n(.*?)// END OF YOUR CREATIVE CODE", 
                                      original_code, re.DOTALL)
            if not user_code_match:
                self.log.error("Could not extract user code section")
                return
                
            user_code = user_code_match.group(1).strip()
            
            # Get pattern from database for techniques
            pattern = self.db.get_pattern_by_version(int(version))
            if pattern:
                self.log.info(f"\nOriginal techniques: {', '.join(pattern.techniques)}")
            
            # Get number of variations
            while True:
                try:
                    num_variations = input("\nHow many variations would you like to generate? (1-10): ").strip()
                    num_variations = int(num_variations)
                    if 1 <= num_variations <= 10:
                        break
                    print("Please enter a number between 1 and 10")
                except ValueError:
                    print("Please enter a valid number")
            
            # Generate variations
            for i in range(num_variations):
                self.log.info(f"\nCreating variation {i+1} of {num_variations}")
                
                modification = self._get_variation_modification()
                
                # Build prompt for code variation
                system_prompt = f"""You are helping create a variation of an existing Processing sketch.
Here is the original creative code:

{user_code}

The user wants these changes: {modification}

Create a new version that maintains the core style and functionality,
but incorporates the requested changes. Return only the code that goes
between the USER'S CREATIVE CODE markers.

Important guidelines:
1. Keep the animation smooth and looping
2. Maintain the use of the progress variable (0.0 to 1.0)
3. Preserve any existing variables or functions unless directly modified
4. Ensure all shapes are drawn relative to (0,0)
5. Do not include any system functions (setup, draw, etc)"""

                # Get new code from OpenAI
                client = openai.OpenAI(api_key=self.config.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": "Generate the new code."}
                    ],
                    temperature=0.7
                )
                
                new_code = response.choices[0].message.content.strip()
                
                # Validate new code
                success, error = self.generator.validate_creative_code(new_code)
                if not success:
                    self.log.error(f"Generated code validation failed: {error}")
                    continue
                
                # Update template with new code
                template = self.generator._build_template_with_config(self.config.get_next_version())
                final_code = template.replace("// === USER'S CREATIVE CODE ===\n", 
                                           f"// === USER'S CREATIVE CODE ===\n{new_code}\n")
                
                # Save and run new code
                with open(self.config.paths['template'], 'w') as f:
                    f.write(final_code)
                
                # Run the sketch
                next_version = self.config.get_next_version()
                render_path = f"renders/render_v{next_version}"
                success = self._run_sketch(render_path)
                
                if success:
                    # Create pattern with parent reference
                    new_pattern = Pattern(
                        version=next_version,
                        code=new_code,
                        timestamp=datetime.now(),
                        techniques=pattern.techniques if pattern else [],
                        parent_patterns=[int(version)],
                        variation_type=f"Dynamic variation ({modification})"
                    )
                    
                    # Score and save pattern
                    scores = self.generator.score_pattern(new_pattern)
                    new_pattern.update_scores(scores)
                    self.db.save_pattern(new_pattern)
                    
                    # Update documentation
                    self.docs.update(new_pattern)
                    
                    self.log.success(f"Successfully created variation {i+1}")
                else:
                    self.log.error(f"Failed to create variation {i+1}")
            
        except Exception as e:
            self.log.error(f"Error creating dynamic variation: {e}")
            if self.config.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())

    def _get_variation_modification(self):
        """Get user input for variation modification"""
        print("\n════════════════════════════════════════════════════════════════════════════════")
        print("║ DYNAMIC VARIATION WIZARD")
        print("════════════════════════════════════════════════════════════════════════════════\n")
        
        print("How would you like to modify the animation?")
        print("1. Change motion pattern")
        print("2. Modify shapes/geometry")
        print("3. Adjust colors/style")
        print("4. Change timing/speed")
        print("5. Add new elements")
        print("6. Custom modification")
        
        while True:
            try:
                choice = int(input("\nEnter choice (1-6): "))
                if 1 <= choice <= 6:
                    break
                print("Invalid choice")
            except ValueError:
                print("Please enter a number")
        
        modification_options = {
            1: {
                "name": "motion pattern",
                "options": [
                    "Linear movement",
                    "Circular motion", 
                    "Wave patterns",
                    "Random movement",
                    "Spiral motion",
                    "Oscillation"
                ]
            },
            2: {
                "name": "geometry",
                "options": [
                    "Circles",
                    "Squares",
                    "Triangles", 
                    "Lines",
                    "Custom polygons",
                    "Mixed shapes"
                ]
            },
            3: {
                "name": "style",
                "options": [
                    "Monochrome",
                    "Rainbow colors",
                    "Complementary colors",
                    "Grayscale", 
                    "Custom color palette",
                    "Color cycling"
                ]
            },
            4: {
                "name": "timing",
                "options": [
                    "Slower motion",
                    "Faster motion",
                    "Variable speed",
                    "Reverse motion",
                    "Pause points",
                    "Custom timing"
                ]
            },
            5: {
                "name": "element",
                "options": [
                    "Particle effects",
                    "Trail effects",
                    "Background patterns",
                    "Interactive elements",
                    "Text elements",
                    "Custom elements"
                ]
            }
        }
        
        if choice == 6:
            print("\nEnter your custom modification instruction:")
            return input("> ").strip()
        
        options = modification_options[choice]
        print(f"\nSelect new {options['name']}:")
        for i, opt in enumerate(options['options'], 1):
            print(f"{i}. {opt}")
            
        while True:
            try:
                subchoice = int(input(f"\nEnter choice (1-{len(options['options'])}): "))
                if 1 <= subchoice <= len(options['options']):
                    if choice == 5:
                        return f"Add {options['options'][subchoice-1].lower()} to the animation"
                    else:
                        action = "Change" if choice != 4 else "Modify"
                        target = "the animation timing to use" if choice == 4 else f"all shapes to" if choice == 2 else f"the {options['name']} to"
                        return f"{action} {target} {options['options'][subchoice-1].lower()}"
            except ValueError:
                print("Please enter a number")

    def _run_sketch(self, render_path: str) -> bool:
        """Run the Processing sketch"""
        try:
            script_path = self.config.base_path / "scripts" / "run_sketches.ps1"
            metadata_str = "{}"
            
            # Run PowerShell script with parameters
            cmd = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path),
                "-SketchName", "prism",
                "-RenderPath", str(render_path),
                "-Metadata", metadata_str
            ]
            
            self.log.debug(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log.error(f"Sketch execution failed: {result.stderr}")
                return False
                
            return True
            
        except Exception as e:
            self.log.error(f"Error running sketch: {e}")
            return False 