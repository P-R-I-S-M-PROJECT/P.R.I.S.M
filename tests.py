from datetime import datetime
from models import Pattern
from logger import ArtLogger
from config import Config
from typing import List
import random
from pathlib import Path
import re

class TestRunner:
    def __init__(self, config: Config, generator, evolution, db):
        self.config = config
        self.generator = generator
        self.evolution = evolution
        self.db = db
        self.log = ArtLogger()

    def test_o1_models(self):
        """Test mode for O1 model generation"""
        self.log.title("O1 MODEL TEST MODE")
        try:
            while True:
                # Force config to use o1 model for testing
                self.config.set_model_selection('o1')
                
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
                
                # Create and score pattern
                pattern = Pattern(
                    version=next_version,
                    code=new_code,
                    timestamp=datetime.now(),
                    techniques=technique_names
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
                
                # Ask to continue
                if input("\nPress Enter to generate another, or 'q' to quit: ").lower() == 'q':
                    # Reset model selection to random before exiting
                    self.config.set_model_selection('random')
                    break
                
        except KeyboardInterrupt:
            # Reset model selection to random on interrupt
            self.config.set_model_selection('random')
            self.log.warning("Test mode stopped by user")

    def test_claude_models(self):
        """Test Claude model code generation"""
        self.log.title("CLAUDE MODEL TEST MODE")
        
        print("Available Claude Models:")
        print("1. Claude 3.5 Sonnet (Latest, Balanced)")
        print("2. Claude 3 Opus (Best Quality)")
        
        while True:
            try:
                choice = input("\nSelect model (1-2): ")
                if choice == "1":
                    model = "claude-3.5-sonnet"
                elif choice == "2":
                    model = "claude-3-opus"
                else:
                    print("Invalid choice. Please select 1 or 2.")
                    continue
                    
                self.log.info(f"Testing with {model}")
                
                # Force config to use claude model for testing
                self.config.set_model_selection(model)
                
                # Get techniques using evolution system
                techniques = self.evolution.select_techniques()
                if not techniques:
                    self.log.error("Failed to select techniques")
                    continue
                    
                # Convert numpy strings to regular strings
                technique_names = [str(t.name) for t in techniques]
                self.log.info(f"Creative approach: {technique_names}")
                
                # Generate new iteration using standard pipeline
                next_version = self.config.get_next_version()
                new_code = self.generator.generate_new_iteration(techniques, next_version)
                
                if not new_code:
                    self.log.error("Failed to generate code")
                    continue
                    
                # Create pattern object
                pattern = Pattern(
                    version=next_version,
                    code=new_code,
                    timestamp=datetime.now(),
                    techniques=technique_names
                )
                
                # Score pattern using generator's analyzer
                scores = self.generator.score_pattern(pattern)
                pattern.update_scores(scores)
                
                # Save pattern
                self.db.save_pattern(pattern)
                
                # Display scores
                self.log.pattern_score(pattern.score)
                self.log.info(f"Innovation: {pattern.innovation_score:.2f}, "
                             f"Aesthetic: {pattern.aesthetic_score:.2f}, "
                             f"Complexity: {pattern.mathematical_complexity:.2f}")
                
                # Ask to continue
                if input("\nPress Enter to generate another, or 'q' to quit: ").lower() == 'q':
                    break
                
            except Exception as e:
                self.log.error(f"Error in test mode: {str(e)}")
                if self.log.debug_enabled:
                    import traceback
                    self.log.debug(traceback.format_exc())
                    
            finally:
                # Reset model selection to random
                self.config.set_model_selection('random')

    def _get_random_techniques(self, count: int = 1) -> List[str]:
        """Get random techniques for testing"""
        all_techniques = []
        for category in ['geometry', 'motion', 'patterns']:
            if category in self.config.technique_categories:
                all_techniques.extend(self.config.technique_categories[category])
                
        return random.sample(all_techniques, min(count, len(all_techniques))) 

    def _run_sketch(self, version: int):
        """Run the Processing sketch for the given version"""
        try:
            # Get paths
            render_path = self.config.base_path / "renders" / f"render_v{version}"
            sketch_path = render_path / "sketch.pde"
            template_path = self.config.base_path / "auto.pde"
            
            # Read template and sketch code
            with open(template_path, 'r') as f:
                template = f.read()
            with open(sketch_path, 'r') as f:
                sketch_code = f.read()
                
            # Insert sketch code into template
            full_code = template.replace("// YOUR CREATIVE CODE GOES HERE", sketch_code)
            
            # Save combined code
            with open(sketch_path, 'w') as f:
                f.write(full_code)
            
            # Run Processing sketch using full path
            self.log.info(f"Running sketch v{version}...")
            processing_path = r"C:\Program Files\processing-4.3\processing-java.exe"  # Adjust this path
            processing_cmd = f'"{processing_path}" --sketch="{render_path}" --run'
            
            import subprocess
            result = subprocess.run(processing_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log.error(f"Error running sketch: {result.stderr}")
                self.log.debug(f"Command output: {result.stdout}")
            else:
                self.log.success("Sketch completed successfully")
                
        except Exception as e:
            self.log.error(f"Error running sketch: {str(e)}")
            self.log.debug(f"Error type: {type(e)}")
            self.log.debug(f"Error details: {dir(e)}")
            raise 