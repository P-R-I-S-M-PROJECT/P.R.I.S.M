import random
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from logger import ArtLogger
from config import Config
from models import Pattern
import json
import subprocess
import time

class DynamicBuilder:
    def __init__(self, config: Config, log: ArtLogger, generator, db):
        self.config = config
        self.log = log
        self.generator = generator
        self.db = db
        self.current_complexity = 0.7
        self.current_innovation = 0.5
        self.selected_techniques = []
        self.selected_model = None
        
    def show_creation_wizard(self, model_name: str = None):
        """Guide user through creating a dynamic artwork"""
        if model_name:
            self.selected_model = model_name
        else:
            self._choose_model()
            
        print("\n════════════════════════════════════════════════════════════════════════════════")
        print("║ DYNAMIC ART WIZARD")
        print(f"║ Using Model: {self.selected_model}")
        print("════════════════════════════════════════════════════════════════════════════════\n")
        
        # Get any custom guidelines first
        print("\nDo you have any specific requirements or guidelines for this piece?")
        print("(e.g., 'spell out PRISM', 'use only squares', 'make it look like a galaxy')")
        print("Press Enter to skip or input your guidelines:")
        custom_guidelines = input().strip()
        
        # If they provided guidelines but want to skip wizard, ask if they want to skip
        if custom_guidelines:
            print("\nWould you like to:")
            print("1. Use guidelines with wizard (recommended)")
            print("2. Use only guidelines (skip wizard)")
            choice = input("\nEnter choice (1-2) or press Enter for option 1: ").strip()
            
            if choice == "2":
                # Build prompt with just guidelines
                prompt = self._build_creative_prompt(
                    motion_style="",
                    shape_elements="",
                    color_approach="",
                    pattern_type="",
                    custom_guidelines=custom_guidelines
                )
                return self._generate_artwork(prompt)
        
        # Step 1: Choose base techniques
        print("\nChoose base mathematical techniques (press Enter at each step to skip):")
        self._choose_base_techniques()
        
        # Step 2: Choose motion style
        motion_style = self._choose_motion_style()
        
        # Step 3: Choose shape elements
        shape_elements = self._choose_shape_elements()
        
        # Step 4: Choose color approach
        color_approach = self._choose_color_approach()
        
        # Step 5: Choose pattern type
        pattern_type = self._choose_pattern_type()
        
        # Build the creative prompt
        prompt = self._build_creative_prompt(
            motion_style,
            shape_elements,
            color_approach,
            pattern_type,
            custom_guidelines=custom_guidelines
        )
        
        # Generate the artwork
        return self._generate_artwork(prompt)
    
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
        print("1. O1 (Standard)")
        print("2. O1-mini (Fast)")
        print("3. 4O (Enhanced)")
        print("4. Claude 3.5 Sonnet")
        print("5. Claude 3 Opus")
        
        while True:
            choice = input("\nEnter choice (1-5): ")
            if choice in models:
                self.selected_model = models[choice]
                break
            print("Invalid choice")
    
    def _choose_base_techniques(self):
        """Let user choose base mathematical techniques"""
        categories = {
            'geometry': self.config.technique_categories['geometry'],
            'motion': self.config.technique_categories['motion'],
            'patterns': self.config.technique_categories['patterns']
        }
        
        for category, techniques in categories.items():
            print(f"\n{category.title()} Techniques:")
            for i, technique in enumerate(techniques, 1):
                print(f"{i}. {technique}")
            
            while True:
                try:
                    choices = input(f"\nSelect {category} techniques (comma-separated numbers, 0 or Enter to skip): ")
                    if not choices.strip() or choices.strip() == "0":
                        break
                        
                    indices = [int(x.strip()) - 1 for x in choices.split(",")]
                    selected = [techniques[i] for i in indices if 0 <= i < len(techniques)]
                    self.selected_techniques.extend(selected)
                    break
                except (ValueError, IndexError):
                    print("Please enter valid numbers")
        
        if self.selected_techniques:
            print(f"\nSelected techniques: {', '.join(self.selected_techniques)}")
        else:
            print("\nNo specific techniques selected - using AI's creative judgment")
    
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
        
        print("\nChoose motion style (press Enter to skip):")
        for i, style in enumerate(styles, 1):
            print(f"{i}. {style}")
            
        while True:
            try:
                choice = input("\nEnter choice (1-8 or press Enter to skip): ").strip()
                if not choice:  # Allow empty input to skip
                    return ""
                choice = int(choice)
                if 1 <= choice <= len(styles):
                    return styles[choice - 1]
                print("Invalid choice")
            except ValueError:
                print("Please enter a number or press Enter to skip")
    
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
        
        print("\nChoose primary shapes (press Enter to skip):")
        for i, shape in enumerate(shapes, 1):
            print(f"{i}. {shape}")
            
        while True:
            try:
                choice = input("\nEnter choice (1-8 or press Enter to skip): ").strip()
                if not choice:  # Allow empty input to skip
                    return ""
                choice = int(choice)
                if 1 <= choice <= len(shapes):
                    return shapes[choice - 1]
                print("Invalid choice")
            except ValueError:
                print("Please enter a number or press Enter to skip")
    
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
        
        print("\nChoose color approach (press Enter to skip):")
        for i, approach in enumerate(approaches, 1):
            print(f"{i}. {approach}")
            
        while True:
            try:
                choice = input("\nEnter choice (1-8 or press Enter to skip): ").strip()
                if not choice:  # Allow empty input to skip
                    return ""
                choice = int(choice)
                if 1 <= choice <= len(approaches):
                    if choice == 8:
                        custom = input("\nDescribe your custom color scheme (or press Enter to skip): ").strip()
                        return custom if custom else ""
                    return approaches[choice - 1]
                print("Invalid choice")
            except ValueError:
                print("Please enter a number or press Enter to skip")
    
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
        
        print("\nChoose pattern type (press Enter to skip):")
        for i, pattern in enumerate(patterns, 1):
            print(f"{i}. {pattern}")
            
        while True:
            try:
                choice = input("\nEnter choice (1-8 or press Enter to skip): ").strip()
                if not choice:  # Allow empty input to skip
                    return ""
                choice = int(choice)
                if 1 <= choice <= len(patterns):
                    return patterns[choice - 1]
                print("Invalid choice")
            except ValueError:
                print("Please enter a number or press Enter to skip")
    
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
            prompt["custom_guidelines"] = custom_guidelines
            
        return prompt
    
    def _generate_artwork(self, prompt_data: dict) -> Optional[Pattern]:
        """Generate the artwork using the built prompt"""
        try:
            # Get next version
            next_version = self.config.get_next_version()
            
            # Select appropriate generator based on model
            if self.selected_model in ['o1', 'o1-mini']:
                generator = self.generator.o1_generator
                generator.current_model = self.selected_model
            elif self.selected_model == '4o':
                generator = self.generator.o4_generator
            elif self.selected_model in ['claude-3.5-sonnet', 'claude-3-opus']:
                generator = self.generator.claude_generator
                generator.current_model = self.selected_model
            else:
                self.log.error(f"Invalid model selected: {self.selected_model}")
                return None
            
            # Add retry logic for generation
            max_retries = 3
            for attempt in range(max_retries):
                if attempt > 0:
                    self.log.info(f"Generation attempt {attempt+1}/{max_retries}")
                
                # Generate the code
                code = generator.generate_code(prompt_data)
                if not code:
                    if attempt < max_retries - 1:
                        continue
                    self.log.error("Failed to generate valid code")
                    return None
                
                # Build the template
                final_code = generator.build_processing_template(code, next_version)
                
                # Save the code
                with open(self.config.paths['template'], 'w') as f:
                    f.write(final_code)
                
                # Run the sketch
                render_path = f"render_v{next_version}"
                success = self._run_sketch(render_path)
                
                if success:
                    # Create pattern object
                    pattern = Pattern(
                        version=next_version,
                        code=code,
                        timestamp=datetime.now(),
                        techniques=self.selected_techniques
                    )
                    
                    # Score and save pattern
                    scores = self.generator.score_pattern(pattern)
                    pattern.update_scores(scores)
                    self.db.save_pattern(pattern)
                    
                    self.log.success(f"Successfully created dynamic artwork using {self.selected_model}")
                    return pattern
                
                if attempt < max_retries - 1:
                    continue
                
                self.log.error("Failed to run sketch")
                return None
            
            return None
            
        except Exception as e:
            self.log.error(f"Error generating artwork: {e}")
            if self.config.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())
            return None

    def _run_sketch(self, render_path: str) -> bool:
        """Run the Processing sketch and wait for completion"""
        try:
            # Create render directory
            Path(render_path).mkdir(parents=True, exist_ok=True)
            
            # Use the generator's run_sketch method
            success, error = self.generator.run_sketch(Path(render_path))
            if not success and error:
                self.log.error(f"Sketch error: {error}")
            return success
            
        except Exception as e:
            self.log.error(f"Error running sketch: {e}")
            if self.config.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())
            return False 