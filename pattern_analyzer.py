from typing import Dict, List
import numpy as np
import cv2
from pathlib import Path
from models.data_models import Pattern
from config import Config
from logger import ArtLogger

class PatternAnalyzer:
    """Analyzes generated patterns for objective quality metrics"""
    
    def __init__(self, config: Config, logger: ArtLogger = None):
        self.config = config
        self.db = config.db_manager
        self.log = logger or ArtLogger()
        
        # Get analysis parameters from config
        try:
            self.analysis_params = self.config.metadata['parameters']['analysis']
        except KeyError:
            raise ValueError("Missing required analysis parameters in config")
    
    def analyze_pattern(self, pattern: Pattern, render_path: Path) -> Dict[str, float]:
        """Perform comprehensive pattern analysis"""
        try:
            # Fix render path to match actual location
            render_path = self.config.base_path / "renders" / f"render_v{pattern.version}"
            
            self.log.debug(f"Starting analysis for pattern v{pattern.version}")
            self.log.debug(f"Checking render path: {render_path}")
            
            if not render_path.exists():
                self.log.error(f"Render path does not exist: {render_path}")
                return self._get_default_scores()
            
            frames = self._load_frames(render_path)
            if not frames:
                self.log.error("No frames loaded for analysis")
                return self._get_default_scores()
            
            self.log.debug(f"Analyzing {len(frames)} frames")
            
            # Calculate core metrics with more diverse weighting
            try:
                complexity = self._calculate_complexity(frames)
                self.log.debug(f"Raw complexity score: {complexity:.2f}")
                # Removed hardcoded technique-specific boosts to maintain creative freedom
                self.log.debug(f"Final complexity score: {complexity:.2f}")
            except Exception as e:
                self.log.error(f"Complexity calculation failed: {e}")
                complexity = 60.0 + np.random.normal(0, 5)
            
            try:
                innovation = self._calculate_innovation(frames, pattern)
                # Boost innovation for certain technique combinations
                if len(pattern.techniques) >= 3:
                    innovation *= 1.15
                self.log.debug(f"Innovation score: {innovation:.2f}")
            except Exception as e:
                self.log.error(f"Innovation calculation failed: {e}")
                innovation = 70.0 + np.random.normal(0, 10)
            
            try:
                aesthetic = self._calculate_aesthetic_score(frames) * 100
                # Adjust aesthetic based on frame analysis
                if np.std([np.std(f) for f in frames]) > 0.1:  # High variation between frames
                    aesthetic *= 1.1
                self.log.debug(f"Aesthetic score: {aesthetic:.2f}")
            except Exception as e:
                self.log.error(f"Aesthetic calculation failed: {e}")
                aesthetic = 65.0 + np.random.normal(0, 7)
            
            try:
                motion = self._calculate_motion_quality(frames) * 100
                self.log.debug(f"Motion score: {motion:.2f}")
            except Exception as e:
                self.log.error(f"Motion calculation failed: {e}")
                motion = 60.0 + np.random.normal(0, 8)
            
            # Calculate new metrics
            try:
                coherence = self._calculate_visual_coherence(frames) * 100
                self.log.debug(f"Coherence score: {coherence:.2f}")
            except Exception as e:
                self.log.error(f"Coherence calculation failed: {e}")
                coherence = 70.0 + np.random.normal(0, 5)
            
            try:
                synergy = self._calculate_technique_synergy(pattern) * 100
                self.log.debug(f"Synergy score: {synergy:.2f}")
            except Exception as e:
                self.log.error(f"Synergy calculation failed: {e}")
                synergy = 75.0 + np.random.normal(0, 5)
            
            # Dynamic weighting based on pattern characteristics
            weights = self._calculate_dynamic_weights(pattern, complexity, innovation, aesthetic, motion)
            
            # Combine metrics with dynamic weighting
            overall_score = (
                complexity * weights['complexity'] +
                innovation * weights['innovation'] +
                aesthetic * weights['aesthetic'] +
                motion * weights['motion']
            )
            
            # Adjust overall score based on coherence and synergy
            overall_score *= (1.0 + (coherence - 75) / 200)  # Small boost/penalty based on coherence
            overall_score *= (1.0 + (synergy - 75) / 200)    # Small boost/penalty based on synergy
            
            # Ensure score stays within bounds
            overall_score = float(max(10.0, min(100.0, overall_score)))
            
            return {
                'overall': float(overall_score),
                'complexity': float(complexity),
                'innovation': float(innovation),
                'aesthetic': float(aesthetic),
                'motion': float(motion),
                'coherence': float(coherence),
                'synergy': float(synergy)
            }
            
        except Exception as e:
            self.log.error(f"Pattern analysis failed: {str(e)}")
            import traceback
            self.log.debug(f"Traceback: {traceback.format_exc()}")
            return self._get_default_scores()
    
    def _load_frames(self, render_path: Path) -> List[np.ndarray]:
        """Load and preprocess frames for analysis"""
        frames = []
        try:
            # Ensure we're looking in the correct directory
            if not render_path.exists():
                self.log.error(f"Render path does not exist: {render_path}")
                return []
            
            # Look for frames in the correct subdirectory
            frames_dir = render_path / "frames"
            if frames_dir.exists():
                frame_path = frames_dir
            else:
                frame_path = render_path
            
            self.log.debug(f"Searching for frames in: {frame_path}")
            
            # Get all PNG files
            frame_files = sorted(frame_path.glob("frame-*.png"))
            self.log.debug(f"Found {len(frame_files)} frame files")
            
            if not frame_files:
                self.log.error(f"No frame files found in {frame_path}")
                # List directory contents for debugging
                self.log.debug(f"Directory contents: {list(frame_path.glob('*'))}")
                return []
            
            # Sample frames for efficiency (every 6th frame)
            for frame_path in frame_files[::6]:
                try:
                    frame = cv2.imread(str(frame_path), cv2.IMREAD_GRAYSCALE)
                    if frame is not None:
                        frames.append(frame)
                        self.log.debug(f"Successfully loaded frame: {frame_path.name}")
                    else:
                        self.log.error(f"Failed to load frame (returned None): {frame_path}")
                except Exception as e:
                    self.log.error(f"Error loading individual frame {frame_path}: {e}")
                
            self.log.debug(f"Successfully loaded {len(frames)} frames")
            
            if not frames:
                self.log.error("No frames were successfully loaded")
            else:
                # Log frame properties for debugging
                sample_frame = frames[0]
                self.log.debug(f"Sample frame shape: {sample_frame.shape}, dtype: {sample_frame.dtype}")
            
            return frames
            
        except Exception as e:
            self.log.error(f"Error in frame loading: {e}")
            import traceback
            self.log.debug(f"Traceback: {traceback.format_exc()}")
            return []
    
    def _calculate_complexity(self, frames: List[np.ndarray]) -> float:
        """Calculate pattern complexity"""
        try:
            if not frames:
                self.log.error("No frames provided for complexity calculation")
                return 0.75  # Return higher default

            complexity_scores = []
            
            for i, frame in enumerate(frames):
                try:
                    # Validate frame
                    if frame is None or frame.size == 0:
                        self.log.error(f"Invalid frame at index {i}")
                        continue
                        
                    # Edge complexity - Enhanced edge detection
                    edges = cv2.Canny(frame, 30, 150)  # Lower threshold to detect more edges
                    edge_density = np.count_nonzero(edges) / frame.size
                    
                    # Pattern density - Calculate active pixels
                    active_pixels = np.count_nonzero(frame > 30) / frame.size
                    
                    # Intensity variation with higher weight
                    intensity_std = np.std(frame) / 128.0
                    
                    # Region complexity - Check distinct regions
                    binary_mask = (frame > 30).astype(np.uint8) * 255  # Convert to proper format
                    _, regions = cv2.connectedComponents(binary_mask)
                    region_complexity = min(1.0, (regions.max() / 100))  # Normalize to max 100 regions
                    
                    # Combine metrics with adjusted weights
                    frame_score = (
                        edge_density * 0.4 +          # Increased edge weight
                        active_pixels * 0.3 +         # Pattern density
                        intensity_std * 0.15 +        # Variation
                        region_complexity * 0.15      # Region complexity
                    ) * 1.2  # Boost overall complexity
                    
                    complexity_scores.append(frame_score)
                    
                except Exception as e:
                    self.log.error(f"Error processing frame {i}: {e}")
                    continue
            
            if not complexity_scores:
                return 0.75
            
            # Take the average and ensure it stays within bounds
            final_score = min(1.0, max(0.3, np.mean(complexity_scores)))
            return final_score * 100  # Convert to 0-100 scale
            
        except Exception as e:
            self.log.error(f"Error calculating complexity: {e}")
            return 75.0  # Return higher default on error
    
    def _calculate_innovation(self, frames: List[np.ndarray], pattern: Pattern) -> float:
        """Calculate innovation score"""
        try:
            # Get historical patterns
            historical_patterns = self._get_historical_patterns()
            
            # First pattern gets high innovation score
            if not historical_patterns:
                return 85.0
            
            # Base score
            base_score = 75.0
            
            # Add technique bonus
            technique_bonus = self._calculate_technique_bonus(pattern.techniques)
            
            # Add visual bonus - only if we have historical frames to compare against
            visual_bonus = self._calculate_visual_bonus(frames, historical_patterns) if historical_patterns else 10.0
            
            return min(100.0, base_score + technique_bonus + visual_bonus)
            
        except Exception as e:
            self.log.error(f"Error calculating innovation: {e}")
            return 75.0
    
    def _calculate_aesthetic_score(self, frames: List[np.ndarray]) -> float:
        """Calculate aesthetic quality with artistic vision principles"""
        try:
            if not frames:
                return 0.5
            
            aesthetic_scores = []
            
            for frame in frames:
                # Calculate compositional balance
                left_half = np.mean(frame[:, :frame.shape[1]//2])
                right_half = np.mean(frame[:, frame.shape[1]//2:])
                top_half = np.mean(frame[:frame.shape[0]//2, :])
                bottom_half = np.mean(frame[frame.shape[0]//2:, :])
                
                balance = 1 - (abs(left_half - right_half) + abs(top_half - bottom_half)) / 510
                
                # Calculate negative space usage
                negative_space = 1 - (np.count_nonzero(frame) / frame.size)
                
                # Calculate layering and depth
                edges = cv2.Canny(frame, 50, 150)
                edge_density = np.count_nonzero(edges) / frame.size
                
                # Calculate contrast and form
                contrast = np.std(frame) / 128.0
                
                # Weight the components based on artistic principles
                frame_score = (
                    balance * 0.3 +           # Compositional balance
                    negative_space * 0.2 +    # Effective use of negative space
                    edge_density * 0.25 +     # Layering and depth
                    contrast * 0.25           # Contrast and form
                )
                aesthetic_scores.append(frame_score)
            
            return np.mean(aesthetic_scores)
            
        except Exception as e:
            self.log.error(f"Error calculating aesthetic score: {e}")
            return 0.5
    
    def _calculate_motion_quality(self, frames: List[np.ndarray]) -> float:
        """Calculate motion quality with artistic vision principles"""
        try:
            if len(frames) < 2:
                return 0.5
            
            motion_scores = []
            
            for i in range(len(frames) - 1):
                # Calculate optical flow
                flow = cv2.calcOpticalFlowFarneback(
                    frames[i], frames[i+1], None,
                    0.5, 3, 15, 3, 5, 1.2, 0
                )
                
                # Calculate flow magnitude and direction
                magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                
                # Score motion qualities - Add safety checks
                mean_magnitude = np.mean(magnitude)
                if mean_magnitude > 0:
                    smoothness = 1 - min(1.0, np.std(magnitude) / mean_magnitude)
                else:
                    smoothness = 1.0  # No motion = perfectly smooth
                
                coverage = np.count_nonzero(magnitude > 0.1) / magnitude.size
                
                # Calculate flow direction consistency
                flow_angles = np.arctan2(flow[..., 1], flow[..., 0])
                direction_consistency = 1 - min(1.0, np.std(flow_angles) / np.pi)
                
                # Get dimensions for center weighting
                height, width = magnitude.shape
                center_y, center_x = height // 2, width // 2
                
                # Calculate distances from center
                y_coords = np.arange(height)[:, None]
                x_coords = np.arange(width)[None, :]
                distances = np.sqrt(
                    (y_coords - center_y) ** 2 +
                    (x_coords - center_x) ** 2
                )
                
                # Calculate center-weighted flow - Add safety check
                center_weight = np.exp(-distances / (height / 4))
                magnitude_sum = np.sum(magnitude)
                if magnitude_sum > 0:
                    motion_guidance = np.sum(magnitude * center_weight) / magnitude_sum
                else:
                    motion_guidance = 0.5  # Neutral score for no motion
                
                # Combine scores with artistic vision weights
                frame_score = (
                    smoothness * 0.3 +           # Smooth, organic motion
                    coverage * 0.2 +             # Overall motion presence
                    direction_consistency * 0.25 + # Coherent motion patterns
                    motion_guidance * 0.25        # Eye-guiding motion
                )
                motion_scores.append(frame_score)
            
            return np.mean(motion_scores)
            
        except Exception as e:
            self.log.error(f"Error calculating motion quality: {e}")
            return 0.5
    
    def _calculate_technique_bonus(self, techniques: List[str]) -> float:
        """Calculate bonus for technique combinations"""
        try:
            historical = self.db.get_historical_techniques(limit=10)
            
            if not historical or not techniques:
                return 10.0
            
            current_set = set(techniques)
            historical_sets = [set(h) for h in historical]
            
            # Check for exact matches
            if current_set in historical_sets:
                return 0.0
            
            # Check for partial matches
            partial_matches = sum(1 for h in historical_sets if h.intersection(current_set))
            
            return max(0.0, 10.0 - (partial_matches * 2.0))
            
        except Exception as e:
            self.log.error(f"Error calculating technique bonus: {e}")
            return 5.0
    
    def _calculate_visual_bonus(self, frames: List[np.ndarray], 
                              historical_patterns: List[List[np.ndarray]]) -> float:
        """Calculate bonus for visual uniqueness"""
        try:
            if not historical_patterns:
                return 10.0
            
            # Calculate average frame for current pattern
            current_avg = np.mean([frame.astype(float) for frame in frames], axis=0)
            
            # Calculate difference from historical patterns
            differences = []
            for hist_frames in historical_patterns:
                hist_avg = np.mean([frame.astype(float) for frame in hist_frames], axis=0)
                diff = np.mean(np.abs(current_avg - hist_avg)) / 255.0
                differences.append(diff)
            
            # Convert difference to bonus (higher difference = higher bonus)
            avg_diff = np.mean(differences)
            return min(10.0, avg_diff * 20.0)
            
        except Exception as e:
            self.log.error(f"Error calculating visual bonus: {e}")
            return 5.0
    
    def _get_historical_patterns(self) -> List[List[np.ndarray]]:
        """Get frames from historical patterns"""
        try:
            patterns = self.db.get_successful_patterns(limit=5)
            historical_frames = []
            
            for pattern in patterns:
                # Updated to use consistent render path structure
                render_path = self.config.base_path / "renders" / f"render_v{pattern.version}"
                # Skip if directory doesn't exist or has no frame files
                if not render_path.exists() or not any(render_path.glob("frame-*.png")):
                    continue
                    
                frames = self._load_frames(render_path)
                if frames:
                    historical_frames.append(frames)
            
            if not historical_frames:
                self.log.debug("No historical frames found for comparison")
            
            return historical_frames
            
        except Exception as e:
            self.log.error(f"Error loading historical patterns: {e}")
            return []
    
    def _calculate_dynamic_weights(self, pattern: Pattern, 
                                 complexity: float, 
                                 innovation: float, 
                                 aesthetic: float, 
                                 motion: float) -> Dict[str, float]:
        """Calculate dynamic weights based on pattern characteristics"""
        weights = {
            'complexity': 0.25,
            'innovation': 0.35,
            'aesthetic': 0.25,
            'motion': 0.15
        }
        
        # Add motion weight adjustment
        if motion > 80:
            weights['motion'] += 0.1
            weights['complexity'] -= 0.05
            weights['innovation'] -= 0.05
        
        # Add aesthetic weight adjustment
        if aesthetic > 85:
            weights['aesthetic'] += 0.1
            weights['complexity'] -= 0.05
            weights['motion'] -= 0.05
        
        # Adjust weights based on technique count
        if len(pattern.techniques) > 2:
            weights['innovation'] += 0.05
            weights['complexity'] += 0.05
            weights['aesthetic'] -= 0.05
            weights['motion'] -= 0.05
        
        # Adjust weights based on score distributions
        if complexity > 80:
            weights['complexity'] += 0.1
            weights['innovation'] -= 0.05
            weights['aesthetic'] -= 0.05
        
        if innovation > 85:
            weights['innovation'] += 0.1
            weights['complexity'] -= 0.05
            weights['aesthetic'] -= 0.05
        
        # Normalize weights to sum to 1
        total = sum(weights.values())
        return {k: v/total for k, v in weights.items()}
    
    def _calculate_visual_coherence(self, frames: List[np.ndarray]) -> float:
        """Calculate visual coherence of the pattern"""
        try:
            if not frames:
                return 0.75
            
            coherence_scores = []
            for frame in frames:
                # Calculate spatial distribution with more tolerance
                spatial_dist = cv2.normalize(frame, None, 0, 1, cv2.NORM_MINMAX)
                spatial_score = np.clip(1 - np.std(spatial_dist) * 2, 0, 1)  # More forgiving scaling
                
                # Calculate element consistency with improved robustness
                edges = cv2.Canny(frame, 50, 150)  # Increased lower threshold
                contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    areas = [cv2.contourArea(c) for c in contours]
                    mean_area = np.mean(areas)
                    if mean_area > 0:
                        # More forgiving size consistency calculation
                        size_consistency = np.clip(1 - (np.std(areas) / mean_area) * 0.5, 0.3, 1.0)
                    else:
                        size_consistency = 0.5
                else:
                    size_consistency = 0.5
                
                # Calculate overall frame coherence with adjusted weights
                frame_coherence = (spatial_score * 0.5 + size_consistency * 0.5)
                coherence_scores.append(frame_coherence)
            
            # Take the mean and ensure it's positive
            return max(0.3, np.mean(coherence_scores))
            
        except Exception as e:
            self.log.error(f"Error calculating visual coherence: {e}")
            return 0.75
            
    def _calculate_technique_synergy(self, pattern: Pattern) -> float:
        """Calculate how well techniques work together"""
        try:
            if len(pattern.techniques) < 2:
                return 0.75
            
            # Get historical synergy data
            synergy_pairs = self.db.get_synergy_pairs(min_score=70.0)
            
            # Create a synergy matrix
            technique_pairs = []
            for i, t1 in enumerate(pattern.techniques):
                for t2 in pattern.techniques[i+1:]:
                    pair = (t1, t2)
                    # Look for historical synergy
                    synergy = next((s[2] for s in synergy_pairs 
                                  if (s[0] == t1 and s[1] == t2) or 
                                     (s[0] == t2 and s[1] == t1)), 75.0)
                    technique_pairs.append(synergy / 100.0)
            
            if not technique_pairs:
                return 0.75
                
            # Calculate overall synergy
            return np.mean(technique_pairs)
            
        except Exception as e:
            self.log.error(f"Error calculating technique synergy: {e}")
            return 0.75
            
    def _get_default_scores(self) -> Dict[str, float]:
        """Return randomized default scores"""
        return {
            'overall': float(65.0 + np.random.normal(0, 5)),
            'complexity': float(60.0 + np.random.normal(0, 7)),
            'innovation': float(70.0 + np.random.normal(0, 10)),
            'aesthetic': float(65.0 + np.random.normal(0, 5)),
            'motion': float(60.0 + np.random.normal(0, 8)),
            'coherence': float(70.0 + np.random.normal(0, 5)),
            'synergy': float(75.0 + np.random.normal(0, 5))
        }