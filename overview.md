# PRISM - Pattern Recognition & Interactive Sketch Machine

## Overview
PRISM is an AI-driven creative system that generates sophisticated geometric animations using Processing. It functions as an automated art studio with evolutionary memory, treating each creation as a data point in a living system. The system emphasizes continuous evolution through pattern analysis, technique synergy tracking, and historical learning.

## Project Structure

1. **Core Components:**
   - `prism.py` - Main system orchestration and continuous generation loop
   - `code_generator.py` - Pattern generation engine with multi-model support
   - `pattern_analyzer.py` - Frame-by-frame analysis and scoring system
   - `pattern_evolution.py` - Technique selection and evolution tracking
   - `logger.py` - Enhanced logging with visual feedback
   - `config.py` - System configuration and parameter management

2. **Database Management:**
   - `database_manager.py` - Evolution-aware SQLite operations
   - `models/data_models.py` - Pattern and Technique data models
   - `models/openai_o1.py` - O1 model integration
   - `models/openai_4o.py` - 4O model integration

3. **Documentation & Analysis:**
   - `documentation_manager.py` - Integrated analysis system
   - Pattern evolution insights
   - Technique performance tracking
   - Historical trend analysis

4. **Support Directories:**
   - `data/` - SQLite database and metadata
   - `renders/` - Generated pattern outputs and frames
   - `scripts/` - PowerShell automation scripts
   - `web/` - Web components and CDN sync

## Pipeline Overview

1. **Initialization Phase:**
   - Load environment variables and configuration
   - Initialize SQLite database connection
   - Set up logging system with visual feedback
   - Load technique categories and parameters

2. **Generation Pipeline:**
   a. **Technique Selection:**
      - Select 1-4 techniques based on historical performance
      - Calculate synergy scores between techniques
      - Apply weighted selection based on success rates
      - Consider technique diversity and innovation potential

   b. **Code Generation:**
      - Select AI model (o1-mini or 4o) based on config weights
      - Generate Processing code using selected techniques
      - Validate code structure and requirements
      - Apply template with standardized setup

   c. **Rendering Process:**
      - Execute Processing sketch via PowerShell
      - Generate 360 frames at 60fps (6-second loop)
      - Save frames and metadata
      - Convert to MP4 using FFmpeg

   d. **Analysis Pipeline:**
      - Load and sample frames (every 6th frame)
      - Analyze complexity (edge density, pattern density)
      - Calculate motion quality (flow, coverage, consistency)
      - Evaluate aesthetic qualities (balance, composition)
      - Measure visual coherence and technique synergy

   e. **Evolution Tracking:**
      - Update technique performance statistics
      - Track pattern lineage and relationships
      - Calculate adaptation rates and innovation factors
      - Store synergy scores between techniques

   f. **Documentation:**
      - Generate comprehensive pattern analysis
      - Track technique-specific insights
      - Monitor evolution trends
      - Store historical performance data

   g. **Content Distribution:**
      - Sync videos to CDN
      - Update web components
      - Track version history
      - Manage render storage

3. **Continuous Operation:**
   - Run iterations every 10 minutes
   - Monitor system performance
   - Track resource usage
   - Handle errors and recovery

## Core Features

1. **Pattern Generation:**
   - AI-driven code generation with multiple models
   - Seamless 6-second loops (360 frames at 60fps)
   - Multiple interweaving cycles and rhythms
   - Dynamic pattern transformation
   - Balance between chaos and order
   - Emphasis on unique, non-repetitive generation

2. **Analysis Systems:**
   - Multi-dimensional pattern analysis:
     * Frame-by-frame visual analysis
     * Technical implementation scoring
     * Aesthetic quality evaluation
     * Evolution trend tracking
     * Technique synergy analysis
   - Historical performance tracking:
     * Pattern lineage tracking
     * Technique combination success rates
     * Evolution chain analysis
     * Adaptation rate monitoring
   - Insight generation:
     * Pattern-specific documentation
     * Technique-specific insights
     * Evolution trend analysis
     * System-wide learning

3. **Evolution Strategy:**
   - Dynamic technique selection with synergy awareness
   - Adaptive learning rates based on performance
   - Pattern lineage tracking and analysis
   - Multi-dimensional evolution:
     * Technique combinations
     * Visual coherence
     * Performance metrics
     * Innovation factors
   - Historical pattern memory:
     * Success pattern recognition
     * Technique synergy tracking
     * Evolution chain analysis
     * Performance trend monitoring

## Technical Implementation

1. **Database Schema:**
   - Patterns table:
     * Version tracking
     * Technique combinations
     * Performance metrics
     * Evolution history
   - Technique stats table:
     * Usage statistics
     * Success rates
     * Synergy scores
     * Adaptation rates
   - Evolution history table:
     * Pattern lineage
     * Performance trends
     * Technique relationships

2. **Analysis Metrics:**
   - Complexity analysis:
     * Edge detection and density
     * Pattern distribution
     * Region complexity
     * Element consistency
   - Motion analysis:
     * Flow smoothness
     * Coverage patterns
     * Direction consistency
     * Center-weighted movement
   - Aesthetic evaluation:
     * Compositional balance
     * Negative space usage
     * Layering and depth
     * Contrast and form

3. **Development Tools:**
   - PowerShell automation scripts
   - FFmpeg video processing
   - SQLite database management
   - CDN integration
   - Cache control utilities

## Future Additions

1. **Multi-LLM System:**
   - Integration with multiple AI models
   - Self-hosted language model deployment
   - Model performance comparison
   - Resource optimization

2. **Enhanced Evolution System (v2):**
   - Advanced technique synergy analysis
   - Pattern DNA tracking and mixing
   - Genetic algorithm integration
   - Evolution visualization tools

3. **Social Agent (v1):**
   - Automated content publishing
   - Platform-specific formatting
   - Analytics dashboard
   - Content calendar management
