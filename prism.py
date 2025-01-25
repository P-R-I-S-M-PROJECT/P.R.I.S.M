import os
import time
import subprocess
import re
from dotenv import load_dotenv
from config import Config
from code_generator import ProcessingGenerator
from documentation_manager import DocumentationManager
from logger import ArtLogger
from pattern_evolution import PatternEvolution
from cleanup import SystemCleaner
from datetime import datetime
from database_manager import DatabaseManager
from models import Pattern
from tests import TestRunner
from models.flux import FluxGenerator
import json
from typing import Dict, List
import sys
import random
from pathlib import Path
import openai

# Load environment variables
load_dotenv()

class PRISM:
    def __init__(self):
        """Initialize PRISM system"""
        self.config = Config()  # Initialize without arguments
        self.log = ArtLogger()
        self.debug_mode = False  # Add debug_mode initialization
        self.selected_model = None
        self.flux_generator = None  # Initialize flux_generator to None
        
        # Initialize database
        self.db = DatabaseManager(self.config)
        
        # Load system stats
        stats = self.db.get_system_stats()
        if stats:
            self.log.info("\nPattern Statistics:")
            self.log.info(f"• Total Patterns: {stats['total_patterns']}")
            self.log.info(f"• Latest Version: v{stats['latest_version']}")
            self.log.info(f"• High Scoring Patterns: {stats['high_scoring_patterns']}")
            self.log.info("\nPerformance Metrics:")
            self.log.info(f"• Average Score: {stats['avg_score']:.2f}")
            self.log.info(f"• Average Innovation: {stats['avg_innovation']:.2f}")
            self.log.info(f"• Average Complexity: {stats['avg_complexity']:.2f}")
            self.log.info("\nTop Technique Combinations:")
            for combo in stats.get('top_technique_combinations', []):
                self.log.info(f"• {combo}")
        
        # Initialize components with shared logger
        self.generator = ProcessingGenerator(self.config, self.log)
        self.docs = DocumentationManager(self.config, self.log)
        self.evolution = PatternEvolution(self.config, self.log)
        self.cleaner = SystemCleaner(self.config, self.log)
        self.test_runner = TestRunner(self.config, self.generator, self.evolution, self.db)
        
        # Add npm installation tracking
        self._npm_installed = False
        
        # Display initial stats
        self._display_system_stats()
    
    def _display_system_stats(self):
        """Display current system statistics"""
        self.log.title("SYSTEM STATISTICS")
        
        stats = self.db.get_system_stats()
        
        self.log.info(f"""
Pattern Statistics:
• Total Patterns: {stats['total_patterns']}
• Latest Version: v{stats['latest_version']}
• High Scoring Patterns: {stats['high_scoring_patterns']}

Performance Metrics:
• Average Score: {stats['avg_score']:.2f}
• Average Innovation: {stats['avg_innovation']:.2f}
• Average Complexity: {stats['avg_complexity']:.2f}

Top Technique Combinations:""")
        
        for combo in stats['top_technique_combinations']:
            self.log.info(f"• {combo['combination']}: {combo['synergy_score']:.2f} ({combo['usage_count']} uses)")
        
        self.log.separator()
    
    def cleanup_system(self):
        """Reset system to template state"""
        self.cleaner.cleanup_system()
    
    def show_menu(self):
        """Display interactive menu"""
        while True:
            self.log.title("PRISM GENERATION SYSTEM")
            print("\nOptions:")
            print("1. Create Art")
            print("2. Studio Cleanup")
            print("3. Toggle Debug Mode")
            print("4. Test O1 Models")
            print("5. Test Claude Models")
            print("6. Variation Mode")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == "1":
                self._show_creation_flow()
            elif choice == "2":
                self.cleanup_system()
            elif choice == "3":
                self.toggle_debug_mode()
            elif choice == "4":
                self.test_runner.test_o1_models()
            elif choice == "5":
                self.test_runner.test_claude_models()
            elif choice == "6":
                self._show_variation_flow()
            elif choice == "7":
                self.log.title("Exiting Studio")
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def _show_creation_flow(self):
        """Show streamlined creation flow"""
        self.log.title("SELECT CREATIVE MODEL")
        print("\nAvailable Models:")
        print("1. Random")
        print("2. O1")
        print("3. O1-mini")
        print("4. 4O")
        print("5. Claude 3.5 Sonnet")
        print("6. Claude 3 Opus")
        print("7. Flux (Static artwork)")
        print("8. Back to Main Menu")
        
        choice = input("\nEnter your choice (1-8): ")
        
        model_map = {
            "1": "random",
            "2": "o1",
            "3": "o1-mini",
            "4": "4o",
            "5": "claude-3.5-sonnet",
            "6": "claude-3-opus",
            "7": "flux"
        }
        
        if choice in model_map:
            self.selected_model = model_map[choice]
            self.config.model_config['model_selection'] = self.selected_model
            
            # Initialize Flux generator if selected
            if self.selected_model == "flux":
                if self.flux_generator is None:
                    self.flux_generator = FluxGenerator(self.config, self.log)
            
            self._show_generation_menu()
        elif choice == "8":
            return
        else:
            print("\nInvalid choice. Please try again.")
    
    def _show_generation_menu(self):
        """Show generation options menu"""
        while True:
            self.log.title("CREATION OPTIONS")
            print("\nCreation Mode:")
            print("1. Single Creation")
            print("2. Multiple Pieces")
            print("3. Continuous Studio")
            print("4. Back to Model Selection")
            print("5. Back to Main Menu")
            
            current_model = self.config.model_config['model_selection']
            print(f"\nCurrent Model: {current_model}")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                self.run_iteration()
                input("\nPress Enter to continue...")
            elif choice == "2":
                try:
                    count = int(input("How many pieces to create? "))
                    if count > 0:
                        for i in range(count):
                            self.log.info(f"\nCreating piece {i+1} of {count}")
                            self.run_iteration()
                        input("\nCreation complete. Press Enter to continue...")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "3":
                try:
                    interval = int(input("Enter interval between creations in seconds: "))
                    if interval <= 0:
                        print("Interval must be greater than 0 seconds")
                        continue
                    self.run_continuous(interval)
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "4":
                self._show_creation_flow()
                break
            elif choice == "5":
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def run_continuous(self, interval: int):
        """Run continuous pattern generation with specified interval"""
        self.log.info(f"Starting continuous automation (interval: {interval}s)...")
        
        try:
            while True:
                print("\n" + "═" * 80)
                print("║ NEW ITERATION")
                print("═" * 80)
                
                # Generate creative approach
                techniques = self._select_random_techniques()
                technique_names = [t.name for t in techniques]
                self.log.info(f"Creative approach: {', '.join(technique_names)}")
                
                # Generate pattern using appropriate generator
                if self.selected_model == "flux":
                    self.flux_generator.generate_with_ai(",".join(technique_names))
                else:
                    self._generate_pattern(techniques, self.generator)
                
                self.log.info(f"Waiting {interval} seconds until next generation...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.log.info("Continuous generation stopped by user")
            return
    
    def run_iteration(self):
        """Run one complete iteration"""
        self.log.title("NEW ITERATION")
        try:
            # Get creative direction
            techniques = self.evolution.select_techniques()
            if not techniques:
                self.log.error("Failed to select techniques")
                return
            
            # Convert numpy strings to regular strings for display and storage
            technique_names = [str(t.name) for t in techniques]
            self.log.info(f"Creative approach: {technique_names}")
            
            # Log which model we're using
            current_model = self.config.model_config['model_selection']
            self.log.info(f"Using model: {current_model}")
            
            # For Flux model, initialize if needed
            if current_model == "flux":
                if self.flux_generator is None:
                    self.flux_generator = FluxGenerator(self.config, self.log)
                self.flux_generator.generate_with_ai(",".join(technique_names))
            else:
                # Generate code and run sketch
                next_version = self.config.get_next_version()
                new_code = self.generator.generate_new_iteration(techniques, next_version)
                if not new_code:
                    self.log.error("Failed to generate code")
                    return
                
                # Create and score pattern with string technique names
                pattern = Pattern(
                    version=next_version,
                    code=new_code,
                    timestamp=datetime.now(),
                    techniques=technique_names  # Use converted strings
                )
                
                # Score pattern
                scores = self.generator.score_pattern(pattern)
                pattern.update_scores(scores)
                
                # Save pattern
                self.db.save_pattern(pattern)
                
                # Display scores
                self.log.pattern_score(pattern.score)
                self.log.info(f"Innovation: {pattern.innovation_score:.2f}, "
                             f"Aesthetic: {pattern.aesthetic_score:.2f}, "
                             f"Complexity: {pattern.mathematical_complexity:.2f}")
                
                # Evolve techniques
                for technique in techniques:
                    self.evolution.evolve_technique(technique, pattern.get_metrics())
                
                # Update documentation
                self.docs.update(pattern)
            
        except Exception as e:
            self.log.error(f"Error in iteration: {e}")
    
    def _sync_to_server(self):
        """Sync videos to web server"""
        try:
            web_dir = self.config.base_path / "web"
            
            # Get latest video file
            videos_dir = web_dir / 'public' / 'videos'
            video_files = sorted(
                [f for f in videos_dir.glob('*.mp4')],
                key=lambda x: int(str(x).split('-')[-1].split('.')[0]),
                reverse=True
            )
            if not video_files:
                self.log.error("No video files found to sync")
                return False
            
            latest_video = video_files[0].name
            
            # Run the sync script
            self.log.info("Syncing video to server...")
            try:
                # Run sync-videos with output filtering
                process = subprocess.Popen(
                    ["node", "--loader", "ts-node/esm", "scripts/sync-videos.ts", latest_video],
                    cwd=str(web_dir),
                    shell=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Filter and print output in real-time
                while True:
                    output = process.stdout.readline()
                    if output:
                        # Skip Node.js warnings and env var logs
                        if not any(skip in output for skip in [
                            "ExperimentalWarning",
                            "Environment variables loaded",
                            "--import",
                            "(Use `node --trace-warnings"
                        ]):
                            print(output.strip())
                    
                    # Check if process has finished
                    return_code = process.poll()
                    if return_code is not None:
                        if return_code == 0:
                            self.log.success("Successfully synced videos to server")
                            return True
                        else:
                            self.log.error("Error syncing videos - check console output above")
                            return False
                    
            except Exception as e:
                self.log.error(f"Error syncing videos: {str(e)}")
                return False
            
        except Exception as e:
            self.log.error(f"Error syncing video: {str(e)}")
            return False
    
    def _run_sketch(self, render_path: str, metadata: Dict = None) -> bool:
        """Run the Processing sketch"""
        try:
            script_path = self.config.base_path / "scripts" / "run_sketches.ps1"
            metadata_str = json.dumps(metadata) if metadata else "{}"
            
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
    
    def toggle_debug_mode(self):
        """Toggle debug mode and update all components"""
        self.debug_mode = not self.debug_mode
        self.log.set_debug(self.debug_mode)
        
        # Update debug mode for all components
        self.generator.log.set_debug(self.debug_mode)
        self.docs.log.set_debug(self.debug_mode)
        self.evolution.log.set_debug(self.debug_mode)
        self.cleaner.log.set_debug(self.debug_mode)
        self.test_runner.log.set_debug(self.debug_mode)
        
        status = "enabled" if self.debug_mode else "disabled"
        self.log.info(f"Debug mode {status}")
        
        # If enabling debug mode, log system info
        if self.debug_mode:
            self._log_system_info()
            
    def _log_system_info(self):
        """Log detailed system information when debug mode is enabled"""
        self.log.debug("\n=== SYSTEM INFORMATION ===")
        self.log.debug(f"Python version: {sys.version}")
        self.log.debug(f"Current working directory: {os.getcwd()}")
        self.log.debug(f"Environment variables: {list(os.environ.keys())}")
        
        # Log model configuration
        if hasattr(self.config, 'model_weights'):
            self.log.debug(f"Model weights: {self.config.model_weights}")
        
        # Log API keys (presence only, not values)
        api_keys = {
            'OPENAI_API_KEY': bool(os.getenv('OPENAI_API_KEY')),
            'ANTHROPIC_API_KEY': bool(os.getenv('ANTHROPIC_API_KEY'))
        }
        self.log.debug(f"API Keys present: {api_keys}")
        
        # Log current debug state
        self.log.debug(f"Debug mode: {self.debug_mode}")
        self.log.debug("==================\n")

    def _select_model(self):
        """Show model selection menu and handle choice"""
        print("\n" + "═" * 80)
        print("║ SELECT CREATIVE MODEL")
        print("═" * 80 + "\n")
        
        print("Available Models:")
        print("1. Random")
        print("2. O1")
        print("3. O1-mini")
        print("4. 4O")
        print("5. Claude 3.5 Sonnet")
        print("6. Claude 3 Opus")
        print("7. Flux (Static artwork)")
        print("8. Back to Main Menu")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-8): ").strip()
                
                if choice == "8":
                    return False
                
                if not choice.isdigit() or not (1 <= int(choice) <= 7):
                    print("Please enter a number between 1 and 8")
                    continue
                
                model_map = {
                    "1": "random",
                    "2": "o1",
                    "3": "o1-mini",
                    "4": "4o",
                    "5": "claude-3.5-sonnet",
                    "6": "claude-3-opus",
                    "7": "flux"
                }
                
                self.selected_model = model_map[choice]
                self.config.model_config['model_selection'] = self.selected_model
                
                # Initialize the appropriate generator
                if self.selected_model == "flux":
                    if self.generator is None:
                        self.generator = FluxGenerator(self.config, self.log)
                
                return True
                
            except ValueError:
                print("\nInvalid choice. Please try again.")

    def _select_random_techniques(self) -> List[Pattern]:
        """Select random techniques for generation"""
        return self.evolution.select_techniques()

    def _get_generator(self):
        """Get the appropriate generator based on selected model"""
        if self.config.model_config['model_selection'] == "flux":
            if not hasattr(self, 'flux_generator'):
                self.flux_generator = FluxGenerator(self.config, self.log)
            return self.flux_generator
        return self.generator

    def _show_variation_flow(self):
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
            # Check for PNG files to determine if static
            png_files = list(render.glob("*.png"))
            if png_files:
                # Try to get metadata - look for any json file matching pattern
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
                    
                    # Check if static or dynamic by looking for PNG files
                    png_files = list(selected_render.glob("*.png"))
                    if png_files:
                        # Find metadata file with timestamp
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
                if self.debug_mode:
                    import traceback
                    self.log.debug(traceback.format_exc())
                break

    def _create_static_variation(self, metadata_file: Path):
        """Create variation of a static Flux piece"""
        try:
            # Initialize Flux generator if needed
            if not hasattr(self, 'flux_generator') or self.flux_generator is None:
                from models.flux import FluxGenerator
                self.flux_generator = FluxGenerator(self.config, self.log)
            
            # Delegate to FluxGenerator's create_variation method
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
            
            # Get variation instructions
            print("\nEnter your variation instructions (e.g. 'use only squares instead of circles')")
            print("Or press Enter to keep original code and adjust interactively")
            variation_instructions = input("> ").strip()
            
            if variation_instructions:
                # Build prompt for code variation
                system_prompt = f"""You are helping create a variation of an existing Processing sketch.
Here is the original creative code:

{user_code}

The user wants these changes: {variation_instructions}

Create a new version that maintains the core style and functionality,
but incorporates the requested changes. Return only the code that goes
between the USER'S CREATIVE CODE markers."""

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
                    return
                
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
                        parent_patterns=[int(version)]
                    )
                    
                    # Score and save pattern
                    scores = self.generator.score_pattern(new_pattern)
                    new_pattern.update_scores(scores)
                    self.db.save_pattern(new_pattern)
                    
                    # Update documentation
                    self.docs.update(new_pattern)
            
        except Exception as e:
            self.log.error(f"Error creating dynamic variation: {e}")

if __name__ == "__main__":
    # Initialize without passing config
    prism = PRISM()
    prism.show_menu()
