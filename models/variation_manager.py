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
import json
import time

class VariationManager:
    def __init__(self, config: Config, log: ArtLogger, generator: ProcessingGenerator, db):
        self.config = config
        self.log = log
        self.generator = generator
        self.db = db
        self.flux_generator = None
        self.debug_mode = False  # Add debug mode tracking

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
            
            # Check for MP4 files first (dynamic)
            mp4_files = list(render.glob("animation_*.mp4"))
            if mp4_files:
                print(f"{i}. render_v{version} (Dynamic)")
            else:
                # If no MP4, check for PNG files (static)
                png_files = list(render.glob("*.png"))
                if png_files:
                    json_files = list(render.glob(f"image_v{version}*.json"))
                    if json_files:
                        print(f"{i}. render_v{version} (Static)")
                    else:
                        print(f"{i}. render_v{version} (Static - No Metadata)")
                else:
                    print(f"{i}. render_v{version} (Unknown Type)")
        
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
                    
                    # Check for MP4 files first (dynamic)
                    mp4_files = list(selected_render.glob("animation_*.mp4"))
                    if mp4_files:
                        self._create_dynamic_variation(selected_render)
                    else:
                        # If no MP4, check for PNG files (static)
                        png_files = list(selected_render.glob("*.png"))
                        if png_files:
                            json_files = list(selected_render.glob(f"image_v{version}*.json"))
                            if json_files:
                                self._create_static_variation(json_files[0])
                            else:
                                self.log.error("Metadata file not found for static image")
                        else:
                            self.log.error("Unknown render type - cannot create variation")
                    break
                else:
                    print("Invalid choice")
            except ValueError:
                print("Please enter a valid number")
            except Exception as e:
                self.log.error(f"Error in variation flow: {e}")
                if self.debug_mode:
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
            if self.debug_mode:
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
            
            # Extract user code section with more flexible regex
            user_code_match = re.search(
                r"(?s)// === USER'S CREATIVE CODE ===\s*(.*?)\s*// END OF YOUR CREATIVE CODE", 
                original_code
            )
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
                max_retries = 3
                success = False
                
                # Try to generate variation with retries
                for retry in range(max_retries):
                    if retry > 0:
                        self.log.info(f"Retry attempt {retry} of {max_retries-1}")
                    
                    # Use O1's variation generation
                    o1_generator = self.generator.o1_generator
                    new_code = o1_generator.create_variation(user_code, modification, retry)
                    
                    if not new_code:
                        self.log.error(f"Attempt {retry+1}: Failed to generate valid code. Retrying...")
                        if retry < max_retries - 1:
                            continue
                        else:
                            self.log.error("Failed to generate valid code after all attempts")
                            break
                    
                    # Get next version and build template
                    next_version = self.config.get_next_version()
                    final_code = o1_generator.build_processing_template(new_code, next_version)
                    
                    # Save the code
                    with open(self.config.paths['template'], 'w') as f:
                        f.write(final_code)
                    
                    # Run the sketch
                    render_path = f"renders/render_v{next_version}"
                    success = self._run_sketch(render_path)
                    
                    if success:
                        # Create pattern with parent reference
                        new_pattern = Pattern(
                            version=next_version,
                            code=new_code,
                            timestamp=datetime.now(),
                            techniques=pattern.techniques if pattern else [],
                            parent_patterns=[int(version)]  # Just keep the parent reference
                        )
                        
                        # Score and save pattern
                        scores = self.generator.score_pattern(new_pattern)
                        new_pattern.update_scores(scores)
                        self.db.save_pattern(new_pattern)
                        
                        self.log.success(f"Successfully created variation {i+1}")
                        break  # Break retry loop on success
                    else:
                        self.log.error(f"Attempt {retry+1}: Failed to run variation. Retrying...")
                        if retry < max_retries - 1:
                            continue
                
                if not success:
                    self.log.error(f"Failed to create variation {i+1} after {max_retries} attempts")
            
        except Exception as e:
            self.log.error(f"Error creating dynamic variation: {e}")
            if self.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())

    def _get_variation_modification(self):
        """Get user input for variation modification"""
        print("\n════════════════════════════════════════════════════════════════════════════════")
        print("║ VARIATION WIZARD")
        print("════════════════════════════════════════════════════════════════════════════════\n")
        
        options = {
            1: ("Motion", [
                "Make it move faster",
                "Make it move slower",
                "Add wave motion",
                "Add spiral motion",
                "Reverse the motion",
                "Make it bounce"
            ]),
            2: ("Shapes", [
                "Use squares instead",
                "Use triangles instead",
                "Use circles instead",
                "Make shapes bigger",
                "Make shapes smaller",
                "Add more shapes"
            ]),
            3: ("Colors", [
                "Make it black and white",
                "Use rainbow colors",
                "Use only blue shades",
                "Use only red shades",
                "Make it monochrome",
                "Invert the colors"
            ]),
            4: ("Pattern", [
                "Make it denser",
                "Make it sparser",
                "Add randomness",
                "Make it symmetrical",
                "Add rotation",
                "Mirror the pattern"
            ]),
            5: ("Custom", None)
        }
        
        print("Choose modification type:")
        for num, (category, _) in options.items():
            print(f"{num}. {category}")
        
        while True:
            try:
                choice = int(input("\nEnter choice (1-5): "))
                if 1 <= choice <= 5:
                    break
                print("Invalid choice")
            except ValueError:
                print("Please enter a number")
        
        if choice == 5:
            # Custom modification
            return input("\nEnter your custom modification instruction:\n> ")
        
        # Show specific options for chosen category
        category, suboptions = options[choice]
        print(f"\nChoose {category.lower()} modification:")
        for i, option in enumerate(suboptions, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                subchoice = int(input(f"\nEnter choice (1-{len(suboptions)}): "))
                if 1 <= subchoice <= len(suboptions):
                    return suboptions[subchoice - 1]
                print("Invalid choice")
            except ValueError:
                print("Please enter a number")

    def _run_sketch(self, render_path: str) -> bool:
        """Run the Processing sketch"""
        try:
            script_path = self.config.base_path / "scripts" / "run_sketches.ps1"
            metadata = {
                "version": render_path.replace("render_v", ""),
                "timestamp": int(time.time() * 1000),
                "type": "variation"
            }
            metadata_str = json.dumps(metadata)
            
            # Run PowerShell script with parameters
            cmd = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", str(script_path),
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