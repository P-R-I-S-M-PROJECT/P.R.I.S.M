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

# Load environment variables
load_dotenv()

class PRISM:
    def __init__(self, config: Config):
        self.log = ArtLogger(debug_enabled=False)
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
            print("1. Run Continuous Generation")
            print("2. Cleanup System")
            print("3. Toggle Debug Mode")
            print("4. Test O1 Models")
            print("5. Test Claude Models")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                self.run_continuous()
            elif choice == "2":
                self.cleanup_system()
            elif choice == "3":
                self.log.set_debug(not self.log.debug_enabled)
                self.log.info(f"Debug mode {'enabled' if self.log.debug_enabled else 'disabled'}")
            elif choice == "4":
                self.test_runner.test_o1_models()
            elif choice == "5":
                self.test_runner.test_claude_models()
            elif choice == "6":
                self.log.title("Exiting System")
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def run_continuous(self):
        """Main loop for continuous generation"""
        self.log.info("Starting continuous automation...")
        try:
            while True:
                self.run_iteration()
                time.sleep(600)
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
            
            # Sync to server
            self._sync_to_server()
            
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
    
    def _sync_videos(self):
        """Sync videos to CDN"""
        try:
            self.log.info("Syncing video to server...")
            result = subprocess.run(
                ['node', 'web/scripts/sync-videos.ts'],
                capture_output=True,
                text=True
            )
            
            # Only pass the relevant output to the logger
            if result.returncode == 0:
                # Extract just the CDN verification part
                output_lines = result.stdout.split('\n')
                cdn_info = '\n'.join(line for line in output_lines 
                                   if 'CDN response' in line 
                                   or 'verification successful' in line
                                   or 'animation_v' in line)
                self.log.video_sync_complete(cdn_info)
            else:
                self.log.error(f"Video sync failed: {result.stderr}")
                
        except Exception as e:
            self.log.error(f"Error syncing videos: {e}")

if __name__ == "__main__":
    config = Config()
    prism = PRISM(config)
    prism.show_menu()
