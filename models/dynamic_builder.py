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
    def __init__(self, config: Config, log: ArtLogger, generator, db, menu_manager):
        self.config = config
        self.log = log
        self.generator = generator
        self.db = db
        self.menu_manager = menu_manager
        self.current_complexity = 0.7
        self.current_innovation = 0.5
        self.selected_techniques = []
        self.selected_model = None
        self.selected_illusions = []
        self.selected_motion_styles = []
        self.selected_shapes = []
        self.selected_colors = []
        self.selected_patterns = []
    
    def create_artwork(self, settings: dict) -> Optional[Pattern]:
        """Create artwork using provided settings"""
        # Restore all saved settings
        self.selected_model = settings['model']
        self.selected_techniques = settings.get('techniques', [])
        self.selected_motion_styles = settings.get('motion_styles', [])
        self.selected_shapes = settings.get('shapes', [])
        self.selected_colors = settings.get('colors', [])
        self.selected_patterns = settings.get('patterns', [])
        
        # Build the creative prompt
        prompt = self._build_creative_prompt(
            motion_style=random.choice(self.selected_motion_styles) if self.selected_motion_styles else "",
            shape_elements=random.choice(self.selected_shapes) if self.selected_shapes else "",
            color_approach=random.choice(self.selected_colors) if self.selected_colors else "",
            pattern_type=random.choice(self.selected_patterns) if self.selected_patterns else "",
            custom_guidelines=settings.get('custom_guidelines', "")
        )
        
        # If this is text art, ensure text-specific settings are preserved
        if "text" in settings.get('custom_guidelines', "").lower():
            prompt["is_text_art"] = True
            # Extract the text from the guidelines (assuming format like "Create text 'PRISM'")
            text_match = re.search(r"text '([^']+)'", settings['custom_guidelines'])
            if text_match:
                prompt["text"] = text_match.group(1)
            
        return self._generate_artwork(prompt)
    
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
            last_error = None
            for attempt in range(max_retries):
                if attempt > 0:
                    self.log.info(f"Generation attempt {attempt+1}/{max_retries}")
                    
                    # If we have a last error, modify the prompt to address it
                    if last_error:
                        if "Missing ';'" in last_error:
                            self.log.debug("Detected missing semicolon error, adding explicit instruction")
                            if "custom_guidelines" in prompt_data:
                                prompt_data["custom_guidelines"] = "IMPORTANT: Ensure all statements end with semicolons. " + prompt_data["custom_guidelines"]
                        elif "letterMask" in last_error:
                            self.log.debug("Detected letterMask error, adding explicit instruction")
                            if "custom_guidelines" in prompt_data:
                                prompt_data["custom_guidelines"] = "IMPORTANT: Follow exact letterMask initialization sequence. " + prompt_data["custom_guidelines"]
                
                # Randomly select new options for each attempt
                if self.selected_illusions:
                    _, chosen_illusion = random.choice(self.selected_illusions)
                    illusion_guidelines = f"Create a dynamic optical illusion using the {chosen_illusion.lower()} technique. "
                    illusion_guidelines += "Focus on creating a strong visual effect that challenges perception. "
                    illusion_guidelines += "Ensure the illusion is clear and effective, with smooth transitions and proper timing for maximum impact."
                    
                    # Preserve existing custom guidelines if they exist
                    existing_guidelines = prompt_data.get("custom_guidelines", "")
                    if existing_guidelines:
                        prompt_data["custom_guidelines"] = f"{existing_guidelines}. {illusion_guidelines}"
                    else:
                        prompt_data["custom_guidelines"] = illusion_guidelines
                
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
                
                try:
                    # Generate the code with retry count and last error
                    code = generator.generate_code(prompt_data, custom_guidelines=custom_guidelines, retry_count=attempt)
                    
                    if not code:
                        if attempt < max_retries - 1:
                            continue
                        self.log.error("Failed to generate valid code")
                        return None
                    
                    # Add Processing-specific syntax validation
                    if "java.util" in code or "lambda" in code:
                        self.log.debug("Detected unsupported Java features, retrying with simpler code")
                        if attempt < max_retries - 1:
                            continue
                    
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
                            techniques=self.selected_techniques,
                            model=self.selected_model,
                            parameters={
                                "complexity": self.current_complexity,
                                "innovation": self.current_innovation
                            },
                            creative_approach={
                                "geometry_techniques": self._get_random_techniques_from_category('geometry', 3),
                                "motion_techniques": self._get_random_techniques_from_category('motion', 3),
                                "pattern_techniques": self._get_random_techniques_from_category('patterns', 3)
                            }
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
                    
                except Exception as e:
                    last_error = str(e)
                    self.log.error(f"Error in generation attempt {attempt+1}: {e}")
                    if attempt == max_retries - 1:
                        if self.config.debug_mode:
                            import traceback
                            self.log.debug(traceback.format_exc())
                        return None
                    continue
            
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
    
    def _get_random_techniques_from_category(self, category: str, count: int = 3) -> List[str]:
        """Get a random selection of techniques from a category"""
        if category not in self.config.technique_categories:
            return []
        
        available_techniques = self.config.technique_categories[category]
        if not available_techniques:
            return []
            
        # Return random selection, but don't exceed available techniques
        count = min(count, len(available_techniques))
        return random.sample(available_techniques, count) 