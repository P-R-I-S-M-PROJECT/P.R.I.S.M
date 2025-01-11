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
        conn = self.db.get_connection()
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
        conn.close()
        
    def update(self, pattern: Optional[Pattern]):
        """Update documentation with enhanced analysis"""
        if pattern is None:
            self.log.error("No pattern provided for documentation update")
            return

        try:
            self.log.analysis_header(f"Analyzing Pattern v{pattern.version}")
            
            # Get historical context
            self.log.processing_step("Gathering historical context")
            recent_patterns = self.db.get_recent_patterns(limit=6)
            pattern_lineage = self.db.get_pattern_lineage(pattern.version)
            technique_stats = self.db.get_technique_stats()
            self.log.processing_step("Historical context gathered", "complete")
        
            # Generate analysis
            self.log.processing_step("Generating comprehensive analysis")
            analysis = self._analyze_pattern(pattern, recent_patterns, pattern_lineage, technique_stats)
        
            if not analysis:
                self.log.error("Failed to generate pattern analysis")
                return
            
            self.log.processing_step("Analysis generation complete", "complete")
            
            # Display insights
            if isinstance(analysis.get('technical_analysis'), str):
                self.log.insight("Technical", analysis.get('technical_analysis', '').split('.')[0])
            elif isinstance(analysis.get('technical_analysis'), dict):
                self.log.insight("Technical", str(analysis.get('technical_analysis')))
            
            if isinstance(analysis.get('aesthetic_analysis'), str):
                self.log.insight("Aesthetic", analysis.get('aesthetic_analysis', '').split('.')[0])
            elif isinstance(analysis.get('aesthetic_analysis'), dict):
                self.log.insight("Aesthetic", str(analysis.get('aesthetic_analysis')))
            
            if analysis.get('evolution_analysis'):
                if isinstance(analysis.get('evolution_analysis'), str):
                    self.log.insight("Evolution", analysis.get('evolution_analysis', '').split('.')[0])
                elif isinstance(analysis.get('evolution_analysis'), dict):
                    self.log.insight("Evolution", str(analysis.get('evolution_analysis')))
        
            # Save pattern analysis
            self.log.processing_step("Saving pattern analysis")
            self._save_pattern_analysis(pattern.version, analysis)
            self.log.processing_step("Pattern analysis saved", "complete")
            
            # Update technique insights
            self.log.processing_step("Updating technique insights")
            self._update_technique_insights(pattern, analysis)
            
            # Show technique analysis
            for technique in pattern.techniques:
                if technique in technique_stats:
                    self.log.technique_analysis(technique, technique_stats[technique])
            
            # Generate and save evolution insights
            if len(pattern_lineage) > 1:
                self.log.processing_step("Generating evolution insights")
                self._generate_evolution_insights(pattern, pattern_lineage)
                
                # Show evolution trace
                steps = [f"v{p.version}: Score={p.score:.1f}" for p in pattern_lineage]
                steps.append(f"v{pattern.version}: Score={pattern.score:.1f} (Current)")
                self.log.evolution_trace(steps)
                
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
            
            # Extract the content from the response object correctly
            analysis = json.loads(response.choices[0].message.content)
            if not isinstance(analysis, dict):
                self.log.error("API returned non-dictionary response")
                return self._get_default_analysis(pattern)
            return analysis
            
        except Exception as e:
            self.log.error(f"Error generating analysis: {e}")
            return self._get_default_analysis(pattern)
    
    def _save_pattern_analysis(self, version: int, analysis: Dict):
        """Save pattern analysis to database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Convert dictionary values to JSON strings if needed
        technical_analysis = (
            json.dumps(analysis.get('technical_analysis'))
            if isinstance(analysis.get('technical_analysis'), dict)
            else str(analysis.get('technical_analysis', ''))
        )
        
        technical_insights = (
            json.dumps(analysis.get('technical_insights'))
            if isinstance(analysis.get('technical_insights'), dict)
            else str(analysis.get('technical_insights', ''))
        )
        
        aesthetic_analysis = (
            json.dumps(analysis.get('aesthetic_analysis'))
            if isinstance(analysis.get('aesthetic_analysis'), dict)
            else str(analysis.get('aesthetic_analysis', ''))
        )
        
        evolution_analysis = (
            json.dumps(analysis.get('evolution_analysis'))
            if isinstance(analysis.get('evolution_analysis'), dict)
            else str(analysis.get('evolution_analysis', ''))
        )
        
        technique_insights = (
            json.dumps(analysis.get('technique_insights'))
            if isinstance(analysis.get('technique_insights'), dict)
            else str(analysis.get('technique_insights', ''))
        )
        
        cursor.execute("""
            INSERT INTO pattern_analysis (
                pattern_version, timestamp, analysis_text,
                technical_insights, aesthetic_notes,
                evolution_notes, technique_observations, tags
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version,
            datetime.now().isoformat(),
            technical_analysis,
            technical_insights,
            aesthetic_analysis,
            evolution_analysis,
            technique_insights,
            json.dumps(analysis.get('tags', []))
        ))
        conn.commit()
        conn.close()
    
    def _update_technique_insights(self, pattern: Pattern, analysis: Dict):
        """Update technique-specific insights"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        technique_insights = analysis.get('technique_insights', {})
        if isinstance(technique_insights, str):
            technique_insights = {t: technique_insights for t in pattern.techniques}
        
        for technique in pattern.techniques:
            insight = technique_insights.get(technique, f"Used in pattern v{pattern.version}")
            cursor.execute("""
                INSERT INTO technique_insights (
                    technique, timestamp, insight_type,
                    insight_text, related_patterns, confidence_score
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                technique,
                datetime.now().isoformat(),
                'performance_analysis',
                insight,
                json.dumps([pattern.version]),
                0.85
            ))
        
        conn.commit()
        conn.close()
    
    def _generate_evolution_insights(self, pattern: Pattern, lineage: List[Pattern]):
        """Generate and save insights about pattern evolution"""
        try:
            # Analyze evolution trends including current pattern
            trends = self._analyze_evolution_trends([*lineage, pattern])
            
            conn = self.db.get_connection()
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
            conn.close()
                
        except Exception as e:
            self.log.error(f"Error generating evolution insights: {e}")
    
    def get_pattern_documentation(self, version: int) -> Dict:
        """Get comprehensive documentation for a pattern"""
        conn = self.db.get_connection()
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
        conn.close()
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
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, insight_type, insight_text,
                   related_patterns, confidence_score
            FROM technique_insights
            WHERE technique = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (technique, limit))
        
        results = [{
            'timestamp': row[0],
            'type': row[1],
            'insight': row[2],
            'related_patterns': json.loads(row[3]),
            'confidence': row[4]
        } for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_evolution_insights(self, limit: int = 5) -> List[Dict]:
        """Get recent evolution insights"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, insight_type, insight_text,
                       patterns_involved, techniques_involved, significance_score
                FROM evolution_insights
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = [{
                'timestamp': row[0],
                'type': row[1],
                'insight': row[2],
                'patterns': json.loads(row[3]),
                'techniques': json.loads(row[4]),
                'significance': row[5]
            } for row in cursor.fetchall()]
            return results
        finally:
            conn.close()
    
    def _build_analysis_context(self, pattern: Pattern, recent_patterns: List[Pattern],
                              lineage: List[Pattern], technique_stats: Dict) -> str:
        """Build rich context for pattern analysis"""
        # Get synergy data for techniques
        synergy_pairs = self.db.get_synergy_pairs(min_score=70.0)
        
        context = [
            f"Pattern Version: {pattern.version}",
            f"Techniques: {', '.join(pattern.techniques)}",
            f"\nPerformance Metrics:",
            f"Overall Score: {pattern.score:.1f}",
            f"Innovation: {pattern.innovation_score:.1f}",
            f"Aesthetic: {pattern.aesthetic_score:.1f}",
            f"Complexity: {pattern.mathematical_complexity:.1f}",
            f"Motion: {pattern.motion_quality:.1f}",
            f"Visual Coherence: {pattern.visual_coherence:.1f}",
            f"Technique Synergy: {pattern.technique_synergy:.1f}",
            
            "\nTechnique Synergies:",
            *[f"{s[0]} + {s[1]}: {s[2]:.1f}" for s in synergy_pairs 
              if s[0] in pattern.techniques and s[1] in pattern.techniques],
            
            "\nEvolution Chain:",
            *[f"v{p.version}: Score={p.score:.1f}, Innovation={p.innovation_score:.1f}" 
              for p in lineage],
            
            "\nTechnique Performance:",
            *[f"{tech}: Usage={stats['usage_count']}, "
              f"Avg Score={stats['avg_score']:.1f}, "
              f"Success Rate={stats['success_rate']:.2f}, "
              f"Innovation Factor={stats['innovation_factor']:.2f}"
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
        innovation_trend = sum(p.innovation_score for p in lineage[-3:]) / 3 - sum(p.innovation_score for p in lineage[:3]) / 3
        coherence_trend = sum(p.visual_coherence for p in lineage[-3:]) / 3 - sum(p.visual_coherence for p in lineage[:3]) / 3
        
        # Analyze technique evolution
        all_techniques = set(sum([p.techniques for p in lineage], []))
        technique_diversity = len(all_techniques)
        
        # Calculate significance based on multiple factors
        significance = min(1.0, (
            abs(score_trend) / 20 +
            abs(innovation_trend) / 20 +
            abs(coherence_trend) / 20 +
            technique_diversity / 10
        ) / 4)
        
        # Generate detailed analysis
        trends = []
        if score_trend > 2:
            trends.append("significant improvement in overall quality")
        elif score_trend < -2:
            trends.append("decline in overall quality")
            
        if innovation_trend > 2:
            trends.append("increasing innovation")
        elif innovation_trend < -2:
            trends.append("decreasing innovation")
            
        if coherence_trend > 2:
            trends.append("improving visual coherence")
        elif coherence_trend < -2:
            trends.append("declining visual coherence")
            
        if technique_diversity >= 5:
            trends.append("high technique diversity")
        elif technique_diversity <= 2:
            trends.append("limited technique exploration")
        
        analysis = f"Pattern evolution shows {', '.join(trends)}. " \
                  f"Score trend: {score_trend:+.1f}, " \
                  f"Innovation trend: {innovation_trend:+.1f}, " \
                  f"Coherence trend: {coherence_trend:+.1f}"
        
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