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
   a. **Technique Selection (`pattern_evolution.py`):**
      - Calculate technique weights based on:
        * Historical performance (40% weight)
        * Success rates (30% weight)
        * Innovation factors (30% weight)
      - Apply adaptation boosts:
        * +20% for techniques with high adaptation rates
        * +30% for techniques with proven synergy
      - Select 1-4 techniques using weighted probabilities
      - Consider technique combinations and synergy history
      - Filter pool for synergistic choices if selecting multiple
      - Update remaining pool based on synergy with all selected techniques

   b. **Code Generation (`code_generator.py`):**
      - Select AI model based on weighted randomization:
        * o1: 33% probability
        * o1-mini: 33% probability
        * 4o: 34% probability
      - Generate Processing code using selected techniques
      - Validate code structure and requirements
      - Apply template with standardized setup
      - Handle error recovery and retries
      - Clean and merge code with proper validation
      - Ensure proper error handling and logging

   c. **Rendering Process:**
      - Execute Processing sketch via PowerShell
      - Generate 360 frames at 60fps (6-second loop)
      - Save frames and metadata
      - Convert to MP4 using FFmpeg
      - Verify render quality and completion

   d. **Analysis Pipeline (`pattern_analyzer.py`):**
      - Frame Analysis: Every 6th frame is analyzed
        * Complexity (edge density, pattern distribution)
        * Motion quality (flow, coverage, consistency)
        * Aesthetic qualities (balance, composition)
        * Visual coherence
        * Region complexity and element consistency
      - Performance Metrics:
        * Innovation score (comparison with history)
        * Technique synergy measurement
        * Adaptation rate calculation
        * Evolution trend analysis
      - Dynamic Weighting:
        * Adjust metric weights based on pattern characteristics
        * Consider technique count and complexity
        * Balance between different quality aspects

   e. **Evolution System:**
      - Technique Evolution:
        * Update success rates and performance stats
        * Adjust adaptation rates based on stability
        * Calculate new synergy scores
        * Update technique weights
        * Track performance trends
      - Pattern Evolution:
        * Track pattern lineage
        * Store performance metrics
        * Update technique relationships
        * Calculate innovation factors
        * Monitor visual coherence trends
      - Database Updates:
        * Save technique statistics
        * Update synergy pairs
        * Store evolution history
        * Track adaptation rates
        * Maintain performance trends

   f. **Documentation:**
      - Generate comprehensive pattern analysis
      - Track technique-specific insights
      - Monitor evolution trends
      - Store historical performance data
      - Generate evolution insights
      - Track technique observations
      - Store pattern analysis with technical insights

   g. **Content Distribution:**
      - Sync videos to CDN
      - Update web components
      - Track version history
      - Manage render storage
      - Handle video verification
      - Monitor sync completion

3. **Continuous Operation:**
   - Run iterations every 10 minutes
   - Monitor system performance
   - Track resource usage
   - Handle errors and recovery
   - Maintain system stability
   - Ensure consistent operation

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
