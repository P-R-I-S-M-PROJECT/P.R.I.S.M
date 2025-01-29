import random
from typing import List, Dict, Optional, Tuple
from logger import ArtLogger
from config import Config

class CreationWizard:
    def __init__(self, config: Config, log: ArtLogger, menu_manager):
        self.config = config
        self.log = log
        self.menu_manager = menu_manager
        self.selected_techniques = []
        self.selected_model = None
        self.selected_illusions = []  # Store selected illusions for multiple generations
        self.selected_motion_styles = []  # Store selected motion styles
        self.selected_shapes = []  # Store selected shapes
        self.selected_colors = []  # Store selected color approaches
        self.selected_patterns = []  # Store selected pattern types
        
    def collect_settings(self, model_name: str = None) -> dict:
        """Collect all settings from the wizard"""
        if model_name:
            self.selected_model = model_name
        else:
            self._choose_model()
            
        print("\n════════════════════════════════════════════════════════════════════════════════")
        print("║ DYNAMIC ART WIZARD")
        print(f"║ Using Model: {self.selected_model}")
        print("════════════════════════════════════════════════════════════════════════════════\n")
        
        # Get creative mode and handle choices
        mode_choice = self.menu_manager._get_creative_mode()
        custom_guidelines = self._handle_creative_mode(mode_choice)
        
        # Collect technique selections
        self._collect_techniques()
        
        # Collect style preferences
        motion_style = self._choose_motion_style()
        shape_elements = self._choose_shape_elements()
        color_approach = self._choose_color_approach()
        pattern_type = self._choose_pattern_type()
        
        return {
            "model": self.selected_model,
            "techniques": self.selected_techniques,
            "motion_styles": self.selected_motion_styles,
            "shapes": self.selected_shapes,
            "colors": self.selected_colors,
            "patterns": self.selected_patterns,
            "custom_guidelines": custom_guidelines
        }
    
    def _handle_creative_mode(self, mode_choice: str) -> str:
        """Handle the selected creative mode and collect guidelines"""
        if not mode_choice:
            return ""
            
        if mode_choice == "1":  # Particle Systems
            return self._handle_particle_systems()
        elif mode_choice == "2":  # Geometric Transformations
            return self._handle_geometric_transformations()
        elif mode_choice == "3":  # Pattern Generation
            return self._handle_pattern_generation()
        elif mode_choice == "4":  # Text Art
            return self._handle_text_art()
        elif mode_choice == "5":  # Optical Illusions
            return self._handle_optical_illusions()
        elif mode_choice == "6":  # Custom Guidelines
            return self.menu_manager._get_custom_guidelines()
        return ""
    
    def _handle_particle_systems(self) -> str:
        """Handle particle system options"""
        print("\nParticle System Options:")
        print("1. Galaxy/Star system")
        print("2. Flocking/Swarming")
        print("3. Particle Attraction")
        print("4. Rain/Snow simulation")
        behavior = input("Choose particle behavior (1-4): ").strip()
        
        behaviors = {
            "1": "Create a galaxy-like system with stars orbiting a central point, using gravitational forces",
            "2": "Implement a flocking system where particles follow emergent swarm behavior",
            "3": "Design particles that attract/repel based on proximity and forces",
            "4": "Simulate natural phenomena with particles affected by wind and gravity"
        }
        guidelines = behaviors.get(behavior, behaviors["1"])
        return self._add_additional_guidelines(guidelines)
    
    def _handle_geometric_transformations(self) -> str:
        """Handle geometric transformation options"""
        print("\nGeometric Options:")
        print("1. Sacred Geometry")
        print("2. Tessellation")
        print("3. Fractal Growth")
        print("4. Shape Morphing")
        geometry = input("Choose geometric style (1-4): ").strip()
        
        geometries = {
            "1": "Transform between sacred geometry patterns (flower of life, metatron's cube, etc)",
            "2": "Create evolving tessellation patterns that fill the space",
            "3": "Generate recursive fractal patterns that grow and evolve",
            "4": "Morph between different geometric shapes smoothly"
        }
        guidelines = geometries.get(geometry, geometries["1"])
        return self._add_additional_guidelines(guidelines)
    
    def _handle_pattern_generation(self) -> str:
        """Handle pattern generation options"""
        print("\nPattern Options:")
        print("1. Reaction Diffusion")
        print("2. Cellular Automata")
        print("3. Flow Fields")
        print("4. Wave Patterns")
        pattern = input("Choose pattern type (1-4): ").strip()
        
        patterns = {
            "1": "Create organic patterns using reaction-diffusion algorithms",
            "2": "Generate evolving patterns using cellular automata rules",
            "3": "Design dynamic flow fields that guide particle movement",
            "4": "Create interference patterns using overlapping waves"
        }
        guidelines = patterns.get(pattern, patterns["1"])
        return self._add_additional_guidelines(guidelines)
    
    def _handle_text_art(self) -> str:
        """Handle text art options"""
        print("\nWhat text would you like to create? (e.g. 'PRISM', 'Hello', etc.)")
        desired_text = input().strip() or "PRISM"  # Default to PRISM if empty
        
        print("\nWould you like to add any additional instructions? (e.g. 'only vertical motion', 'use specific colors', etc.)")
        print("Press Enter to skip")
        extra_instructions = input("> ").strip()
        
        print("\nText Art Options:")
        print("1. Particle Text")
        print("2. Pattern-Filled Text")
        print("3. Emergent Text")
        print("4. Morphing Text")
        print("\nEnter choice (1-4) or press Enter to let AI choose: ")
        text_style = input().strip()
        
        text_styles = {
            "1": f"Create text '{desired_text}' using dynamic particle systems that assemble and flow",
            "2": f"Create text '{desired_text}' filled with intricate patterns and motion",
            "3": f"Create text '{desired_text}' that emerges from underlying patterns",
            "4": f"Create text '{desired_text}' through transforming flowing shapes that morph"
        }
        guidelines = text_styles.get(text_style, f"Create text '{desired_text}' through shape-based patterns and dynamic motion")
        
        if extra_instructions:
            guidelines += f". Additional Requirements: {extra_instructions}"
        return guidelines
    
    def _handle_optical_illusions(self) -> str:
        """Handle optical illusion options"""
        result = self.menu_manager._get_illusion_choices()
        if not result:
            return "Create a dynamic optical illusion using any suitable technique. Choose the most effective approach to create a compelling visual effect. Focus on strong perceptual impact and smooth execution."
            
        self.selected_illusions, categories = result
        if not self.selected_illusions:
            cat_names = [self.menu_manager.illusion_types[c]['name'] for c in categories]
            guidelines = f"Create a dynamic optical illusion combining elements from the following categories: {', '.join(cat_names)}. "
            guidelines += "Choose the most effective techniques to create compelling visual effects. "
            guidelines += "Focus on strong perceptual impact and smooth execution."
            return self._add_additional_guidelines(guidelines)
            
        _, chosen_illusion = random.choice(self.selected_illusions)
        guidelines = f"Create a dynamic optical illusion using the {chosen_illusion.lower()} technique. "
        guidelines += "Focus on creating a strong visual effect that challenges perception. "
        guidelines += "Ensure the illusion is clear and effective, with smooth transitions and proper timing for maximum impact."
        return self._add_additional_guidelines(guidelines)
    
    def _add_additional_guidelines(self, base_guidelines: str) -> str:
        """Add additional user guidelines to base guidelines"""
        print("\nWould you like to add any additional instructions? (e.g. specific colors, motion constraints, etc.)")
        print("Press Enter to skip")
        additional = input("> ").strip()
        if additional:
            return f"{base_guidelines}. Additional Requirements: {additional}"
        return base_guidelines
    
    def _choose_model(self):
        """Let user choose which model to use"""
        models = {
            "1": "o1",
            "2": "o1-mini",
            "3": "4o",
            "4": "claude-3.5-sonnet",
            "5": "claude-3-opus"
        }
        
        print("\nChoose Model:")
        print("1. O1")
        print("2. O1-mini")
        print("3. 4O")
        print("4. Claude 3.5 Sonnet")
        print("5. Claude 3 Opus")
        
        while True:
            choice = input("\nEnter choice (1-5): ")
            if choice in models:
                self.selected_model = models[choice]
                break
            print("Invalid choice")
    
    def _parse_range_selection(self, selection: str, max_value: int) -> list:
        """Parse a range selection string into a list of integers"""
        if not selection.strip() or selection.lower() == "all":
            return list(range(max_value))
            
        selected = set()
        parts = selection.split(",")
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            try:
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    if 1 <= start <= end <= max_value:
                        selected.update(range(start-1, end))
                else:
                    num = int(part)
                    if 1 <= num <= max_value:
                        selected.add(num-1)
            except ValueError:
                continue
                
        return sorted(list(selected))
    
    def _choose_motion_style(self) -> str:
        """Choose the overall motion style"""
        styles = [
            "Fluid and organic",
            "Geometric and precise",
            "Chaotic and energetic",
            "Smooth and minimal",
            "Wave-like and flowing",
            "Pulsing and rhythmic",
            "Spiral and circular",
            "Random and unpredictable"
        ]
        
        print("\nChoose motion style:")
        print("Format: single number, list (1,2,3), range (1-3), 'all', or Enter to skip")
        
        for i, style in enumerate(styles, 1):
            print(f"{i}. {style}")
            
        choice = input("\nEnter selection: ").strip()
        if not choice:
            return ""
            
        indices = self._parse_range_selection(choice, len(styles))
        if indices:
            self.selected_motion_styles = [styles[i] for i in indices]
            return random.choice(self.selected_motion_styles)
        return ""
    
    def _choose_shape_elements(self) -> str:
        """Choose primary shape elements"""
        shapes = [
            "Circles and dots",
            "Squares and rectangles",
            "Triangles and polygons",
            "Lines and curves",
            "Points and particles",
            "Organic shapes",
            "Mixed geometry",
            "Abstract forms"
        ]
        
        print("\nChoose primary shapes:")
        print("Format: single number, list (1,2,3), range (1-3), 'all', or Enter to skip")
        
        for i, shape in enumerate(shapes, 1):
            print(f"{i}. {shape}")
            
        choice = input("\nEnter selection: ").strip()
        if not choice:
            return ""
            
        indices = self._parse_range_selection(choice, len(shapes))
        if indices:
            self.selected_shapes = [shapes[i] for i in indices]
            return random.choice(self.selected_shapes)
        return ""
    
    def _choose_color_approach(self) -> str:
        """Choose color scheme approach"""
        approaches = [
            "Monochromatic harmony",
            "Complementary contrasts",
            "Rainbow transitions",
            "Grayscale patterns",
            "Warm color palette",
            "Cool color palette",
            "High contrast black/white",
            "Custom color scheme"
        ]
        
        print("\nChoose color approach:")
        print("Format: single number, list (1,2,3), range (1-3), 'all', or Enter to skip")
        
        for i, approach in enumerate(approaches, 1):
            print(f"{i}. {approach}")
            
        choice = input("\nEnter selection: ").strip()
        if not choice:
            return ""
            
        indices = self._parse_range_selection(choice, len(approaches))
        if indices:
            self.selected_colors = [approaches[i] for i in indices]
            selected_approach = random.choice(self.selected_colors)
            if selected_approach == "Custom color scheme":
                custom = input("\nDescribe your custom color scheme (or press Enter to skip): ").strip()
                return custom if custom else ""
            return selected_approach
        return ""
    
    def _choose_pattern_type(self) -> str:
        """Choose overall pattern type"""
        patterns = [
            "Geometric patterns",
            "Organic patterns",
            "Recursive forms",
            "Fractal-based",
            "Symmetrical design",
            "Random distribution",
            "Grid-based layout",
            "Flow field patterns"
        ]
        
        print("\nChoose pattern type:")
        print("Format: single number, list (1,2,3), range (1-3), 'all', or Enter to skip")
        
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. {pattern}")
            
        choice = input("\nEnter selection: ").strip()
        if not choice:
            return ""
            
        indices = self._parse_range_selection(choice, len(patterns))
        if indices:
            self.selected_patterns = [patterns[i] for i in indices]
            return random.choice(self.selected_patterns)
        return ""
    
    def _collect_techniques(self):
        """Collect technique selections from user"""
        print("\nChoose base mathematical techniques")
        print("---------------------------")
        print("You can select specific techniques for each category, or press Enter to skip.")
        print("Format: single number, list (1,2,3), range (1-3), 'all', or Enter to skip")
        print("\nIf you skip all categories, the AI will intelligently select techniques based on:")
        print("• Your custom guidelines and creative direction")
        print("• Historical performance data")
        print("• Technique synergy patterns")
        print("• The chosen creative mode (static vs. dynamic)\n")
        
        categories = {
            'geometry': self.config.technique_categories['geometry'],
            'motion': self.config.technique_categories['motion'],
            'patterns': self.config.technique_categories['patterns']
        }
            
        for category, techniques in categories.items():
            print(f"\n{category.title()} Techniques:")
            for i, technique in enumerate(techniques, 1):
                print(f"{i}. {technique}")
            
            choices = input(f"\nSelect {category} techniques: ").strip()
            if choices:
                indices = self._parse_range_selection(choices, len(techniques))
                selected = [techniques[i] for i in indices]
                self.selected_techniques.extend(selected)
        
        if self.selected_techniques:
            print(f"\nSelected techniques: {', '.join(self.selected_techniques)}")
        else:
            print("\nNo specific techniques selected - AI will analyze your requirements and select optimal techniques") 