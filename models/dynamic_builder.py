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
import re

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
        self.selected_illusions = []  # Store selected illusions for multiple generations
        self.selected_motion_styles = []  # Store selected motion styles
        self.selected_shapes = []  # Store selected shapes
        self.selected_colors = []  # Store selected color approaches
        self.selected_patterns = []  # Store selected pattern types
        
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
        print("\nChoose Creative Mode:")
        print("1. Particle Systems (physics-based animations)")
        print("2. Geometric Transformations (shape morphing)")
        print("3. Pattern Generation (recursive/emergent)")
        print("4. Text Art (shape-based/organic)")
        print("5. Optical Illusions & Visual Puzzles")
        print("6. Custom Guidelines")
        print("\nEnter choice (1-6) or press Enter to skip: ")
        mode_choice = input().strip()
        
        custom_guidelines = ""
        if mode_choice:
            if mode_choice == "1":  # Particle Systems
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
                custom_guidelines = behaviors.get(behavior, behaviors["1"])
                
            elif mode_choice == "2":  # Geometric Transformations
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
                custom_guidelines = geometries.get(geometry, geometries["1"])
                
            elif mode_choice == "3":  # Pattern Generation
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
                custom_guidelines = patterns.get(pattern, patterns["1"])
                
            elif mode_choice == "4":  # Text Art
                print("\nWhat text would you like to create? (e.g. 'PRISM', 'Hello', etc.)")
                desired_text = input().strip() or "PRISM"  # Default to PRISM if empty
                
                # NEW: Ask for additional instructions
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
                custom_guidelines = text_styles.get(text_style, f"Create text '{desired_text}' through shape-based patterns and dynamic motion")
                
                # Append extra instructions if provided
                if extra_instructions:
                    custom_guidelines += f". Additional Requirements: {extra_instructions}"
            
            elif mode_choice == "5":  # Optical Illusions
                print("\nOptical Illusion Categories:")
                print("1. Motion Illusions (spinning, drifting effects)")
                print("2. Geometric Illusions (impossible shapes)")
                print("3. Color Illusions (contrast, afterimages)")
                print("4. Cognitive Illusions (ambiguous figures)")
                print("\nFormat: single number, list (1,2,3), range (1-3), 'all', or Enter to skip")
                
                illusion_type = input("\nChoose illusion categories: ").strip()
                
                illusion_types = {
                    "1": {
                        "name": "Motion Illusions",
                        "options": [
                            "Spinning Spiral (hypnotic rotation effect)",
                            "Peripheral Drift (subtle motion in periphery)",
                            "Motion Aftereffect (waterfall illusion)",
                            "Rotating Snakes (illusory rotation)",
                        ]
                    },
                    "2": {
                        "name": "Geometric Illusions",
                        "options": [
                            "Impossible Shapes (paradoxical structures)",
                            "Cafe Wall (parallel lines appear sloped)",
                            "Penrose Triangle (impossible triangle)",
                            "Necker Cube (ambiguous perspective)",
                        ]
                    },
                    "3": {
                        "name": "Color Illusions",
                        "options": [
                            "Simultaneous Contrast (color perception changes)",
                            "Color Afterimage (complementary color effect)",
                            "Chromatic Aberration (color splitting)",
                            "Bezold Effect (color spreading)",
                        ]
                    },
                    "4": {
                        "name": "Cognitive Illusions",
                        "options": [
                            "Ambiguous Figures (multiple interpretations)",
                            "Hidden Patterns (emergent images)",
                            "Gestalt Patterns (whole vs parts)",
                            "Anamorphic Art (perspective-dependent)",
                        ]
                    }
                }
                
                if illusion_type:
                    indices = self._parse_range_selection(illusion_type, 4)
                    if indices:
                        # Convert 0-based indices to 1-based category numbers
                        categories = [str(i + 1) for i in indices]
                        
                        # For each selected category, show its options and get specific choices
                        selected_illusions = []
                        for cat_num in categories:
                            if cat_num in illusion_types:
                                category = illusion_types[cat_num]
                                print(f"\n{category['name']} Options:")
                                for i, option in enumerate(category['options'], 1):
                                    print(f"{i}. {option}")
                                
                                specific_choice = input(f"\nChoose specific {category['name'].lower()} (same format as above): ").strip()
                                
                                if specific_choice:
                                    sub_indices = self._parse_range_selection(specific_choice, len(category['options']))
                                    if sub_indices:
                                        # Add all selected illusions from this category
                                        for idx in sub_indices:
                                            illusion = category['options'][idx].split(" (")[0]
                                            self.selected_illusions.append((category['name'], illusion))
                
                        if self.selected_illusions:
                            # Randomly select one illusion from all chosen ones for each piece
                            cat_name, chosen_illusion = random.choice(self.selected_illusions)
                            custom_guidelines = f"Create a dynamic optical illusion using the {chosen_illusion.lower()} technique. "
                            custom_guidelines += "Focus on creating a strong visual effect that challenges perception. "
                            custom_guidelines += "Ensure the illusion is clear and effective, with smooth transitions and proper timing for maximum impact."
                        else:
                            # If no specific illusions were chosen, use all selected categories
                            cat_names = [illusion_types[c]['name'] for c in categories]
                            custom_guidelines = f"Create a dynamic optical illusion combining elements from the following categories: {', '.join(cat_names)}. "
                            custom_guidelines += "Choose the most effective techniques to create compelling visual effects. "
                            custom_guidelines += "Focus on strong perceptual impact and smooth execution."
                    else:
                        custom_guidelines = "Create a dynamic optical illusion using any suitable technique. "
                        custom_guidelines += "Choose the most effective approach to create a compelling visual effect. "
                        custom_guidelines += "Focus on strong perceptual impact and smooth execution."
                else:
                    custom_guidelines = "Create a dynamic optical illusion using any suitable technique. "
                    custom_guidelines += "Choose the most effective approach to create a compelling visual effect. "
                    custom_guidelines += "Focus on strong perceptual impact and smooth execution."
            
            elif mode_choice == "6":  # Custom Guidelines
                print("\nEnter your custom creative guidelines:")
                custom_guidelines = input().strip()
        
        # If they provided guidelines but want to skip wizard, ask if they want to skip
        if custom_guidelines:
            # Check if this is a text-based requirement
            is_text_requirement = any(word in custom_guidelines.lower() for word in ['text', 'spell', 'word', 'letter'])
            
            if is_text_requirement:
                print("\nNOTE: For text-based art, we'll use:")
                print("• Shape-based letter formation (NO direct text() calls)")
                print("• PGraphics masks for letter boundaries")
                print("• Dynamic patterns that organically reveal text")
            
            print("\nWould you like to:")
            print("1. Use guidelines with wizard (recommended)")
            print("2. Use only guidelines (skip wizard)")
            choice = input("\nEnter choice (1-2) or press Enter for option 1: ").strip()
            
            if choice == "2":
                # Build prompt with just guidelines
                prompt = self._build_creative_prompt(
                    custom_guidelines=custom_guidelines
                )
                return self._generate_artwork(prompt)
        
        # Step 1: Choose base techniques
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
            motion_style=motion_style,
            shape_elements=shape_elements,
            color_approach=color_approach,
            pattern_type=pattern_type,
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
    
    def _parse_range_selection(self, selection: str, max_value: int) -> list:
        """Parse a range selection string into a list of integers.
        
        Supports formats:
        - Single numbers: "1", "2"
        - Comma-separated: "1,2,3"
        - Ranges: "1-3" or "1,3-5"
        - "all" or empty for all options
        
        Args:
            selection: Input string to parse
            max_value: Maximum allowed value (inclusive)
            
        Returns:
            List of selected indices (0-based)
        """
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
            # Store all selected styles
            self.selected_motion_styles = [styles[i] for i in indices]
            # For this generation, randomly select one
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
            # Store all selected shapes
            self.selected_shapes = [shapes[i] for i in indices]
            # For this generation, randomly select one
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
            # Store all selected approaches
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
            # Store all selected patterns
            self.selected_patterns = [patterns[i] for i in indices]
            # For this generation, randomly select one
            return random.choice(self.selected_patterns)
        return ""
    
    def _build_creative_prompt(self, motion_style: str = "", shape_elements: str = "", color_approach: str = "", pattern_type: str = "", custom_guidelines: str = "") -> dict:
        """Build the creative prompt from selected options"""
        # Start with base prompt structure
        prompt = {
            "techniques": self.selected_techniques,
            "motion_style": motion_style,
            "shape_elements": shape_elements,
            "color_approach": color_approach,
            "pattern_type": pattern_type,
        }
        
        if custom_guidelines:
            # Let the AI interpret and handle the guidelines directly
            prompt["custom_guidelines"] = custom_guidelines
            
            # If this is text art, add text-specific information
            if "text" in custom_guidelines.lower():
                # Extract the text from the guidelines (assuming format like "Create text 'PRISM'")
                text_match = re.search(r"text '([^']+)'", custom_guidelines)
                if text_match:
                    prompt["text"] = text_match.group(1)
                    prompt["is_text_art"] = True
            
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
                
                # Randomly select new options for each attempt
                if self.selected_illusions:
                    cat_name, chosen_illusion = random.choice(self.selected_illusions)
                    prompt_data["custom_guidelines"] = f"Create a dynamic optical illusion using the {chosen_illusion.lower()} technique. "
                    prompt_data["custom_guidelines"] += "Focus on creating a strong visual effect that challenges perception. "
                    prompt_data["custom_guidelines"] += "Ensure the illusion is clear and effective, with smooth transitions and proper timing for maximum impact."
                
                if self.selected_motion_styles:
                    prompt_data["motion_style"] = random.choice(self.selected_motion_styles)
                
                if self.selected_shapes:
                    prompt_data["shape_elements"] = random.choice(self.selected_shapes)
                
                if self.selected_colors:
                    prompt_data["color_approach"] = random.choice(self.selected_colors)
                
                if self.selected_patterns:
                    prompt_data["pattern_type"] = random.choice(self.selected_patterns)
                
                # Get custom guidelines if they exist
                custom_guidelines = prompt_data.get("custom_guidelines", None)
                
                # Generate the code
                code = generator.generate_code(prompt_data, custom_guidelines=custom_guidelines)
                    
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
            # Ensure render_path is relative to the renders directory
            full_render_path = self.config.base_path / "renders" / render_path
            
            # Use the generator's run_sketch method
            success, error = self.generator.run_sketch(full_render_path)
            if not success and error:
                self.log.error(f"Sketch error: {error}")
            return success
            
        except Exception as e:
            self.log.error(f"Error running sketch: {str(e)}")
            if self.config.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())
            return False

    def get_creation_settings(self, model_name: str = None) -> dict:
        """Collect all settings from the wizard but don't generate artwork yet"""
        if model_name:
            self.selected_model = model_name
        else:
            self._choose_model()
            
        print("\n════════════════════════════════════════════════════════════════════════════════")
        print("║ DYNAMIC ART WIZARD")
        print(f"║ Using Model: {self.selected_model}")
        print("════════════════════════════════════════════════════════════════════════════════\n")
        
        # Get any custom guidelines first
        print("\nChoose Creative Mode:")
        print("1. Particle Systems (physics-based animations)")
        print("2. Geometric Transformations (shape morphing)")
        print("3. Pattern Generation (recursive/emergent)")
        print("4. Text Art (shape-based/organic)")
        print("5. Optical Illusions & Visual Puzzles")
        print("6. Custom Guidelines")
        print("\nEnter choice (1-6) or press Enter to skip: ")
        mode_choice = input().strip()
        
        custom_guidelines = ""
        if mode_choice:
            if mode_choice == "1":  # Particle Systems
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
                custom_guidelines = behaviors.get(behavior, behaviors["1"])
            
            elif mode_choice == "2":  # Geometric Transformations
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
                custom_guidelines = geometries.get(geometry, geometries["1"])
            
            elif mode_choice == "3":  # Pattern Generation
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
                custom_guidelines = patterns.get(pattern, patterns["1"])
            
            elif mode_choice == "4":  # Text Art
                print("\nWhat text would you like to create? (e.g. 'PRISM', 'Hello', etc.)")
                desired_text = input().strip() or "PRISM"  # Default to PRISM if empty
                
                # NEW: Ask for additional instructions
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
                custom_guidelines = text_styles.get(text_style, f"Create text '{desired_text}' through shape-based patterns and dynamic motion")
                
                # Append extra instructions if provided
                if extra_instructions:
                    custom_guidelines += f". Additional Requirements: {extra_instructions}"
            
            elif mode_choice == "5":  # Optical Illusions
                print("\nOptical Illusion Categories:")
                print("1. Motion Illusions (spinning, drifting effects)")
                print("2. Geometric Illusions (impossible shapes)")
                print("3. Color Illusions (contrast, afterimages)")
                print("4. Cognitive Illusions (ambiguous figures)")
                print("\nFormat: single number, list (1,2,3), range (1-3), 'all', or Enter to skip")
                
                illusion_type = input("\nChoose illusion categories: ").strip()
                
                illusion_types = {
                    "1": {
                        "name": "Motion Illusions",
                        "options": [
                            "Spinning Spiral (hypnotic rotation effect)",
                            "Peripheral Drift (subtle motion in periphery)",
                            "Motion Aftereffect (waterfall illusion)",
                            "Rotating Snakes (illusory rotation)",
                        ]
                    },
                    "2": {
                        "name": "Geometric Illusions",
                        "options": [
                            "Impossible Shapes (paradoxical structures)",
                            "Cafe Wall (parallel lines appear sloped)",
                            "Penrose Triangle (impossible triangle)",
                            "Necker Cube (ambiguous perspective)",
                        ]
                    },
                    "3": {
                        "name": "Color Illusions",
                        "options": [
                            "Simultaneous Contrast (color perception changes)",
                            "Color Afterimage (complementary color effect)",
                            "Chromatic Aberration (color splitting)",
                            "Bezold Effect (color spreading)",
                        ]
                    },
                    "4": {
                        "name": "Cognitive Illusions",
                        "options": [
                            "Ambiguous Figures (multiple interpretations)",
                            "Hidden Patterns (emergent images)",
                            "Gestalt Patterns (whole vs parts)",
                            "Anamorphic Art (perspective-dependent)",
                        ]
                    }
                }
                
                if illusion_type:
                    indices = self._parse_range_selection(illusion_type, 4)
                    if indices:
                        # Convert 0-based indices to 1-based category numbers
                        categories = [str(i + 1) for i in indices]
                        
                        # For each selected category, show its options and get specific choices
                        selected_illusions = []
                        for cat_num in categories:
                            if cat_num in illusion_types:
                                category = illusion_types[cat_num]
                                print(f"\n{category['name']} Options:")
                                for i, option in enumerate(category['options'], 1):
                                    print(f"{i}. {option}")
                                
                                specific_choice = input(f"\nChoose specific {category['name'].lower()} (same format as above): ").strip()
                                
                                if specific_choice:
                                    sub_indices = self._parse_range_selection(specific_choice, len(category['options']))
                                    if sub_indices:
                                        # Add all selected illusions from this category
                                        for idx in sub_indices:
                                            illusion = category['options'][idx].split(" (")[0]
                                            self.selected_illusions.append((category['name'], illusion))
                
                        if self.selected_illusions:
                            # Randomly select one illusion from all chosen ones for each piece
                            cat_name, chosen_illusion = random.choice(self.selected_illusions)
                            custom_guidelines = f"Create a dynamic optical illusion using the {chosen_illusion.lower()} technique. "
                            custom_guidelines += "Focus on creating a strong visual effect that challenges perception. "
                            custom_guidelines += "Ensure the illusion is clear and effective, with smooth transitions and proper timing for maximum impact."
                        else:
                            # If no specific illusions were chosen, use all selected categories
                            cat_names = [illusion_types[c]['name'] for c in categories]
                            custom_guidelines = f"Create a dynamic optical illusion combining elements from the following categories: {', '.join(cat_names)}. "
                            custom_guidelines += "Choose the most effective techniques to create compelling visual effects. "
                            custom_guidelines += "Focus on strong perceptual impact and smooth execution."
                    else:
                        custom_guidelines = "Create a dynamic optical illusion using any suitable technique. "
                        custom_guidelines += "Choose the most effective approach to create a compelling visual effect. "
                        custom_guidelines += "Focus on strong perceptual impact and smooth execution."
                else:
                    custom_guidelines = "Create a dynamic optical illusion using any suitable technique. "
                    custom_guidelines += "Choose the most effective approach to create a compelling visual effect. "
                    custom_guidelines += "Focus on strong perceptual impact and smooth execution."
            
            elif mode_choice == "6":  # Custom Guidelines
                print("\nEnter your custom creative guidelines:")
                custom_guidelines = input().strip()
        
        # Step 1: Choose base techniques
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
        
        # Step 2: Choose motion style
        motion_style = self._choose_motion_style()
        
        # Step 3: Choose shape elements
        shape_elements = self._choose_shape_elements()
            
        # Step 4: Choose color approach
        color_approach = self._choose_color_approach()
        
        # Step 5: Choose pattern type
        pattern_type = self._choose_pattern_type()
        
        # Get all wizard settings
        self._choose_motion_style()
        self._choose_shape_elements()
        self._choose_color_approach()
        self._choose_pattern_type()
        
        settings = {
            "model": self.selected_model,
            "techniques": self.selected_techniques,
            "motion_styles": self.selected_motion_styles,
            "shapes": self.selected_shapes,
            "colors": self.selected_colors,
            "patterns": self.selected_patterns,
            "custom_guidelines": custom_guidelines
        }
        
        return settings
        
    def create_with_settings(self, settings: dict) -> Optional[Pattern]:
        """Create artwork using stored settings"""
        self.selected_model = settings['model']
        self.selected_techniques = settings.get('techniques', [])
        
        if settings.get('skip_wizard'):
            prompt = self._build_creative_prompt(
                motion_style="",
                shape_elements="",
                color_approach="",
                pattern_type="",
                custom_guidelines=settings['custom_guidelines']
            )
        else:
            prompt = self._build_creative_prompt(
                motion_style=settings.get('motion_style', ""),
                shape_elements=settings.get('shape_elements', ""),
                color_approach=settings.get('color_approach', ""),
                pattern_type=settings.get('pattern_type', ""),
                custom_guidelines=settings.get('custom_guidelines', "")
            )
            
        return self._generate_artwork(prompt) 