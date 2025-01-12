from datetime import datetime
from models import Pattern
from logger import ArtLogger
from config import Config
from typing import List
import random

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
        """Test Claude models by generating patterns"""
        print("\n" + "═" * 80)
        print("║ CLAUDE MODEL TEST MODE")
        print("═" * 80 + "\n")
        
        print("Available Claude Models:")
        print("1. Claude 3.5 Sonnet (Balanced)")
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
                
                # Get random techniques
                techniques = self._get_random_techniques()
                self.log.info(f"Creative approach: {techniques}")
                
                # Log test configuration
                self.log.debug("\n=== TEST CONFIGURATION ===")
                self.log.debug(f"Selected model: {model}")
                self.log.debug(f"Techniques: {techniques}")
                self.log.debug("==================\n")
                
                # Generate code
                code = self.generator.generate_with_model(model, techniques)
                if not code:
                    self.log.error("Failed to generate code")
                    continue
                    
                self.log.success("Code generated successfully")
                
                # Get next version by scanning renders directory
                version = self.config.update_version_from_renders()
                self.log.debug(f"Using version: v{version}")
                
                # Create render directory
                render_path = self.config.base_path / "renders" / f"render_v{version}"
                render_path.mkdir(parents=True, exist_ok=True)
                
                # Save code to file
                code_path = render_path / "sketch.pde"
                with open(code_path, "w") as f:
                    f.write(code)
                
                self.log.info(f"Code saved to {code_path}")
                self.log.info("Running sketch...")
                
                # Run the sketch
                self._run_sketch(version)
                
                # Ask to continue
                if not input("\nGenerate another? (y/n): ").lower().startswith('y'):
                    break
                    
            except Exception as e:
                self.log.error(f"Test error: {str(e)}")
                self.log.debug(f"Error type: {type(e)}")
                self.log.debug(f"Error details: {dir(e)}")
                if not input("\nTry again? (y/n): ").lower().startswith('y'):
                    break

    def _get_random_techniques(self, count: int = 1) -> List[str]:
        """Get random techniques for testing"""
        all_techniques = []
        for category in ['geometry', 'motion', 'patterns']:
            if category in self.config.technique_categories:
                all_techniques.extend(self.config.technique_categories[category])
                
        return random.sample(all_techniques, min(count, len(all_techniques))) 