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
            tech_stats = self.db.get_technique_stats()
            
            # Get successful synergy pairs
            synergy_pairs = self.db.get_synergy_pairs(min_score=80.0)
            
            # Determine if we're generating for Flux (static) or Processing (animation)
            is_static = self.config.model_config.get('model_selection') == 'flux'
            
            # Select 1-4 techniques with better distribution
            # For static images, prefer 2-3 techniques for better composition
            if is_static:
                num_techniques = random.randint(2, 3)
            else:
                num_techniques = random.randint(1, 4)
            
            # Create weighted pool of techniques
            technique_pool = []
            for category, techniques in categories.items():
                for tech in techniques:
                    weight = 1.0
                    if tech in tech_stats:
                        stats = tech_stats[tech]
                        # Enhanced weighting based on comprehensive metrics
                        performance_weight = (
                            stats['avg_score'] / 100 * 0.4 +
                            stats['success_rate'] * 0.3 +
                            stats['innovation_factor'] * 0.3
                        )
                        weight *= performance_weight
                        
                        # For static images, boost visual techniques
                        if is_static and any(x in tech.lower() for x in ['color', 'pattern', 'texture', 'composition']):
                            weight *= 1.3
                        
                        # Boost weight based on adaptation rate
                        if stats.get('adaptation_rate', 1.0) > 1.1:
                            weight *= 1.2
                        
                        # Boost weight for techniques with good synergy history
                        synergy_bonus = any(
                            s[2] >= 85.0 for s in synergy_pairs
                            if s[0] == tech or s[1] == tech
                        )
                        if synergy_bonus:
                            weight *= 1.3
                    
                    technique_pool.append((tech, category, weight))
            
            # Select first technique with preference for high performers
            weights = [t[2] for t in technique_pool]
            first_choice = random.choices(technique_pool, weights=weights, k=1)[0]
            selected = [first_choice]
            
            # If only selecting one technique, return now
            if num_techniques == 1:
                return [self._create_technique(first_choice[0], first_choice[1])]
            
            # Filter pool for synergistic choices if selecting multiple
            remaining_pool = []
            first_tech = first_choice[0]
            for tech, category, weight in technique_pool:
                if tech != first_tech:
                    # Check synergy with first technique
                    synergy_score = next(
                        (s[2] for s in synergy_pairs 
                         if (s[0] == first_tech and s[1] == tech) or 
                            (s[0] == tech and s[1] == first_tech)),
                        75.0
                    )
                    # Boost weight based on synergy
                    synergy_weight = weight * (synergy_score / 75.0)
                    remaining_pool.append((tech, category, synergy_weight))
            
            # Select remaining techniques
            while len(selected) < num_techniques and remaining_pool:
                weights = [t[2] for t in remaining_pool]
                chosen = random.choices(remaining_pool, weights=weights, k=1)[0]
                selected.append(chosen)
                
                # Update remaining pool based on synergy with all selected techniques
                new_pool = []
                for tech, category, weight in remaining_pool:
                    if tech != chosen[0]:
                        # Calculate average synergy with all selected techniques
                        synergies = []
                        for selected_tech, _, _ in selected:
                            synergy_score = next(
                                (s[2] for s in synergy_pairs 
                                 if (s[0] == selected_tech and s[1] == tech) or 
                                    (s[0] == tech and s[1] == selected_tech)),
                                75.0
                            )
                            synergies.append(synergy_score)
                        avg_synergy = sum(synergies) / len(synergies)
                        # Update weight based on average synergy
                        synergy_weight = weight * (avg_synergy / 75.0)
                        new_pool.append((tech, category, synergy_weight))
                remaining_pool = new_pool
            
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
        """Evolve a technique based on its performance with enhanced metrics"""
        try:
            # Get historical synergy data
            synergy_pairs = self.db.get_synergy_pairs(min_score=70.0)
            
            # Add combined techniques data for synergy tracking
            combined_techniques = [t for t in technique.synergy_scores.keys()]
            performance['combined_techniques'] = combined_techniques
            
            # Check if this was a static image generation
            is_static = self.config.model_config.get('model_selection') == 'flux'
            if is_static:
                # For static images, adjust evolution metrics
                performance['aesthetic_weight'] = 1.2  # Boost aesthetic importance
                performance['motion_weight'] = 0.1    # Reduce motion importance
                performance['complexity_weight'] = 1.1 # Slightly boost complexity
            
            # Create evolved version with enhanced learning
            evolved = technique.evolve(performance)
            
            # Update technique stats in database
            self.db.save_technique(evolved)
            
            # Update synergy pairs in database
            for other_tech in combined_techniques:
                synergy_score = evolved.get_synergy_score(other_tech)
                self.db.update_synergy_pair(evolved.name, other_tech, synergy_score)
            
            return evolved
            
        except Exception as e:
            self.log.error(f"Error evolving technique: {e}")
            return technique
    
    def update_technique_scores(self, pattern: Pattern) -> None:
        """Update technique performance statistics"""
        try:
            # Get existing technique stats
            tech_stats = self.db.get_technique_stats()
            
            for technique_name in pattern.techniques:
                # Get the category for this technique
                category = self._get_category_name(technique_name, self.config.technique_categories)
                
                # Get existing stats or use defaults
                existing_stats = tech_stats.get(technique_name, {})
                usage_count = existing_stats.get('usage_count', 0) + 1
                old_avg_score = existing_stats.get('avg_score', 75.0)
                
                # Calculate new averages
                new_avg_score = ((old_avg_score * (usage_count - 1)) + pattern.score) / usage_count
                new_success_rate = ((existing_stats.get('success_rate', 0.75) * (usage_count - 1)) + 
                                  (pattern.score / 100)) / usage_count
                
                # Create updated technique stats
                technique = Technique(
                    name=technique_name,
                    description="",
                    parameters={},
                    mathematical_concepts=[technique_name],
                    emergent_behaviors=[],
                    success_rate=new_success_rate,
                    usage_count=usage_count,
                    avg_score=new_avg_score,
                    aesthetic_score=pattern.aesthetic_score,
                    complexity_score=pattern.mathematical_complexity,
                    innovation_factor=existing_stats.get('innovation_factor', 1.0),
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