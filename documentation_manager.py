import json
import re
from typing import Dict, List, Optional
import openai
from datetime import datetime
from models import Pattern
from logger import ArtLogger
from config import Config

class DocumentationManager:
    def __init__(self, config: Config, logger: ArtLogger = None):
        self.config = config
        self.db = config.db_manager
        self.log = logger or ArtLogger()
        self._init_db()
    
    def _init_db(self):
        """Initialize documentation tables"""
        with self.db.db_path.open() as conn:
            cursor = conn.cursor()
            
            # Create pattern_analysis table for detailed documentation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pattern_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_version INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL,
                    analysis_text TEXT NOT NULL,
                    technical_insights TEXT,
                    aesthetic_notes TEXT,
                    evolution_notes TEXT,
                    technique_observations TEXT,
                    tags TEXT,
                    FOREIGN KEY (pattern_version) REFERENCES patterns(version)
                )
            """)
            
            # Create technique_insights table for technique-specific documentation
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technique_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    technique TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    insight_type TEXT NOT NULL,
                    insight_text TEXT NOT NULL,
                    related_patterns TEXT,
                    confidence_score REAL DEFAULT 0.75,
                    FOREIGN KEY (technique) REFERENCES technique_stats(technique)
                )
            """)
            
            # Create evolution_insights table for tracking evolutionary patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evolution_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    insight_type TEXT NOT NULL,
                    insight_text TEXT NOT NULL,
                    patterns_involved TEXT,
                    techniques_involved TEXT,
                    significance_score REAL DEFAULT 0.75
                )
            """)
            
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pattern_analysis_version ON pattern_analysis(pattern_version)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_technique_insights_technique ON technique_insights(technique)")
            
            conn.commit()
    
    def update(self, pattern: Optional[Pattern]):
        """Update documentation with enhanced analysis"""
        if pattern is None:
            self.log.error("No pattern provided for documentation update")
            return

        try:
            # Get historical context
            recent_patterns = self.db.get_recent_patterns(limit=6)
            pattern_lineage = self.db.get_pattern_lineage(pattern.version)
            technique_stats = self.db.get_technique_stats()
            
            # Generate analysis
            analysis = self._analyze_pattern(pattern, recent_patterns, pattern_lineage, technique_stats)
            
            if not analysis:
                self.log.error("Failed to generate pattern analysis")
                return
            
            # Save pattern analysis
            self._save_pattern_analysis(pattern.version, analysis)
            
            # Update technique insights
            self._update_technique_insights(pattern, analysis)
            
            # Generate and save evolution insights
            if len(pattern_lineage) > 1:
                self._generate_evolution_insights(pattern, pattern_lineage)
            
        except Exception as e:
            self.log.error(f"Error updating documentation: {e}")
    
    def _analyze_pattern(self, pattern: Pattern, recent_patterns: List[Pattern], 
                        lineage: List[Pattern], technique_stats: Dict) -> Dict:
        """Generate comprehensive pattern analysis"""
        try:
            client = openai.OpenAI(api_key=self.config.api_key)
            
            # Build rich context for analysis
            context = self._build_analysis_context(pattern, recent_patterns, lineage, technique_stats)
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "system",
                    "content": """Analyze this generative art pattern and provide insights in JSON format with these keys:
                        - technical_analysis: Technical implementation details
                        - aesthetic_analysis: Visual and artistic qualities
                        - evolution_analysis: How it evolved from previous versions
                        - technique_insights: Specific insights about technique usage
                        - tags: Key concepts and characteristics"""
                }, {
                    "role": "user",
                    "content": context
                }],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            self.log.error(f"Error generating analysis: {e}")
            return self._get_default_analysis(pattern)
    
    def _save_pattern_analysis(self, version: int, analysis: Dict):
        """Save pattern analysis to database"""
        with self.db.db_path.open() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pattern_analysis (
                    pattern_version, timestamp, analysis_text,
                    technical_insights, aesthetic_notes,
                    evolution_notes, technique_observations, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version,
                datetime.now().isoformat(),
                analysis.get('technical_analysis', ''),
                analysis.get('technical_insights', ''),
                analysis.get('aesthetic_analysis', ''),
                analysis.get('evolution_analysis', ''),
                analysis.get('technique_insights', ''),
                json.dumps(analysis.get('tags', []))
            ))
            conn.commit()
    
    def _update_technique_insights(self, pattern: Pattern, analysis: Dict):
        """Update technique-specific insights"""
        with self.db.db_path.open() as conn:
            cursor = conn.cursor()
            
            for technique in pattern.techniques:
                if technique_insight := analysis.get('technique_insights', {}).get(technique):
                    cursor.execute("""
                        INSERT INTO technique_insights (
                            technique, timestamp, insight_type,
                            insight_text, related_patterns, confidence_score
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        technique,
                        datetime.now().isoformat(),
                        'performance_analysis',
                        technique_insight,
                        json.dumps([pattern.version]),
                        0.85
                    ))
            
            conn.commit()
    
    def _generate_evolution_insights(self, pattern: Pattern, lineage: List[Pattern]):
        """Generate and save insights about pattern evolution"""
        try:
            # Analyze evolution trends including current pattern
            trends = self._analyze_evolution_trends([*lineage, pattern])
            
            with self.db.db_path.open() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO evolution_insights (
                        timestamp, insight_type, insight_text,
                        patterns_involved, techniques_involved, significance_score
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.now().isoformat(),
                    'evolution_trend',
                    trends['analysis'],
                    json.dumps([p.version for p in [*lineage, pattern]]),
                    json.dumps(list(set(sum([p.techniques for p in [*lineage, pattern]], [])))),
                    trends['significance']
                ))
                conn.commit()
                
        except Exception as e:
            self.log.error(f"Error generating evolution insights: {e}")
    
    def get_pattern_documentation(self, version: int) -> Dict:
        """Get comprehensive documentation for a pattern"""
        with self.db.db_path.open() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT analysis_text, technical_insights, aesthetic_notes,
                       evolution_notes, technique_observations, tags
                FROM pattern_analysis
                WHERE pattern_version = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (version,))
            
            row = cursor.fetchone()
            if not row:
                return {}
            
            return {
                'analysis': row[0],
                'technical_insights': row[1],
                'aesthetic_notes': row[2],
                'evolution_notes': row[3],
                'technique_observations': row[4],
                'tags': json.loads(row[5])
            }
    
    def get_technique_insights(self, technique: str, limit: int = 5) -> List[Dict]:
        """Get historical insights for a technique"""
        with self.db.db_path.open() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, insight_type, insight_text,
                       related_patterns, confidence_score
                FROM technique_insights
                WHERE technique = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (technique, limit))
            
            return [{
                'timestamp': row[0],
                'type': row[1],
                'insight': row[2],
                'related_patterns': json.loads(row[3]),
                'confidence': row[4]
            } for row in cursor.fetchall()]
    
    def get_evolution_insights(self, limit: int = 5) -> List[Dict]:
        """Get recent evolution insights"""
        with self.db.db_path.open() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, insight_type, insight_text,
                       patterns_involved, techniques_involved, significance_score
                FROM evolution_insights
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [{
                'timestamp': row[0],
                'type': row[1],
                'insight': row[2],
                'patterns': json.loads(row[3]),
                'techniques': json.loads(row[4]),
                'significance': row[5]
            } for row in cursor.fetchall()]
    
    def _build_analysis_context(self, pattern: Pattern, recent_patterns: List[Pattern],
                              lineage: List[Pattern], technique_stats: Dict) -> str:
        """Build rich context for pattern analysis"""
        context = [
            f"Pattern Version: {pattern.version}",
            f"Techniques: {', '.join(pattern.techniques)}",
            f"Scores: Overall={pattern.score:.1f}, Innovation={pattern.innovation_score:.1f}, "
            f"Aesthetic={pattern.aesthetic_score:.1f}, Complexity={pattern.mathematical_complexity:.1f}",
            "\nRecent History:",
            *[f"v{p.version}: {', '.join(p.techniques)} - Score: {p.score:.1f}" 
              for p in recent_patterns],
            "\nEvolution Chain:",
            *[f"v{p.version}: Score={p.score:.1f}" for p in lineage],
            "\nTechnique Performance:",
            *[f"{tech}: Usage={stats['usage_count']}, Avg Score={stats['avg_score']:.1f}"
              for tech, stats in technique_stats.items() if tech in pattern.techniques]
        ]
        
        return "\n".join(context)
    
    def _analyze_evolution_trends(self, lineage: List[Pattern]) -> Dict:
        """Analyze evolution trends in pattern lineage"""
        if len(lineage) < 2:
            return {
                'analysis': "Insufficient history for trend analysis",
                'significance': 0.5
            }
        
        # Calculate trend metrics
        score_trend = sum(p.score for p in lineage[-3:]) / 3 - sum(p.score for p in lineage[:3]) / 3
        technique_diversity = len(set(sum([p.techniques for p in lineage], [])))
        
        significance = min(1.0, (abs(score_trend) / 20 + technique_diversity / 10) / 2)
        
        analysis = f"Pattern evolution shows {'positive' if score_trend > 0 else 'negative'} " \
                  f"score trend ({score_trend:.1f}) with {technique_diversity} unique techniques used."
        
        return {
            'analysis': analysis,
            'significance': significance
        }
    
    def _get_default_analysis(self, pattern: Pattern) -> Dict:
        """Generate default analysis when AI generation fails"""
        return {
            'technical_analysis': f"Pattern v{pattern.version} implements {', '.join(pattern.techniques)}",
            'aesthetic_analysis': f"Achieved aesthetic score of {pattern.aesthetic_score:.1f}",
            'evolution_analysis': "Evolution analysis unavailable",
            'technique_insights': {t: f"Used in pattern v{pattern.version}" for t in pattern.techniques},
            'tags': pattern.techniques
        }