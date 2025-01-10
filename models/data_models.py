from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
import random

@dataclass
class Pattern:
    """Represents a generated pattern with enhanced evolutionary tracking"""
    version: int
    code: str
    timestamp: datetime
    techniques: List[str]
    score: float = 75.0
    innovation_score: float = 75.0
    aesthetic_score: float = 75.0
    mathematical_complexity: float = 75.0
    motion_quality: float = 75.0
    visual_coherence: float = 75.0  # New: Measure how well elements work together
    technique_synergy: float = 75.0  # New: How well techniques complement each other
    evolution_chain: List[int] = field(default_factory=list)  # New: Track pattern lineage
    parent_patterns: List[int] = field(default_factory=list)  # New: Patterns this evolved from
    
    def get_metrics(self) -> Dict[str, float]:
        """Get all pattern metrics including new evolution metrics"""
        return {
            'score': self.score,
            'innovation': self.innovation_score,
            'aesthetic': self.aesthetic_score,
            'complexity': self.mathematical_complexity,
            'motion': self.motion_quality,
            'coherence': self.visual_coherence,
            'synergy': self.technique_synergy
        }
    
    def update_scores(self, metrics: Dict[str, float]):
        """Update pattern scores with evolution tracking"""
        self.score = metrics.get('overall', self.score)
        self.innovation_score = metrics.get('innovation', self.innovation_score)
        self.aesthetic_score = metrics.get('aesthetic', self.aesthetic_score)
        self.mathematical_complexity = metrics.get('complexity', self.mathematical_complexity)
        self.motion_quality = metrics.get('motion', self.motion_quality)
        self.visual_coherence = metrics.get('coherence', self.visual_coherence)
        self.technique_synergy = metrics.get('synergy', self.technique_synergy)
    
    def add_to_evolution_chain(self, parent_version: int):
        """Track pattern evolution history"""
        if parent_version not in self.parent_patterns:
            self.parent_patterns.append(parent_version)
        self.evolution_chain = self.parent_patterns + [self.version]

@dataclass
class Technique:
    """Represents a creative technique with enhanced evolution tracking"""
    name: str
    description: str
    parameters: Dict[str, Any]
    mathematical_concepts: List[str]
    category: str
    emergent_behaviors: List[str] = field(default_factory=list)
    success_rate: float = 0.75
    usage_count: int = 0
    avg_score: float = 75.0
    aesthetic_score: float = 75.0
    complexity_score: float = 75.0
    innovation_factor: float = 1.0
    last_used: Optional[datetime] = None
    synergy_scores: Dict[str, float] = field(default_factory=dict)  # New: Track technique combinations
    evolution_history: List[Dict[str, float]] = field(default_factory=list)  # New: Track score evolution
    adaptation_rate: float = 1.0  # New: How quickly technique adapts to feedback
    
    def evolve(self, performance: Dict[str, float]) -> 'Technique':
        """Create evolved version with enhanced learning"""
        score = performance.get('overall', 75.0)
        
        # Track historical performance
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'score': score,
            'aesthetic': performance.get('aesthetic', 75.0),
            'complexity': performance.get('complexity', 75.0),
            'innovation': performance.get('innovation', 75.0)
        })
        
        # Adaptive learning rate based on performance stability
        if len(self.evolution_history) > 5:
            recent_scores = [h['score'] for h in self.evolution_history[-5:]]
            score_stability = np.std(recent_scores)
            self.adaptation_rate = 1.0 / (1.0 + score_stability)  # Lower rate if unstable
        
        # Weighted average with adaptation rate
        new_success_rate = (
            (self.success_rate * self.usage_count + (score / 100) * self.adaptation_rate) / 
            (self.usage_count + self.adaptation_rate)
        )
        
        new_avg_score = (
            (self.avg_score * self.usage_count + score * self.adaptation_rate) / 
            (self.usage_count + self.adaptation_rate)
        )
        
        # Update synergy scores with other techniques
        for other_tech in performance.get('combined_techniques', []):
            if other_tech != self.name:
                current_synergy = self.synergy_scores.get(other_tech, 75.0)
                self.synergy_scores[other_tech] = (
                    current_synergy * 0.8 + score * 0.2  # Blend old and new scores
                )
        
        return Technique(
            name=self.name,
            description=self.description,
            parameters=self.parameters.copy(),
            mathematical_concepts=self.mathematical_concepts,
            category=self.category,
            emergent_behaviors=self.emergent_behaviors,
            success_rate=new_success_rate,
            usage_count=self.usage_count + 1,
            avg_score=new_avg_score,
            aesthetic_score=performance.get('aesthetic', 75.0),
            complexity_score=performance.get('complexity', 75.0),
            innovation_factor=self.innovation_factor * (1.1 if performance.get('innovation', 0) > 80 else 1.0),
            last_used=datetime.now(),
            synergy_scores=self.synergy_scores.copy(),
            evolution_history=self.evolution_history.copy(),
            adaptation_rate=self.adaptation_rate
        )
    
    def get_synergy_score(self, other_technique: str) -> float:
        """Get the synergy score with another technique"""
        return self.synergy_scores.get(other_technique, 75.0)
    
    def get_evolution_trend(self, metric: str = 'score', window: int = 5) -> float:
        """Calculate the trend of a metric over recent evolution history"""
        if len(self.evolution_history) < 2:
            return 0.0
        
        recent = self.evolution_history[-window:]
        values = [h[metric] for h in recent if metric in h]
        if len(values) < 2:
            return 0.0
            
        # Calculate trend using linear regression slope
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        return slope

@dataclass
class StyleVariation:
    """Represents a visual style configuration with evolution tracking"""
    name: str
    background: int = 0
    stroke: int = 255
    stroke_weight: float = 1.0
    fill_enabled: bool = False
    success_rate: float = 0.75
    usage_count: int = 0
    avg_score: float = 75.0
    color_harmony: Dict[str, List[int]] = field(default_factory=dict)  # New: Track successful color combinations
    style_evolution: List[Dict[str, Any]] = field(default_factory=list)  # New: Track style changes
    
    def to_processing_code(self) -> str:
        """Convert style to Processing code"""
        code = []
        
        # Set fill
        if not self.fill_enabled:
            code.append("noFill();")
        else:
            # Use successful color harmonies if available
            if self.color_harmony:
                harmony = random.choice(list(self.color_harmony.values()))
                code.append(f"fill({','.join(map(str, harmony))});")
        
        # Set stroke
        code.append(f"stroke({self.stroke});")
        code.append(f"strokeWeight({self.stroke_weight});")
        
        return "\n".join(code)
    
    def evolve_style(self, performance: Dict[str, float]) -> 'StyleVariation':
        """Evolve style based on performance"""
        # Track style evolution
        self.style_evolution.append({
            'timestamp': datetime.now().isoformat(),
            'performance': performance,
            'style': {
                'background': self.background,
                'stroke': self.stroke,
                'stroke_weight': self.stroke_weight,
                'fill_enabled': self.fill_enabled
            }
        })
        
        # Update success metrics
        new_success_rate = (self.success_rate * self.usage_count + performance.get('overall', 75.0) / 100) / (self.usage_count + 1)
        new_avg_score = (self.avg_score * self.usage_count + performance.get('overall', 75.0)) / (self.usage_count + 1)
        
        return StyleVariation(
            name=self.name,
            background=self.background,
            stroke=self.stroke,
            stroke_weight=self.stroke_weight,
            fill_enabled=self.fill_enabled,
            success_rate=new_success_rate,
            usage_count=self.usage_count + 1,
            avg_score=new_avg_score,
            color_harmony=self.color_harmony.copy(),
            style_evolution=self.style_evolution.copy()
        ) 