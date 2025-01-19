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
from models import Pattern
from tests import TestRunner
import json
from typing import Dict
import sys

# Load environment variables
load_dotenv()

class PRISM:
    def __init__(self, config: Config):
        self.debug_mode = False
        self.log = ArtLogger(debug_enabled=self.debug_mode)
        self.config = config
        self.db = config.db_manager
        
        # Initialize components with shared logger
        self.generator = ProcessingGenerator(config, self.log)
        self.docs = DocumentationManager(config, self.log)
        self.evolution = PatternEvolution(config, self.log)
        self.cleaner = SystemCleaner(config, self.log)
        self.test_runner = TestRunner(config, self.generator, self.evolution, self.db)
        
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
            print("1. Generate Patterns")
            print("2. Cleanup System")
            print("3. Toggle Debug Mode")
            print("4. Test O1 Models")
            print("5. Test Claude Models")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                self._show_generation_menu()
            elif choice == "2":
                self.cleanup_system()
            elif choice == "3":
                self.toggle_debug_mode()
            elif choice == "4":
                self.test_runner.test_o1_models()
            elif choice == "5":
                self.test_runner.test_claude_models()
            elif choice == "6":
                self.log.title("Exiting System")
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def _show_generation_menu(self):
        """Show generation options menu"""
        while True:
            self.log.title("PATTERN GENERATION OPTIONS")
            print("\nGeneration Mode:")
            print("1. Single Pattern")
            print("2. Multiple Patterns")
            print("3. Continuous Generation")
            print("4. Select Model")
            print("5. Back to Main Menu")
            
            current_model = self.config.model_config['model_selection']
            print(f"\nCurrent Model: {current_model}")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == "1":
                self.run_iteration()
                input("\nPress Enter to continue...")
            elif choice == "2":
                try:
                    count = int(input("How many patterns to generate? "))
                    if count > 0:
                        for i in range(count):
                            self.log.info(f"\nGenerating pattern {i+1} of {count}")
                            self.run_iteration()
                        input("\nGeneration complete. Press Enter to continue...")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "3":
                try:
                    interval = int(input("Enter interval between generations in seconds (min 60): "))
                    if interval < 60:
                        print("Interval must be at least 60 seconds")
                        continue
                    self.run_continuous(interval)
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "4":
                self._show_model_selection_menu()
            elif choice == "5":
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def _show_model_selection_menu(self):
        """Show model selection menu"""
        while True:
            self.log.title("MODEL SELECTION")
            print("\nAvailable Models:")
            print("1. Random")
            print("2. O1")
            print("3. O1-mini")
            print("4. 4O")
            print("5. Claude 3.5 Sonnet")
            print("6. Claude 3 Opus")
            print("7. Flux")
            print("8. Back to Generation Menu")
            
            current_model = self.config.model_config['model_selection']
            print(f"\nCurrent Model: {current_model}")
            
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
                self.config.set_model_selection(model_map[choice])
                print(f"\nModel set to: {model_map[choice]}")
                input("Press Enter to continue...")
                return True  # Return to generation menu
            elif choice == "8":
                return True  # Return to generation menu
            else:
                print("\nInvalid choice. Please try again.")
    
    def run_continuous(self, interval: int = 600):
        """Run continuous generation with specified interval"""
        self.log.info(f"Starting continuous automation (interval: {interval}s)...")
        try:
            while True:
                self.run_iteration()
                self.log.info(f"Waiting {interval} seconds until next generation...")
                time.sleep(interval)
        except KeyboardInterrupt:
            self.log.warning("Stopping automation...")
    
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
            
            # For Flux model, let user select variant
            if current_model == "flux":
                print("\nSelect Flux model variant:")
                variants = self.config.static_image_config['models']['flux']['variants']
                for i, (name, info) in enumerate(variants.items(), 1):
                    print(f"{i}. {name.upper()} - {info['description']}")
                
                while True:
                    try:
                        choice = input("\nEnter choice (1-3): ").strip()
                        if not choice.isdigit() or not (1 <= int(choice) <= 3):
                            print("Please enter a number between 1 and 3")
                            continue
                        variant_names = list(variants.keys())
                        selected_variant = variant_names[int(choice)-1]
                        self.config.static_image_config['models']['flux']['selected_variant'] = selected_variant
                        break
                    except (ValueError, IndexError):
                        print("Invalid selection, please try again")
            
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

if __name__ == "__main__":
    config = Config()
    prism = PRISM(config)
    prism.show_menu()
