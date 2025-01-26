from pathlib import Path
import yaml
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING, List
import os
from dotenv import load_dotenv
import random

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Config:
    def __init__(self):
        """Initialize configuration"""
        # Load environment variables
        load_dotenv()
        
        # Get API keys
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable not found")
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not found")
            
        # Set base path
        self.base_path = Path(os.getcwd())
        
        # Set up paths
        self.data_dir = self.base_path / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Model configuration
        self.model_config = {
            'available_models': ['o1', 'o1-mini', '4o', 'claude-3-opus', 'claude-3.5-sonnet', 'flux'],
            'default_model': '4o',
            'model_selection': 'random',  # 'random' or specific model name
            'model_weights': {
                '4o': 0.167,
                'o1': 0.167,
                'o1-mini': 0.167,
                'claude-3-opus': 0.167,   
                'claude-3.5-sonnet': 0.167, 
                'flux': 0.167  # Flux with internal variants
            }
        }
        
        # Static Image Generation Configuration
        self.static_image_config = {
            'models': {
                'flux': {
                    'variants': {
                        'pro': {
                            'endpoint': 'fal-ai/flux-pro/new',
                            'description': 'High quality image generation',
                            'weight': 0.33
                        },
                        'schnell': {
                            'endpoint': 'fal-ai/flux/schnell',
                            'description': 'Fast turbo mode generation',
                            'weight': 0.33
                        },
                        'dev': {
                            'endpoint': 'fal-ai/flux/dev',
                            'description': 'Development mode with latest features',
                            'weight': 0.34
                        }
                    }
                }
            },
            'prompt_elements': {
                'visual_elements': [
                    'color', 'form', 'texture', 'light',
                    'pattern', 'depth', 'contrast', 'movement'
                ],
                'emotional_qualities': [
                    'serene', 'dynamic', 'mysterious', 'bold',
                    'ethereal', 'chaotic', 'harmonious', 'playful'
                ],
                'stylistic_approaches': [
                    'painterly', 'photographic', 'illustrative',
                    'geometric', 'minimal', 'textural', 'atmospheric'
                ]
            },
            'categories': {
                'subjects': [
                    'Animal', 'Architecture', 'Character', 'Nature',
                    'People', 'Science', 'Abstract', 'Landscape'
                ]
            },
            'creative_guidance': {
                'conceptual_fusion': {
                    'description': 'How different artistic elements can blend',
                    'examples': [
                        'Traditional techniques merging with digital aesthetics',
                        'Abstract concepts materializing through organic forms',
                        'Cultural elements weaving into contemporary expressions'
                    ]
                },
                'artistic_balance': {
                    'description': 'Balance between different artistic elements',
                    'examples': [
                        'Chaos and order in dynamic equilibrium',
                        'Traditional and contemporary elements in harmony',
                        'Personal vision meeting universal themes'
                    ]
                },
                'narrative_depth': {
                    'description': 'Ways to add depth and meaning',
                    'examples': [
                        'Layered symbolism and metaphor',
                        'Personal and universal storytelling',
                        'Cultural and historical references'
                    ]
                }
            },
            'ai_agent_guidelines': {
                'prompt_crafting': [
                    'Blend different artistic elements intuitively',
                    'Balance tradition with innovation',
                    'Embrace diverse artistic perspectives',
                    'Consider cultural and personal contexts'
                ],
                'variation_approaches': [
                    'Explore multiple artistic interpretations',
                    'Play with different cultural influences',
                    'Experiment with technique combinations',
                    'Adapt to different artistic contexts'
                ],
                'quality_aspects': [
                    'Visual impact and aesthetic harmony',
                    'Conceptual depth and clarity',
                    'Technical execution and innovation',
                    'Cultural relevance and resonance'
                ]
            },
            'evaluation_criteria': {
                'aesthetic': ['composition', 'harmony', 'impact'],
                'technical': ['execution', 'innovation', 'control'],
                'conceptual': ['depth', 'originality', 'resonance']
            }
        }
        
        # Integration settings
        self.static_integration = {
            'use_existing_db': True,  # Use main PRISM database
            'shared_evolution': True,  # Share evolution system
            'specialized_metrics': True,  # Use image-specific metrics
            'template_mixing': True  # Allow mixing code and image templates
        }
        
        # Performance thresholds
        self.static_thresholds = {
            'min_quality_score': 75.0,
            'innovation_boost': 1.2,
            'complexity_factor': 1.1,
            'style_consistency': 0.85
        }
        
        # Initialize components
        self._metadata = None
        self._db_manager: 'DatabaseManager' = None
        
        # Load or initialize config
        self.load_config()
        
        # Verify required files
        self._verify_required_files()
        
        # Add technique categories mapping for easy access
        self.technique_categories = {
            'geometry': self.metadata['parameters']['creative_core']['mathematical_concepts']['geometry'],
            'motion': self.metadata['parameters']['creative_core']['mathematical_concepts']['motion'],
            'patterns': self.metadata['parameters']['creative_core']['mathematical_concepts']['patterns']
        }
    
    def _verify_required_files(self):
        """Verify all required files exist"""
        required_files = [
            self.base_path / "prism.pde",
            self.base_path / "scripts" / "run_sketches.ps1",
            self.base_path / "scripts" / "ffmpeg.exe"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")
    
    @property
    def db_manager(self) -> 'DatabaseManager':
        """Get database manager instance (lazy initialization)"""
        if self._db_manager is None:
            from database_manager import DatabaseManager
            self._db_manager = DatabaseManager(self)
        return self._db_manager
    
    @property
    def database_path(self) -> Path:
        """Get path to SQLite database"""
        return self.data_dir / "database.db"
    
    @property
    def api_key(self) -> str:
        """Get OpenAI API key"""
        return self.openai_key
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get system metadata"""
        return self._metadata
    
    @property
    def paths(self) -> Dict[str, Path]:
        """Get important file paths"""
        return {
            'template': self.base_path / "prism.pde",
        }
    
    def initialize_metadata(self):
        """Initialize metadata with expanded technique categories"""
        self._metadata = {
            'current_version': 0,
            'last_updated': datetime.now().isoformat(),
            'parameters': {
                'system': {
                    'base_resolution': [1080, 1080],
                    'frame_rate': 60,
                    'total_frames': 360,
                    'render_quality': 'P2D'
                },
                'generation': {
                    'constraints': {
                        'max_elements': 1000,
                        'min_frame_time': 16
                    },
                    'ai_parameters': {
                        'last_used_model': None,
                        'generation_stats': {
                            'o1': {'uses': 0, 'avg_score': 0},
                            'o1-mini': {'uses': 0, 'avg_score': 0},
                            '4o': {'uses': 0, 'avg_score': 0}
                        }
                    }
                },
                'creative_core': {
                    'mathematical_concepts': {
                        'geometry': [
                            'circle_packing',
                            'voronoi_diagrams',
                            'delaunay_triangulation',
                            'fibonacci_spiral',
                            'lissajous_curves',
                            'cardioids',
                            'superellipse',
                            'hypocycloid',
                            'rose_curves',
                            'phyllotaxis',
                            'polygon_morphing',
                            'spirograph',
                            'golden_ratio',
                            'tesselation',
                            'meander_patterns',
                            'star_polygons',
                            'truchet_tiles',
                            'hyperbolic_tiling',
                            'kaleidoscopic_transforms',
                            'l_system_fractals',
                            'strange_attractors',
                            'chladni_patterns',
                            'dla_growth',
                            'procedural_terrain'
                        ],
                        'motion': [
                            'harmonic_motion',
                            'wave_interference',
                            'flow_fields',
                            'parametric_motion',
                            'brownian_motion',
                            'particle_systems',
                            'spring_physics',
                            'orbital_motion',
                            'pendulum_motion',
                            'circular_motion',
                            'wave_propagation',
                            'perlin_noise_motion',
                            'elastic_motion',
                            'spiral_motion',
                            'oscillation',
                            'lerp_transitions',
                            'flocking_boids',
                            'swarm_intelligence',
                            'advanced_physics',
                            'agent_based_drawing',
                            'temporal_shifts',
                            'emergent_behavior',
                            'collective_motion'
                        ],
                        'patterns': [
                            'cellular_automata',
                            'fractals',
                            'recursive_patterns',
                            'stroke_variations',
                            'reaction_diffusion',
                            'noise_landscapes',
                            'moiré_patterns',
                            'tiling_systems',
                            'interference_patterns',
                            'mandala_patterns',
                            'maze_generation',
                            'dot_patterns',
                            'grid_deformation',
                            'symmetry_patterns',
                            'line_weaving',
                            'halftone_patterns',
                            'l_systems',
                            'pixel_sorting',
                            'glitch_effects',
                            'feedback_loops',
                            'blend_modes',
                            'color_harmonies',
                            'resonance_patterns'
                        ]
                    }
                },
                'analysis': {
                    'visual': {
                        'edge_threshold': [100, 200],
                        'feature_weights': {
                            'edge_density': 0.5,
                            'contrast': 0.5
                        }
                    },
                    'aesthetic': {
                        'weights': {
                            'balance': 0.6,
                            'contrast': 0.4
                        }
                    },
                    'motion': {
                        'flow_weight': 0.7,
                        'coverage_weight': 0.3
                    }
                }
            }
        }
        
        self.save_metadata()
    
    def save_metadata(self):
        """Save metadata to YAML file"""
        with open(self.data_dir / "metadata.yaml", 'w') as f:
            yaml.safe_dump(self._metadata, f)
    
    def load_config(self):
        """Load or initialize configuration"""
        try:
            metadata_path = self.data_dir / "metadata.yaml"
            if metadata_path.exists():
                with open(metadata_path) as f:
                    self._metadata = yaml.safe_load(f)
                if not self._metadata:
                    self.initialize_metadata()
            else:
                self.initialize_metadata()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.initialize_metadata()
    
    def update_version_from_renders(self) -> int:
        """Scan renders directory and update version tracking across system"""
        try:
            # Scan renders directory for latest version
            renders_path = self.base_path / "renders"
            if not renders_path.exists():
                return 1
                
            versions = []
            for dir_path in renders_path.glob("render_v*"):
                try:
                    version_str = dir_path.name.replace("render_v", "")
                    version = int(version_str)
                    versions.append(version)
                except ValueError:
                    continue
            
            next_version = max(versions, default=0) + 1
            
            # Update metadata
            self.metadata['current_version'] = next_version - 1  # Current is last completed
            self.save_metadata()
            
            # Update database if needed
            if versions:  # Only if we found versions
                latest_version = max(versions)
                self.db_manager.ensure_version_exists(latest_version)
            
            return next_version
            
        except Exception as e:
            self.log.error(f"Error updating version from renders: {e}")
            return 1

    def get_next_version(self) -> int:
        """Get next version number, scanning renders directory first"""
        return self.update_version_from_renders()
    
    def _load_environment(self) -> Dict[str, str]:
        """Load required environment variables"""
        api_key = os.getenv('OPENAI_API_KEY')
        claude_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not found")
        if not claude_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not found")
        return {
            'OPENAI_API_KEY': api_key,
            'ANTHROPIC_API_KEY': claude_key
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get current model configuration"""
        return self.model_config
    
    def set_model_selection(self, mode: str):
        """Set model selection mode ('random' or specific model name)"""
        if mode == 'random' or mode in self.model_config['available_models']:
            self.model_config['model_selection'] = mode
        else:
            raise ValueError(f"Invalid model selection mode: {mode}")
    
    def get_prompt_template(self, category: str = None) -> str:
        """Get a prompt template, optionally filtered by category"""
        templates = self.static_image_config['prompt_templates']
        if not category:
            return random.choice(templates)
        return next((t for t in templates if category in t), random.choice(templates))
    
    def get_quality_modifiers(self, complexity: float) -> List[str]:
        """Get appropriate quality modifiers based on complexity"""
        modifiers = []
        if complexity > 0.7:
            modifiers.extend([
                random.choice(self.static_image_config['quality_modifiers']['detail_level']),
                random.choice(self.static_image_config['quality_modifiers']['lighting'])
            ])
        if complexity > 0.8:
            modifiers.append(
                random.choice(self.static_image_config['quality_modifiers']['texture'])
            )
        return modifiers
    
    def evaluate_static_image(self, metrics: Dict) -> float:
        """Evaluate a static image using specialized criteria"""
        weights = {
            'technical': 0.4,
            'artistic': 0.4,
            'conceptual': 0.2
        }
        
        score = 0.0
        for category, weight in weights.items():
            criteria = self.static_image_config['evaluation_criteria'][category]
            category_score = sum(metrics.get(c, 0) for c in criteria) / len(criteria)
            score += category_score * weight
            
        return score