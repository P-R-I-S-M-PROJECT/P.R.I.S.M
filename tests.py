from datetime import datetime
from models import Pattern
from logger import ArtLogger
from config import Config

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
        """Test mode for Claude model generation"""
        self.log.title("CLAUDE MODEL TEST MODE")
        try:
            # Let user choose which Claude model to test
            print("\nAvailable Claude Models:")
            print("1. Claude 3.5 Sonnet (Balanced)")
            print("2. Claude 3 Opus (Best Quality)")
            choice = input("\nSelect model (1-2): ")
            
            if choice == "1":
                model = 'claude-3.5-sonnet'
            elif choice == "2":
                model = 'claude-3-opus'
            else:
                self.log.error("Invalid choice")
                return
            
            self.log.info(f"Testing with {model}")
            
            while True:
                # Force config to use selected Claude model for testing
                self.config.set_model_selection(model)
                
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