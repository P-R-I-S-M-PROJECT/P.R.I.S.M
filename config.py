from pathlib import Path
import yaml
from datetime import datetime
from typing import Dict, Any, TYPE_CHECKING
import os
from dotenv import load_dotenv

if TYPE_CHECKING:
    from database_manager import DatabaseManager

class Config:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.env = self._load_environment()
        
        # Set up paths
        self.base_path = Path(__file__).parent
        self.data_dir = self.base_path / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Model configuration
        self.model_config = {
            'available_models': ['o1', 'o1-mini', '4o'],
            'default_model': '4o',
            'model_selection': 'random',  # 'random' or specific model name
            'model_weights': {
                '4o': 0.34,
                'o1': 0.33,
                'o1-mini': 0.33
            }
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
            self.base_path / "auto.pde",
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
        return self.env['OPENAI_API_KEY']
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get system metadata"""
        return self._metadata
    
    @property
    def paths(self) -> Dict[str, Path]:
        """Get important file paths"""
        return {
            'template': self.base_path / "auto.pde",
        }
    
    def initialize_metadata(self):
        """Initialize metadata with expanded technique categories"""
        self._metadata = {
            'current_version': 0,
            'last_updated': datetime.now().isoformat(),
            'parameters': {
                'system': {
                    'base_resolution': [800, 800],
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
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not found")
        return {'OPENAI_API_KEY': api_key}
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get current model configuration"""
        return self.model_config
    
    def set_model_selection(self, mode: str):
        """Set model selection mode ('random' or specific model name)"""
        if mode == 'random' or mode in self.model_config['available_models']:
            self.model_config['model_selection'] = mode
        else:
            raise ValueError(f"Invalid model selection mode: {mode}")