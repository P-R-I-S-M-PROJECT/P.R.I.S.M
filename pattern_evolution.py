from typing import List, Dict, Any
from config import Config
from models import Pattern, Technique
from logger import ArtLogger
from datetime import datetime
import numpy as np
import random

class PatternEvolution:
    def __init__(self, config: Config, logger: ArtLogger = None):
        self.config = config
        self.db = config.db_manager
        self.log = logger or ArtLogger()
        self.params: Dict[str, Any] = config.metadata['parameters']
        
    def select_techniques(self) -> List[Technique]:
        """Select techniques with improved constraints and combinations"""
        try:
            categories = self.config.technique_categories
            
            # Select 2-4 techniques with better distribution
            num_techniques = random.randint(1, 4)
            
            # Ensure at least one geometry or pattern technique
            selected_categories = []
            if random.random() < 0.8:  # 80% chance to include geometry
                selected_categories.append('geometry')
            if random.random() < 0.7:  # 70% chance to include patterns
                selected_categories.append('patterns')
            if random.random() < 0.6:  # 60% chance to include motion
                selected_categories.append('motion')
                
            # If nothing selected, force at least one category
            if not selected_categories:
                selected_categories = [random.choice(['geometry', 'patterns'])]
            
            # Create weighted pool of techniques
            technique_pool = []
            for category in selected_categories:
                techniques = categories[category]
                # Get historical performance for weighting
                tech_stats = self.db.get_technique_stats()
                
                for tech in techniques:
                    weight = 1.0
                    if tech in tech_stats:
                        stats = tech_stats[tech]
                        # Boost weight for successful techniques
                        if stats['avg_score'] > 80:
                            weight *= 1.2
                        if stats['success_rate'] > 0.8:
                            weight *= 1.1
                    technique_pool.append((tech, category, weight))
            
            # Select techniques with weights
            selected = []
            while len(selected) < num_techniques and technique_pool:
                weights = [t[2] for t in technique_pool]
                chosen = random.choices(technique_pool, weights=weights, k=1)[0]
                selected.append(chosen)
                # Remove chosen technique and others from same category if we want variety
                technique_pool = [t for t in technique_pool if t[0] != chosen[0]]
                if len(selected) >= 2:  # After 2 selections, maybe remove same category
                    if random.random() < 0.7:  # 70% chance to force category variety
                        technique_pool = [t for t in technique_pool if t[1] != chosen[1]]
            
            return [self._create_technique(tech_name, category) 
                   for tech_name, category, _ in selected]
            
        except Exception as e:
            self.log.error(f"Error selecting techniques: {e}")
            return []
    
    def _create_technique(self, name: str, category: str) -> Technique:
        """Helper to create a technique object with better initial scores"""
        # Get historical stats if available
        tech_stats = self.db.get_technique_stats()
        
        if name in tech_stats:
            stats = tech_stats[name]
            return Technique(
                name=name,
                description="",
                parameters={},
                mathematical_concepts=[name],
                emergent_behaviors=[],
                success_rate=stats['success_rate'],
                usage_count=stats['usage_count'],
                avg_score=stats['avg_score'],
                aesthetic_score=max(75.0, stats['avg_score']),
                complexity_score=max(75.0, stats['avg_score'] * 0.9),
                innovation_factor=1.1 if stats['avg_score'] > 80 else 1.0,
                last_used=datetime.now(),
                category=category
            )
        
        # For new techniques, start with optimistic scores
        return Technique(
            name=name,
            description="",
            parameters={},
            mathematical_concepts=[name],
            emergent_behaviors=[],
            success_rate=0.8,
            usage_count=0,
            avg_score=80.0,
            aesthetic_score=80.0,
            complexity_score=80.0,
            innovation_factor=1.2,  # Higher innovation for new techniques
            last_used=datetime.now(),
            category=category
        )
    
    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for techniques"""
        return {
            'scale': 1.0,
            'speed': 1.0,
            'complexity': 0.7,
            'variation': 0.3
        }
    
    def evolve_technique(self, technique: Technique, performance: Dict[str, float]) -> Technique:
        """Evolve a technique based on its performance"""
        try:
            # Create evolved version with 'overall' instead of 'score'
            evolved = Technique(
                name=technique.name,
                description=technique.description,
                parameters=technique.parameters.copy(),
                mathematical_concepts=technique.mathematical_concepts,
                emergent_behaviors=technique.emergent_behaviors,
                success_rate=performance.get('overall', 75.0) / 100,
                usage_count=technique.usage_count + 1,
                avg_score=performance.get('overall', 75.0),
                aesthetic_score=performance.get('aesthetic', 75.0),
                complexity_score=performance.get('complexity', 75.0),
                innovation_factor=technique.innovation_factor * (1.1 if performance.get('innovation', 0) > 80 else 1.0),
                last_used=datetime.now(),
                category=technique.category
            )
            
            return evolved
            
        except Exception as e:
            self.log.error(f"Error evolving technique: {e}")
            return technique
    
    def update_technique_scores(self, pattern: Pattern) -> None:
        """Update technique performance statistics"""
        try:
            for technique_name in pattern.techniques:
                # Get the category for this technique
                category = self._get_category_name(technique_name, self.config.technique_categories)
                
                # Create basic technique stats with category
                technique = Technique(
                    name=technique_name,
                    description="",
                    parameters={},
                    mathematical_concepts=[technique_name],
                    emergent_behaviors=[],
                    success_rate=pattern.score / 100,
                    usage_count=1,
                    avg_score=pattern.score,
                    aesthetic_score=pattern.aesthetic_score,
                    complexity_score=pattern.mathematical_complexity,
                    innovation_factor=pattern.innovation_score,
                    last_used=datetime.now(),
                    category=category
                )
                
                # Save updated stats
                self.db.save_technique(technique)
                
        except Exception as e:
            self.log.error(f"Error updating technique scores: {e}")
    
    def _get_category_name(self, technique: str, concepts: Dict) -> str:
        """Determine which category a technique belongs to"""
        for category, techniques in concepts.items():
            if technique in techniques:
                return category
        return "unknown"
    
    def _get_rotation_description(self, rotation: int) -> str:
        """Get human-readable description of current rotation"""
        descriptions = {
            0: "geometry concepts",
            1: "motion concepts",
            2: "pattern concepts",
            3: "geometry and motion combination",
            4: "motion and pattern combination",
            5: "geometry and pattern combination"
        }
        return descriptions.get(rotation, "mixed concepts")