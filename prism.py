import os
import time
import subprocess
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
from models.variation_manager import VariationManager
from models.menu_manager import MenuManager
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
        
        # Initialize components with shared logger
        self.generator = ProcessingGenerator(self.config, self.log)
        self.docs = DocumentationManager(self.config, self.log)
        self.evolution = PatternEvolution(self.config, self.log)
        self.cleaner = SystemCleaner(self.config, self.log)
        self.test_runner = TestRunner(self.config, self.generator, self.evolution, self.db)
        self.variation_manager = VariationManager(self.config, self.log, self.generator, self.db)
        self.menu_manager = MenuManager(self.config, self.log, self)
        
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
        self.menu_manager.show_menu()
    
    def run_continuous(self, interval: int):
        """Run continuous pattern generation with specified interval"""
        self.log.info(f"Starting continuous automation (interval: {interval}s)...")
        
        try:
            while True:
                print("\n" + "═" * 80)
                print("║ NEW ITERATION")
                print("═" * 80)
                
                # For Flux model, use wizard
                if self.selected_model == "flux":
                    self.flux_generator.generate_with_ai()  # No prompt - will trigger wizard
                else:
                    # Generate creative approach for other models
                    techniques = self._select_random_techniques()
                    technique_names = [t.name for t in techniques]
                    self.log.info(f"Creative approach: {', '.join(technique_names)}")
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
            # Log which model we're using
            current_model = self.config.model_config['model_selection']
            self.log.info(f"Using model: {current_model}")
            
            # For Flux model, initialize if needed and use wizard
            if current_model == "flux":
                if self.flux_generator is None:
                    self.flux_generator = FluxGenerator(self.config, self.log)
                self.flux_generator.generate_with_ai()  # No prompt - will trigger wizard
                return
            
            # For other models, get creative direction
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

    def _select_random_techniques(self) -> List[Pattern]:
        """Select random techniques for generation"""
        return self.evolution.select_techniques()

if __name__ == "__main__":
    # Initialize without passing config
    prism = PRISM()
    prism.show_menu()
