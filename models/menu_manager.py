from logger import ArtLogger
from config import Config
from models.flux import FluxGenerator
from models.dynamic_builder import DynamicBuilder

class MenuManager:
    def __init__(self, config: Config, log: ArtLogger, prism_instance):
        self.config = config
        self.log = log
        self.prism = prism_instance
        self.selected_model = None
        self.dynamic_builder = None
        
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
                self.show_creation_flow()
            elif choice == "2":
                self.prism.cleanup_system()
            elif choice == "3":
                self.prism.toggle_debug_mode()
            elif choice == "4":
                self.prism.test_runner.test_o1_models()
            elif choice == "5":
                self.prism.test_runner.test_claude_models()
            elif choice == "6":
                self.prism.variation_manager.show_variation_flow()
            elif choice == "7":
                self.log.title("Exiting Studio")
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def show_creation_flow(self):
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
        
        if choice == "8":
            return
            
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
                if self.prism.flux_generator is None:
                    self.prism.flux_generator = FluxGenerator(self.config, self.log)
                self.show_flux_menu()
            else:
                self.show_animated_model_menu()
        else:
            print("\nInvalid choice. Please try again.")
    
    def show_animated_model_menu(self):
        """Show menu for animated model creation"""
        while True:
            self.log.title("CREATION MODE")
            current_model = self.config.model_config['model_selection']
            print(f"\nCurrent Model: {current_model}")
            
            print("\nCreation Mode:")
            print("1. Guided Creation (Wizard)")
            print("2. Automated Evolution")
            print("3. Back to Model Selection")
            print("4. Back to Main Menu")
            
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == "1":  # Wizard Mode
                if self.dynamic_builder is None:
                    self.dynamic_builder = DynamicBuilder(
                        self.config,
                        self.log,
                        self.prism.generator,
                        self.prism.db
                    )
                self.show_wizard_mode_menu(current_model)
                input("\nPress Enter to continue...")
            elif choice == "2":  # Automated Evolution
                self.show_generation_menu()
            elif choice == "3":
                self.show_creation_flow()
                break
            elif choice == "4":
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def show_wizard_mode_menu(self, current_model):
        """Show wizard mode selection menu"""
        while True:
            self.log.title("WIZARD MODE")
            print(f"\nCurrent Model: {current_model}")
            
            print("\nSelect Mode:")
            print("1. Standard Mode (Direct Creation)")
            print("2. Refinement Mode (Iterative Creation)")
            print("3. Back to Creation Mode")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":  # Standard Mode
                self.show_standard_mode(current_model)
                break
            elif choice == "2":  # Refinement Mode
                self.show_refinement_mode(current_model)
                break
            elif choice == "3":
                break
            else:
                print("\nInvalid choice. Please try again.")

    def show_standard_mode(self, current_model):
        """Show standard mode interface with batch creation option"""
        while True:
            self.log.title("STANDARD MODE")
            print(f"\nCurrent Model: {current_model}")
            
            print("\nCreation Options:")
            print("1. Create Single Piece")
            print("2. Create Multiple Pieces")
            print("3. Back to Wizard Mode")
            
            choice = input("\nEnter your choice (1-3): ")
            
            if choice == "1":  # Single piece
                pattern = self.dynamic_builder.show_creation_wizard(model_name=current_model)
                if pattern:
                    self.log.success("Pattern created successfully")
                break
            elif choice == "2":  # Multiple pieces
                try:
                    count = int(input("\nHow many pieces would you like to create? (1-10): "))
                    if 1 <= count <= 10:
                        # Get settings once and store them
                        self.log.info(f"\nSetting up creation parameters for {count} pieces...")
                        settings = self.dynamic_builder.get_creation_settings(model_name=current_model)
                        
                        # Use stored settings for each piece
                        for i in range(count):
                            self.log.info(f"\nCreating piece {i+1} of {count}")
                            pattern = self.dynamic_builder.create_with_settings(settings)
                            if pattern:
                                self.log.success(f"Pattern {i+1} created successfully")
                            else:
                                self.log.error(f"Failed to create pattern {i+1}")
                        break
                    else:
                        print("Please enter a number between 1 and 10")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "3":
                break
            else:
                print("\nInvalid choice. Please try again.")

    def show_refinement_mode(self, current_model):
        """Show refinement mode interface"""
        while True:
            self.log.title("REFINEMENT MODE")
            print(f"\nCurrent Model: {current_model}")
            
            # Create initial piece
            pattern = self.dynamic_builder.show_creation_wizard(model_name=current_model)
            if pattern is None:
                print("\nFailed to create initial piece")
                break
                
            while True:
                print("\nRefinement Options:")
                print("1. Keep this version")
                print("2. Modify and try again")
                print("3. Start over")
                print("4. Back to Wizard Mode")
                
                choice = input("\nEnter your choice (1-4): ")
                
                if choice == "1":  # Keep version
                    self.log.success("Pattern saved successfully")
                    return
                elif choice == "2":  # Modify
                    # Create variation of current pattern
                    render_dir = self.config.base_path / f"renders/render_v{pattern.version}"
                    if render_dir.exists():
                        self.prism.variation_manager._create_dynamic_variation(render_dir)
                    else:
                        self.log.error(f"Could not find render directory: {render_dir}")
                elif choice == "3":  # Start over
                    break  # Break inner loop to create new pattern
                elif choice == "4":  # Back to menu
                    return
                else:
                    print("\nInvalid choice. Please try again.")

    def show_generation_menu(self):
        """Show automated generation options menu"""
        while True:
            self.log.title("AUTOMATED EVOLUTION")
            print("\nCreation Mode:")
            print("1. Single Creation")
            print("2. Multiple Pieces")
            print("3. Continuous Studio")
            print("4. Back to Creation Mode")
            print("5. Back to Model Selection")
            print("6. Back to Main Menu")
            
            current_model = self.config.model_config['model_selection']
            print(f"\nCurrent Model: {current_model}")
            
            choice = input("\nEnter your choice (1-6): ")
            
            if choice == "1":
                self.prism.run_iteration()
                input("\nPress Enter to continue...")
            elif choice == "2":
                try:
                    count = int(input("How many pieces to create? "))
                    if count > 0:
                        for i in range(count):
                            self.log.info(f"\nCreating piece {i+1} of {count}")
                            self.prism.run_iteration()
                        input("\nCreation complete. Press Enter to continue...")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "3":
                try:
                    interval = int(input("Enter interval between creations in seconds: "))
                    if interval <= 0:
                        print("Interval must be greater than 0 seconds")
                        continue
                    self.prism.run_continuous(interval)
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "4":
                self.show_animated_model_menu()
                break
            elif choice == "5":
                self.show_creation_flow()
                break
            elif choice == "6":
                break
            else:
                print("\nInvalid choice. Please try again.")

    def _build_creative_prompt(self, motion: str, shapes: str, colors: str, pattern: str, custom_guidelines: str = "") -> dict:
        """Build the creative prompt from selected options"""
        prompt = {
            "techniques": self.selected_techniques,
            "motion_style": motion,
            "shape_elements": shapes,
            "color_approach": colors,
            "pattern_type": pattern,
        }
        
        if custom_guidelines:
            # Check if this is a text-based requirement
            is_text_requirement = any(word in custom_guidelines.lower() for word in ['text', 'spell', 'word', 'letter'])
            
            if is_text_requirement:
                # Enhance the guideline to be more specific about shape-based approach
                enhanced_guideline = f"""Form text organically using the following approach:
• Use {shapes.lower() if shapes else 'geometric patterns'} to construct letter shapes
• Implement with PGraphics mask for precise boundaries
• Text should emerge from {pattern.lower() if pattern else 'dynamic patterns'}
• Animate smoothly with {motion.lower() if motion else 'fluid motion'}
• Original requirement: {custom_guidelines}"""
                prompt["custom_guidelines"] = enhanced_guideline
            else:
                prompt["custom_guidelines"] = custom_guidelines
            
        return prompt 