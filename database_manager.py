from typing import List, Dict, Optional, Any
from datetime import datetime
import sqlite3
import json
from config import Config
from models import Pattern, Technique
from logger import ArtLogger
import threading
from functools import lru_cache

class DatabaseManager:
    def __init__(self, config: 'Config'):
        self.config = config
        self.db_path = config.database_path
        self.log = ArtLogger()
        self._cache = {}
        self._cache_lock = threading.Lock()
        self.init_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_db(self, force: bool = False):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if force:
                cursor.execute("DROP TABLE IF EXISTS patterns")
                cursor.execute("DROP TABLE IF EXISTS technique_stats")
                cursor.execute("DROP TABLE IF EXISTS evolution_history")
                cursor.execute("DROP TABLE IF EXISTS technique_synergy")
            
            # Create patterns table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    techniques TEXT,
                    model TEXT DEFAULT 'o1-mini',
                    score REAL DEFAULT 75.0,
                    innovation_score REAL DEFAULT 75.0,
                    aesthetic_score REAL DEFAULT 75.0,
                    mathematical_complexity REAL DEFAULT 75.0,
                    motion_quality REAL DEFAULT 75.0,
                    visual_coherence REAL DEFAULT 75.0,
                    technique_synergy REAL DEFAULT 75.0,
                    parent_patterns TEXT
                )
            """)
            
            # Create technique_stats if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technique_stats (
                    technique TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    avg_score REAL DEFAULT 75.0,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.75,
                    last_used DATETIME,
                    aesthetic_score REAL DEFAULT 75.0,
                    complexity_score REAL DEFAULT 75.0,
                    innovation_factor REAL DEFAULT 1.0,
                    adaptation_rate REAL DEFAULT 1.0
                )
            """)
            
            # Initialize technique categories if table is empty
            cursor.execute("SELECT COUNT(*) FROM technique_stats")
            if cursor.fetchone()[0] == 0:
                self._init_technique_categories(cursor)
            
            # Create evolution history table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evolution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    technique TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    score REAL,
                    aesthetic REAL,
                    complexity REAL,
                    innovation REAL,
                    FOREIGN KEY (technique) REFERENCES technique_stats(technique)
                )
            """)
            
            # Create technique synergy table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technique_synergy (
                    technique1 TEXT NOT NULL,
                    technique2 TEXT NOT NULL,
                    synergy_score REAL DEFAULT 75.0,
                    last_updated DATETIME,
                    usage_count INTEGER DEFAULT 0,
                    PRIMARY KEY (technique1, technique2),
                    FOREIGN KEY (technique1) REFERENCES technique_stats(technique),
                    FOREIGN KEY (technique2) REFERENCES technique_stats(technique)
                )
            """)
            
            # Create indices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_version ON patterns(version)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_patterns_score ON patterns(score)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evolution_technique ON evolution_history(technique)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evolution_timestamp ON evolution_history(timestamp)")
            
            conn.commit()
        finally:
            conn.close()
    
    def _init_technique_categories(self, cursor):
        """Initialize technique categories from config"""
        categories = self.config.technique_categories
        timestamp = datetime.now().isoformat()
        
        for category, techniques in categories.items():
            for technique in techniques:
                cursor.execute("""
                    INSERT OR IGNORE INTO technique_stats (
                        technique, category, last_used
                    ) VALUES (?, ?, ?)
                """, (technique, category, timestamp))
    
    @lru_cache(maxsize=32)
    def get_pattern(self, pattern_id: int) -> Optional[Pattern]:
        """Get pattern by ID with caching"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, code, timestamp, techniques, score,
                       innovation_score, aesthetic_score, mathematical_complexity,
                       motion_quality, visual_coherence, technique_synergy,
                       parent_patterns
                FROM patterns 
                WHERE id = ?
            """, (pattern_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            return Pattern(
                version=row[0],
                code=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                techniques=json.loads(row[3]) if row[3] else [],
                score=row[4],
                innovation_score=row[5],
                aesthetic_score=row[6],
                mathematical_complexity=row[7],
                motion_quality=row[8],
                visual_coherence=row[9],
                technique_synergy=row[10],
                parent_patterns=json.loads(row[11]) if row[11] else []
            )
        finally:
            conn.close()
    
    def get_recent_patterns(self, limit: int = 3) -> List[Pattern]:
        """Get most recent patterns"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, code, timestamp, techniques, score,
                       innovation_score, aesthetic_score, mathematical_complexity,
                       motion_quality, visual_coherence, technique_synergy,
                       parent_patterns
                FROM patterns 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            return [Pattern(
                version=row[0],
                code=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                techniques=json.loads(row[3]) if row[3] else [],
                score=row[4],
                innovation_score=row[5],
                aesthetic_score=row[6],
                mathematical_complexity=row[7],
                motion_quality=row[8],
                visual_coherence=row[9],
                technique_synergy=row[10],
                parent_patterns=json.loads(row[11]) if row[11] else []
            ) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_successful_patterns(self, min_score: float = 75.0, limit: int = 5) -> List[Pattern]:
        """Get patterns with score above threshold"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, code, timestamp, techniques, score,
                       innovation_score, aesthetic_score, mathematical_complexity,
                       motion_quality, visual_coherence, technique_synergy,
                       parent_patterns
                FROM patterns 
                WHERE score >= ?
                ORDER BY score DESC 
                LIMIT ?
            """, (min_score, limit))
            
            return [Pattern(
                version=row[0],
                code=row[1],
                timestamp=datetime.fromisoformat(row[2]),
                techniques=json.loads(row[3]) if row[3] else [],
                score=row[4],
                innovation_score=row[5],
                aesthetic_score=row[6],
                mathematical_complexity=row[7],
                motion_quality=row[8],
                visual_coherence=row[9],
                technique_synergy=row[10],
                parent_patterns=json.loads(row[11]) if row[11] else []
            ) for row in cursor.fetchall()]
    
    def get_technique_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get enhanced performance statistics for all techniques"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.technique, t.category, t.avg_score, t.usage_count,
                       t.success_rate, t.last_used, t.aesthetic_score,
                       t.complexity_score, t.innovation_factor, t.adaptation_rate,
                       (
                           SELECT GROUP_CONCAT(s.technique2 || ':' || s.synergy_score)
                           FROM technique_synergy s
                           WHERE s.technique1 = t.technique
                           AND s.synergy_score >= 80
                       ) as synergies
                FROM technique_stats t
                WHERE t.usage_count > 0
            """)
            
            stats = {}
            for row in cursor.fetchall():
                synergies = {}
                if row[10]:  # Process synergies
                    for pair in row[10].split(','):
                        tech, score = pair.split(':')
                        synergies[tech] = float(score)
                
                stats[row[0]] = {
                    'category': row[1],
                    'avg_score': row[2],
                    'usage_count': row[3],
                    'success_rate': row[4],
                    'last_used': row[5],
                    'aesthetic_score': row[6],
                    'complexity_score': row[7],
                    'innovation_factor': row[8],
                    'adaptation_rate': row[9],
                    'synergies': synergies
                }
            
            return stats
        finally:
            conn.close()
    
    def save_pattern(self, pattern: Pattern) -> int:
        """Save pattern with evolution tracking"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patterns (
                    version, code, timestamp, techniques, score,
                    innovation_score, aesthetic_score, mathematical_complexity,
                    motion_quality, visual_coherence, technique_synergy,
                    parent_patterns
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.version,
                pattern.code,
                pattern.timestamp.isoformat(),
                json.dumps(pattern.techniques),
                pattern.score,
                pattern.innovation_score,
                pattern.aesthetic_score,
                pattern.mathematical_complexity,
                pattern.motion_quality,
                pattern.visual_coherence,
                pattern.technique_synergy,
                json.dumps(pattern.parent_patterns)
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def save_technique(self, technique: Technique) -> None:
        """Save technique with evolution history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save main technique stats
            cursor.execute("""
                INSERT OR REPLACE INTO technique_stats (
                    technique, category, avg_score, usage_count, success_rate,
                    last_used, aesthetic_score, complexity_score,
                    innovation_factor, adaptation_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                technique.name,
                technique.category,
                technique.avg_score,
                technique.usage_count,
                technique.success_rate,
                technique.last_used.isoformat(),
                technique.aesthetic_score,
                technique.complexity_score,
                technique.innovation_factor,
                technique.adaptation_rate
            ))
            
            # Save evolution history
            if technique.evolution_history:
                latest_history = technique.evolution_history[-1]
                cursor.execute("""
                    INSERT INTO evolution_history (
                        technique, timestamp, score, aesthetic,
                        complexity, innovation
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    technique.name,
                    latest_history['timestamp'],
                    latest_history['score'],
                    latest_history['aesthetic'],
                    latest_history['complexity'],
                    latest_history['innovation']
                ))
            
            # Update synergy scores
            for other_tech, synergy_score in technique.synergy_scores.items():
                cursor.execute("""
                    INSERT OR REPLACE INTO technique_synergy (
                        technique1, technique2, synergy_score, last_updated
                    ) VALUES (?, ?, ?, ?)
                """, (
                    technique.name,
                    other_tech,
                    synergy_score,
                    datetime.now().isoformat()
                ))
    
    def get_technique_evolution(self, technique_name: str, limit: int = 10) -> List[Dict[str, float]]:
        """Get evolution history for a technique"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, score, aesthetic, complexity, innovation
                FROM evolution_history
                WHERE technique = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (technique_name, limit))
            
            return [{
                'timestamp': row[0],
                'score': row[1],
                'aesthetic': row[2],
                'complexity': row[3],
                'innovation': row[4]
            } for row in cursor.fetchall()]
    
    def get_synergy_pairs(self, min_score: float = 80.0) -> List[tuple[str, str, float]]:
        """Get technique pairs with high synergy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT technique1, technique2, synergy_score
                FROM technique_synergy
                WHERE synergy_score >= ?
                ORDER BY synergy_score DESC
            """, (min_score,))
            
            return cursor.fetchall()
    
    def get_pattern_lineage(self, version: int) -> List[Pattern]:
        """Get the evolution chain for a pattern"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                WITH RECURSIVE lineage AS (
                    SELECT id, version, parent_patterns
                    FROM patterns
                    WHERE version = ?
                    UNION ALL
                    SELECT p.id, p.version, p.parent_patterns
                    FROM patterns p
                    JOIN lineage l ON p.version IN (
                        SELECT value
                        FROM json_each(l.parent_patterns)
                    )
                )
                SELECT p.*
                FROM lineage l
                JOIN patterns p ON p.id = l.id
                ORDER BY p.version
            """, (version,))
            
            return [Pattern(
                version=row[1],
                code=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                techniques=json.loads(row[4]) if row[4] else [],
                score=row[6],
                innovation_score=row[7],
                aesthetic_score=row[8],
                mathematical_complexity=row[9],
                motion_quality=row[10],
                visual_coherence=row[11],
                technique_synergy=row[12],
                parent_patterns=json.loads(row[13]) if row[13] else []
            ) for row in cursor.fetchall()]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get enhanced system-wide statistics"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get pattern stats with existing metrics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    COALESCE(MAX(version), 0) as latest,
                    SUM(CASE WHEN score > 75 THEN 1 ELSE 0 END) as high_scoring,
                    COALESCE(AVG(score), 0) as avg_score,
                    COALESCE(AVG(innovation_score), 0) as avg_innovation,
                    COALESCE(AVG(mathematical_complexity), 0) as avg_complexity,
                    COALESCE(AVG(motion_quality), 0) as avg_motion
                FROM patterns
            """)
            pattern_stats = cursor.fetchone()
            
            # Get top technique combinations
            cursor.execute("""
                SELECT 
                    t1.technique || ' + ' || t2.technique as combo,
                    s.synergy_score,
                    COUNT(*) as usage_count
                FROM technique_synergy s
                JOIN technique_stats t1 ON t1.technique = s.technique1
                JOIN technique_stats t2 ON t2.technique = s.technique2
                WHERE s.synergy_score >= 80
                GROUP BY s.technique1, s.technique2
                ORDER BY s.synergy_score DESC
                LIMIT 5
            """)
            
            top_combos = [{
                'combination': row[0],
                'synergy_score': row[1],
                'usage_count': row[2]
            } for row in cursor.fetchall()]
            
            # Ensure we have valid values even with empty database
            return {
                'total_patterns': pattern_stats[0] or 0,
                'latest_version': pattern_stats[1] or 0,
                'high_scoring_patterns': pattern_stats[2] or 0,
                'avg_score': pattern_stats[3] or 0.0,
                'avg_innovation': pattern_stats[4] or 0.0,
                'avg_complexity': pattern_stats[5] or 0.0,
                'avg_motion': pattern_stats[6] or 0.0,
                'top_technique_combinations': top_combos or []
            }
        finally:
            conn.close()
    
    def update_synergy_pair(self, technique1: str, technique2: str, synergy_score: float) -> None:
        """Update or create synergy score between two techniques"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Ensure consistent ordering of technique pairs
            if technique1 > technique2:
                technique1, technique2 = technique2, technique1
            
            cursor.execute("""
                INSERT OR REPLACE INTO technique_synergy (
                    technique1, technique2, synergy_score, last_updated, usage_count
                ) VALUES (
                    ?, ?, ?, ?, 
                    COALESCE((SELECT usage_count + 1 FROM technique_synergy 
                             WHERE technique1 = ? AND technique2 = ?), 1)
                )
            """, (
                technique1, technique2, synergy_score, 
                datetime.now().isoformat(),
                technique1, technique2
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_historical_techniques(self, limit: int = 10) -> List[List[str]]:
        """Get techniques used in recent patterns"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT techniques
                FROM patterns
                WHERE techniques IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [json.loads(row[0]) if row[0] else [] 
                   for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def ensure_version_exists(self, version: int) -> None:
        """Ensure a version exists in the database, creating placeholder if needed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if version exists
            cursor.execute("SELECT COUNT(*) FROM patterns WHERE version = ?", (version,))
            exists = cursor.fetchone()[0] > 0
            
            # Create placeholder if it doesn't exist
            if not exists:
                cursor.execute("""
                    INSERT INTO patterns (
                        version, code, timestamp, techniques, score,
                        innovation_score, aesthetic_score, mathematical_complexity,
                        motion_quality, visual_coherence, technique_synergy
                    ) VALUES (
                        ?, 'PLACEHOLDER', datetime('now'), '[]',
                        75.0, 75.0, 75.0, 75.0, 75.0, 75.0, 75.0
                    )
                """, (version,))
                conn.commit()