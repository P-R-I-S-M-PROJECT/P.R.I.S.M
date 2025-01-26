from typing import Dict, List, Optional, Union
import fal_client
from logger import ArtLogger
from config import Config
import os
from enum import Enum
from dataclasses import dataclass
from models.data_models import Technique, Pattern
import requests
from pathlib import Path
import base64
from datetime import datetime
from pattern_analyzer import PatternAnalyzer
from pattern_evolution import PatternEvolution
from database_manager import DatabaseManager
import random
import json
import openai
import subprocess

class FluxModel(Enum):
    SCHNELL = "fal-ai/flux/schnell"  # Turbo mode
    PRO = "fal-ai/flux-pro/new"      # Pro version
    DEV = "fal-ai/flux/dev"          # Development mode

    @classmethod
    def get_description(cls, model):
        descriptions = {
            cls.SCHNELL: "Turbo mode - Fast generation, low cost",
            cls.PRO: "Pro version - Highest cost, highest quality",
            cls.DEV: "Development mode - high cost, high quality"
        }
        return descriptions.get(model, "")

class ImageSize(Enum):
    SQUARE_HD = "square_hd"          # 1024x1024
    SQUARE = "square"                # 512x512
    PORTRAIT_4_3 = "portrait_4_3"    # 768x1024
    PORTRAIT_16_9 = "portrait_16_9"  # 576x1024
    LANDSCAPE_4_3 = "landscape_4_3"  # 1024x768
    LANDSCAPE_16_9 = "landscape_16_9"# 1024x576

@dataclass
class FluxConfig:
    image_size: Union[ImageSize, Dict[str, int]] = ImageSize.SQUARE_HD
    num_inference_steps: int = 28
    guidance_scale: float = 3.5
    num_images: int = 1
    enable_safety_checker: bool = True
    seed: Optional[int] = None
    sync_mode: bool = True
    model: FluxModel = FluxModel.PRO

class FluxGenerator:
    def __init__(self, config: Config, logger: ArtLogger = None):
        """Initialize the Flux generator with configuration"""
        self.config = config
        self.log = logger or ArtLogger()
        self.current_complexity = 0.7
        self.current_innovation = 0.5
        self.selected_size = None
        self.selected_model = None
        self.model_selected = False
        self.variant_selected = False
        
        # Initialize config structure if it doesn't exist
        if 'models' not in self.config.static_image_config:
            self.config.static_image_config['models'] = {}
        if 'flux' not in self.config.static_image_config['models']:
            self.config.static_image_config['models']['flux'] = {}
        
        # Load previously selected variant if it exists
        flux_config = self.config.static_image_config['models']['flux']
        if 'selected_variant' in flux_config:
            try:
                variant = flux_config['selected_variant']
                self.selected_model = FluxModel[variant.upper()]
                self.model_selected = True
                self.variant_selected = True
                
                # Load size if it exists
                if 'selected_size' in flux_config:
                    size = flux_config['selected_size']
                    self.selected_size = ImageSize[size.upper()]
                    
                self.log.debug(f"Loaded saved variant: {variant} and size: {size if 'selected_size' in flux_config else 'None'}")
            except Exception as e:
                self.log.error(f"Error loading saved variant: {e}")
                # Reset state if loading fails
                self.selected_model = None
                self.model_selected = False
                self.variant_selected = False
        
        # Initialize analysis and evolution systems
        self.analyzer = PatternAnalyzer(config)
        self.evolution = PatternEvolution(config)
        self.db = DatabaseManager(config)
        
        # Ensure FAL_KEY is set
        if not os.getenv("FAL_KEY") and hasattr(config, "fal_key"):
            os.environ["FAL_KEY"] = config.fal_key
        
        if not os.getenv("FAL_KEY"):
            raise ValueError("FAL_KEY environment variable or config.fal_key must be set")

    def _select_model_and_size(self):
        """Prompt user to select image size and use the selected Flux variant"""
        # Only prompt for model variant if not already selected
        if not self.variant_selected or self.selected_model is None:
            variants = self.config.static_image_config['models']['flux']['variants']
            print("\nSelect Flux model variant:")
            for i, (name, info) in enumerate(variants.items(), 1):
                print(f"{i}. {name.upper()} - {info['description']}")
            
            while True:
                try:
                    choice = input("\nEnter choice (1-3): ").strip()
                    if not choice.isdigit() or not (1 <= int(choice) <= 3):
                        print("Please enter a number between 1 and 3")
                        continue
                    variant_names = list(variants.keys())
                    selected_variant = variant_names[int(choice)-1]
                    self.selected_model = FluxModel[selected_variant.upper()]
                    self.model_selected = True
                    self.variant_selected = True
                    
                    # Save to config immediately
                    self.config.static_image_config['models']['flux']['selected_variant'] = selected_variant
                    self.config.save_metadata()
                    break
                except (ValueError, IndexError):
                    print("Invalid selection, please try again")
        
        # Only prompt for image size if not selected
        if self.selected_size is None:
            print("\nSelect image size:")
            sizes = list(ImageSize)
            size_descriptions = {
                ImageSize.SQUARE_HD: "1024x1024 - High quality square",
                ImageSize.SQUARE: "512x512 - Standard square",
                ImageSize.PORTRAIT_4_3: "768x1024 - Portrait 4:3",
                ImageSize.PORTRAIT_16_9: "576x1024 - Portrait 16:9",
                ImageSize.LANDSCAPE_4_3: "1024x768 - Landscape 4:3",
                ImageSize.LANDSCAPE_16_9: "1024x576 - Landscape 16:9"
            }
            
            for i, size in enumerate(sizes, 1):
                print(f"{i}. {size_descriptions[size]}")
            
            while True:
                try:
                    choice = input("\nEnter choice (1-6): ").strip()
                    if not choice.isdigit() or not (1 <= int(choice) <= 6):
                        print("Please enter a number between 1 and 6")
                        continue
                    self.selected_size = sizes[int(choice)-1]
                    
                    # Save to config immediately
                    self.config.static_image_config['models']['flux']['selected_size'] = self.selected_size.name
                    self.config.save_metadata()
                    break
                except (ValueError, IndexError):
                    print("Invalid selection, please try again")

    def generate_with_ai(self, prompt: str, **kwargs) -> bool:
        """Generate image using Flux AI with PRISM integration"""
        try:
            version = self.config.get_next_version()
            techniques = self._parse_techniques_from_prompt(prompt)
            
            # Get historical context
            recent_patterns = self.db.get_recent_patterns(3)
            historical_techniques = self.db.get_historical_techniques(10)
            
            # Calculate synergy and adjust parameters
            synergy_pairs = self.db.get_synergy_pairs()
            technique_stats = self.db.get_technique_stats()
            
            # Adjust parameters based on historical performance
            self._adjust_parameters(techniques, technique_stats, synergy_pairs)
            
            creative_prompt = self._build_creative_prompt(techniques)
            
            # Only select model and size if not already selected
            if not self.variant_selected or self.selected_size is None:
                self._select_model_and_size()
                # Save selections to config
                self.config.static_image_config['models']['flux']['selected_variant'] = self.selected_model.name.lower()
                self.config.static_image_config['models']['flux']['selected_size'] = self.selected_size.name
                self.config.save_metadata()
                self.log.debug(f"Saved variant {self.selected_model.name} and size {self.selected_size.name} to config")
            else:
                self.log.debug(f"Using saved variant {self.selected_model.name} and size {self.selected_size.name}")
            
            flux_config = self._build_flux_config()
            flux_config.image_size = self.selected_size
            flux_config.model = self.selected_model
            
            # Set seed if provided
            if 'seed' in kwargs:
                flux_config.seed = kwargs['seed']
            
            # Always show the creative prompt
            self.log.info(f"Creative prompt: {creative_prompt}")

            # Create metadata before generation
            metadata = {
                "version": version,
                "timestamp": datetime.now().isoformat(),
                "model": self.selected_model.name,
                "image_size": self.selected_size.name,
                "prompt": creative_prompt,
                "techniques": [t.name for t in techniques],
                "parameters": {
                    "complexity": self.current_complexity,
                    "innovation": self.current_innovation,
                    "guidance_scale": flux_config.guidance_scale,
                    "num_inference_steps": flux_config.num_inference_steps,
                    "seed": flux_config.seed
                },
                "parent_patterns": [p.version for p in recent_patterns] if recent_patterns else []
            }

            # Adjust inference steps based on model
            if self.selected_model == FluxModel.SCHNELL:
                num_inference_steps = min(12, flux_config.num_inference_steps)  # Schnell has max 12 steps
            else:
                num_inference_steps = flux_config.num_inference_steps

            def on_queue_update(update):
                if isinstance(update, fal_client.InProgress):
                    for log in update.logs:
                        print(f"Progress: {log['message']}")
            
            result = fal_client.subscribe(
                self.selected_model.value,
                arguments={
                    "prompt": creative_prompt,
                    "image_size": self.selected_size.value,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": flux_config.guidance_scale,
                    "num_images": 1,
                    "enable_safety_checker": True,
                    "sync_mode": True,
                    "seed": flux_config.seed
                },
                with_logs=True,
                on_queue_update=on_queue_update
            )
            
            if not result or "images" not in result:
                self.log.error("Failed to generate image")
                return False
            
            try:
                render_path = self.config.base_path / "renders" / f"render_v{version}"
                render_path.mkdir(parents=True, exist_ok=True)
                
                image_data = result["images"][0]
                image_url = image_data.get("url", "")
                image_path = render_path / "frame-0000.png"
                
                if image_url.startswith("data:"):
                    base64_data = image_url.split(",")[1]
                    image_bytes = base64.b64decode(base64_data)
                    with open(image_path, "wb") as f:
                        f.write(image_bytes)
                else:
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        with open(image_path, "wb") as f:
                            f.write(image_response.content)
                    else:
                        self.log.error("Failed to download image")
                        return False
                
                print(f"\nImage saved to: {image_path}")
                
                # Create pattern object
                pattern = Pattern(
                    version=version,
                    code="",  # No code for image patterns
                    timestamp=datetime.now(),
                    techniques=[t.name for t in techniques],
                    parent_patterns=[p.version for p in recent_patterns]
                )
                
                # Analyze pattern with render path
                metrics = self.analyzer.analyze_pattern(pattern, render_path)
                pattern.update_scores(metrics)
                
                # Update metadata with analysis results
                metadata["analysis"] = {
                    "overall_score": pattern.score,
                    "aesthetic_score": pattern.aesthetic_score,
                    "complexity_score": pattern.mathematical_complexity,
                    "innovation_score": pattern.innovation_score,
                    "coherence_score": pattern.visual_coherence,
                    "synergy_score": pattern.technique_synergy
                }
                
                # Run PowerShell script with metadata
                script_path = self.config.base_path / "scripts" / "run_sketches.ps1"
                metadata_json = json.dumps(metadata)
                
                cmd = [
                    "powershell.exe",
                    "-ExecutionPolicy", "Bypass",
                    "-File", str(script_path),
                    "-RenderPath", str(render_path),
                    "-Metadata", metadata_json,
                    "-Mode", "flux"
                ]
                
                subprocess.run(cmd, check=True)
                
                # Evolve techniques based on performance
                evolved_techniques = []
                for technique in techniques:
                    evolved = technique.evolve({
                        'overall': pattern.score,
                        'aesthetic': pattern.aesthetic_score,
                        'complexity': pattern.mathematical_complexity,
                        'innovation': pattern.innovation_score,
                        'combined_techniques': [t.name for t in techniques]
                    })
                    evolved_techniques.append(evolved)
                    self.db.save_technique(evolved)
                
                # Save pattern to database
                self.db.save_pattern(pattern)
                
                # Update system stats
                stats = self.db.get_system_stats()
                self.log.info(f"System Stats: {stats}")
                
                return True
                
            except Exception as e:
                self.log.error(f"Error saving image: {str(e)}")
                return False
            
        except Exception as e:
            self.log.error(f"Error in Flux generation: {str(e)}")
            return False
    
    def _adjust_parameters(self, techniques: List[Technique], stats: Dict, synergy_pairs: List[tuple]) -> None:
        """Adjust generation parameters based on historical performance"""
        # Calculate average performance metrics
        avg_scores = []
        for technique in techniques:
            if technique.name in stats:
                tech_stats = stats[technique.name]
                avg_scores.append(tech_stats['avg_score'])
                
                # Adjust complexity based on historical success
                if tech_stats['complexity_score'] > 80:
                    self.current_complexity = min(1.0, self.current_complexity * 1.1)
                
                # Adjust innovation based on adaptation rate
                if tech_stats['innovation_factor'] > 1.2:
                    self.current_innovation = min(1.0, self.current_innovation * 1.15)
        
        # Check for synergistic combinations
        technique_names = [t.name for t in techniques]
        for t1, t2, score in synergy_pairs:
            if t1 in technique_names and t2 in technique_names:
                if score > 85:
                    self.current_complexity *= 1.1
                    self.current_innovation *= 1.1
    
    def _parse_techniques_from_prompt(self, prompt: str) -> List[Technique]:
        """Parse techniques from the prompt string"""
        # Split prompt into technique names and limit to 1-2 random techniques
        technique_names = [t.strip() for t in prompt.split(',')]
        if len(technique_names) > 2:
            technique_names = random.sample(technique_names, random.randint(1, 2))
        
        # Create proper Technique objects with required fields
        techniques = []
        for name in technique_names:
            technique = Technique(
                name=name,
                description=f"Generated technique: {name}",
                parameters={},
                mathematical_concepts=[name],
                category="generated"
            )
            techniques.append(technique)
            
        return techniques
    
    def validate_creative_code(self, code: str) -> tuple[bool, str]:
        """Mock validation for compatibility - always returns success for image generation"""
        return True, None
    
    def validate_core_requirements(self, code: str) -> tuple[bool, str]:
        """Mock validation for compatibility - always returns success for image generation"""
        return True, None
    
    def _build_creative_prompt(self, techniques: List[Technique]) -> str:
        """Build a concise, focused artistic prompt"""
        try:
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=self.config.openai_key)
            
            # Get creative elements from config
            elements = self.config.static_image_config['prompt_elements']
            
            # Build system prompt for creative interpretation
            system_prompt = """You are an expert AI art director.
Create a clear, focused prompt for an AI image generator.
Keep it under 50 words.
Focus on the core visual concept.
Be direct and specific.
Return ONLY the final prompt text."""

            # Build artistic context
            artistic_context = ", ".join([t.name for t in techniques])
            
            # Build user prompt with creative guidance
            user_prompt = f"""Create a focused prompt using:

Main elements: {artistic_context}
Style: {random.choice(elements['stylistic_approaches'])}
Key visual: {random.choice(elements['visual_elements'])}
Mood: {random.choice(elements['emotional_qualities'])}

Make it clear and impactful."""

            # Get creative prompt from OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.log.error(f"Error building creative prompt: {str(e)}")
            # Simple artistic fallback
            return f"A {random.choice(elements['stylistic_approaches'])} artwork featuring {', '.join([t.name for t in techniques])}"
    
    def _build_flux_config(self) -> FluxConfig:
        """Build Flux configuration based on current settings"""
        return FluxConfig(
            image_size=self.selected_size or ImageSize.SQUARE_HD,
            num_inference_steps=max(28, int(self.current_complexity * 40)),
            guidance_scale=3.5 + (self.current_innovation * 2),
            num_images=1,
            enable_safety_checker=True,
            seed=None,
            sync_mode=True,
            model=self.selected_model or FluxModel.PRO
        )
    
    def _save_generated_images(self, result: Dict, version: int) -> None:
        """Save initial image for run_sketches.ps1 to process"""
        try:
            # Create version directory
            render_path = self.config.base_path / "renders" / f"render_v{version}"
            render_path.mkdir(parents=True, exist_ok=True)
            
            # Get image URL or data
            image_data = result["images"][0]
            image_url = image_data.get("url", "")
            
            # Save first image as frame-0000.png
            image_path = render_path / "frame-0000.png"
            
            if image_url.startswith("data:"):
                # Handle base64 data URL
                # Extract the base64 data after the comma
                base64_data = image_url.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                self.log.success("Image saved successfully from base64 data")
            else:
                # Handle HTTP URL
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    self.log.success("Image saved successfully from URL")
                else:
                    self.log.error("Failed to download image from URL")
                    return
                    
        except Exception as e:
            self.log.error(f"Error saving image: {str(e)}")
    
    def set_complexity(self, value: float) -> None:
        """Set the complexity value (0.0 to 1.0)"""
        self.current_complexity = max(0.0, min(1.0, value))
    
    def set_innovation(self, value: float) -> None:
        """Set the innovation value (0.0 to 1.0)"""
        self.current_innovation = max(0.0, min(1.0, value))
    
    def generate_async(self, prompt: str, flux_config: Optional[FluxConfig] = None) -> Optional[str]:
        """Submit an async generation request and return the request ID"""
        try:
            config = flux_config or FluxConfig()
            config.sync_mode = False  # Force async for this method
            
            arguments = {
                "prompt": prompt,
                "image_size": config.image_size.value if isinstance(config.image_size, ImageSize) else config.image_size,
                "num_inference_steps": config.num_inference_steps,
                "guidance_scale": config.guidance_scale,
                "num_images": config.num_images,
                "enable_safety_checker": config.enable_safety_checker,
                "sync_mode": False
            }
            
            if config.seed is not None:
                arguments["seed"] = config.seed
            
            # Submit async request
            handler = fal_client.submit(
                "fal-ai/flux/dev",
                arguments=arguments
            )
            
            return handler.request_id
            
        except Exception as e:
            self.log.error(f"Error submitting async request: {str(e)}")
            return None
    
    def get_result(self, request_id: str) -> Optional[Dict]:
        """Get the result of an async generation request"""
        try:
            return fal_client.result("fal-ai/flux/dev", request_id)
        except Exception as e:
            self.log.error(f"Error getting result: {str(e)}")
            return None
    
    def get_status(self, request_id: str) -> Optional[Dict]:
        """Get the status of an async generation request"""
        try:
            return fal_client.status("fal-ai/flux/dev", request_id, with_logs=True)
        except Exception as e:
            self.log.error(f"Error getting status: {str(e)}")
            return None
    
    def upload_file(self, file_path: str) -> Optional[str]:
        """Upload a file to use in generation"""
        try:
            return fal_client.upload_file(file_path)
        except Exception as e:
            self.log.error(f"Error uploading file: {str(e)}")
            return None
    
    def create_variation(self, metadata_file: Path) -> bool:
        """Create variation of a static Flux piece"""
        try:
            # Initialize required attributes
            if not hasattr(self, 'current_complexity'):
                self.current_complexity = 0.7
            if not hasattr(self, 'current_innovation'):
                self.current_innovation = 0.5
            if not hasattr(self, 'selected_model'):
                self.selected_model = FluxModel.PRO
            if not hasattr(self, 'selected_size'):
                self.selected_size = ImageSize.SQUARE_HD
            if not hasattr(self, 'variant_selected'):
                self.variant_selected = True
            if not hasattr(self, 'analyzer'):
                self.analyzer = PatternAnalyzer(self.config, self.log)
            if not hasattr(self, 'db'):
                self.db = DatabaseManager(self.config)
            
            # Load original metadata with utf-8-sig encoding to handle BOM
            with open(metadata_file, 'r', encoding='utf-8-sig') as f:
                content = f.read().strip()
                if not content:
                    self.log.error("Empty metadata file")
                    return False
                metadata = json.loads(content)
            
            # Display original prompt and metadata
            self.log.info("\nOriginal Creation:")
            self.log.info(f"Prompt: {metadata['prompt']}")
            if 'techniques' in metadata:
                self.log.info(f"Techniques: {', '.join(metadata['techniques'])}")
            if 'model' in metadata:
                self.log.info(f"Model: {metadata['model']}")
            
            # Get variation instructions
            print("\nEnter your variation instructions (e.g. 'make it more abstract' or 'add subtle PRISM text')")
            print("Or press Enter to keep original prompt and adjust interactively")
            variation_instructions = input("> ").strip()
            
            # Get number of variations to generate
            while True:
                try:
                    num_variations = input("\nHow many unique variations would you like to generate? (1-10): ").strip()
                    num_variations = int(num_variations)
                    if 1 <= num_variations <= 10:
                        break
                    print("Please enter a number between 1 and 10")
                except ValueError:
                    print("Please enter a valid number")
            
            # Build system prompt for generating multiple variations
            if variation_instructions:
                system_prompt = f"""You are helping create multiple unique variations of an existing AI artwork.
Original prompt: {metadata['prompt']}
User wants these changes: {variation_instructions}

Create {num_variations} unique prompts that maintain the core style and elements of the original,
but incorporate the requested changes in different creative ways.
Each prompt should be distinctly different while staying true to the original concept.
Format your response as a numbered list, with each prompt on a new line starting with a number.
Example:
1. First unique variation...
2. Second unique variation...
etc.

Return ONLY the numbered list of prompts."""

                # Get multiple unique prompts from OpenAI
                client = openai.OpenAI(api_key=self.config.openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o",  # Using the correct implemented model
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate {num_variations} unique variations."}
                    ],
                    temperature=0.9  # Higher temperature for more variety
                )
                
                # Parse the numbered list of prompts
                prompts_text = response.choices[0].message.content.strip()
                new_prompts = []
                for line in prompts_text.split('\n'):
                    if line.strip() and any(line.startswith(f"{i}.") for i in range(1, num_variations + 1)):
                        prompt = line.split('.', 1)[1].strip()
                        new_prompts.append(prompt)
            else:
                # If no instructions, just use the original prompt multiple times
                new_prompts = [metadata['prompt']] * num_variations
            
            # Set model and size from original metadata if available
            if 'model' in metadata:
                try:
                    self.selected_model = FluxModel[metadata['model']]
                except KeyError:
                    pass  # Keep default if model not found
            
            if 'image_size' in metadata:
                try:
                    self.selected_size = ImageSize[metadata['image_size']]
                except KeyError:
                    pass  # Keep default if size not found
            
            # Generate variations with same parameters as original if available
            params = metadata.get('parameters', {})
            
            success = True
            for i, prompt in enumerate(new_prompts, 1):
                self.log.info(f"\nGenerating variation {i} of {num_variations}...")
                self.log.info(f"Prompt: {prompt}")
                
                # Generate the variation with the unique prompt
                current_success = self.generate_with_ai(
                    prompt,
                    complexity=params.get('complexity', 0.7),
                    innovation=params.get('innovation', 0.5),
                    guidance_scale=params.get('guidance_scale', 4.5),
                    num_inference_steps=params.get('num_inference_steps', 28)
                )
                success = success and current_success
            
            return success
            
        except json.JSONDecodeError as je:
            self.log.error(f"Error reading metadata file (JSON format error): {je}")
            if hasattr(self.log, 'debug_mode') and self.log.debug_mode:
                with open(metadata_file, 'r', encoding='utf-8-sig') as f:
                    self.log.debug(f"File contents:\n{f.read()}")
            return False
        except Exception as e:
            self.log.error(f"Error creating static variation: {e}")
            if hasattr(self.log, 'debug_mode') and self.log.debug_mode:
                import traceback
                self.log.debug(traceback.format_exc())
            return False 