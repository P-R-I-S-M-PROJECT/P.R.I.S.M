from logger import ArtLogger
from config import Config
from models.flux import FluxGenerator

class MenuManager:
    def __init__(self, config: Config, log: ArtLogger, prism_instance):
        self.config = config
        self.log = log
        self.prism = prism_instance
        self.selected_model = None
        
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
            
            self.show_generation_menu()
        elif choice == "8":
            return
        else:
            print("\nInvalid choice. Please try again.")
    
    def show_generation_menu(self):
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
                self.show_creation_flow()
                break
            elif choice == "5":
                break
            else:
                print("\nInvalid choice. Please try again.") 