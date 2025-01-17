# PRISM Technical Overview

## Core Architecture

PRISM is built on a multi-model AI architecture that leverages both OpenAI and Anthropic models for creative code generation. The system employs an evolutionary approach to pattern generation, continuously learning from past successes and failures.

## Interactive System

The system provides a comprehensive menu-driven interface:

1. **Pattern Generation**
   - Single pattern generation with immediate feedback
   - Batch generation of multiple patterns
   - Continuous generation with custom intervals
   - Direct model selection for targeted experiments

2. **Model Selection**
   - Random mode with equal model weights
   - Direct model selection for focused testing
   - Seamless switching between models
   - Model-specific performance tracking

3. **System Management**
   - Pattern cleanup and archival
   - Debug mode for detailed logging
   - Dedicated model testing modes
   - Performance metrics and statistics

## AI Models

The system integrates multiple AI models with different strengths:

1. **OpenAI Models**
   - O1
   - O1-mini
   - 4O

2. **Anthropic Models**
   - Claude 3.5 Sonnet
   - Claude 3 Opus

Each model is weighted equally (20%) in random selection mode.

## Generation Pipeline

1. **Technique Selection**
   - Analyzes historical performance data
   - Weights techniques based on success rates
   - Considers innovation potential
   - Calculates synergy between techniques

2. **Model Selection**
   - User-selected or random based on configuration
   - Each model has equal probability in random mode
   - Models can be tested individually

3. **Code Generation**
   - Selected model generates Processing code
   - Code is validated and sanitized
   - Syntax is converted if needed
   - Error recovery mechanisms in place

4. **Rendering**
   - Processing sketch compilation (`prism.pde`)
   - 360-frame animation @ 60fps
   - FFmpeg video conversion
   - Local storage with metadata

## Analysis System

The analysis pipeline evaluates patterns across multiple dimensions:

1. **Visual Complexity**
   - Edge detection analysis
   - Color distribution metrics
   - Pattern density calculations

2. **Motion Quality**
   - Frame-to-frame difference analysis
   - Motion smoothness metrics
   - Loop seamlessness check

3. **Aesthetic Quality**
   - Composition balance
   - Color harmony
   - Visual interest metrics

## Testing Framework

The system includes dedicated test modes for thorough model evaluation:

1. **O1 Test Mode**
   - Isolates GPT-3.5 model for testing
   - Generates and scores patterns
   - Tracks performance metrics
   - Interactive continuation

2. **Claude Test Mode**
   - Choice between Sonnet and Opus models
   - Full pattern generation pipeline
   - Comprehensive scoring
   - Interactive testing session

Test modes are accessible through the main menu and provide detailed feedback on each generation.

## Evolution System

The evolution system adapts based on:

1. **Performance Tracking**
   - Success rate per technique
   - Model performance metrics
   - Pattern scores history

2. **Technique Evolution**
   - Synergy calculations
   - Weight adjustments
   - Innovation boosting

3. **Pattern Lineage**
   - Version tracking
   - Technique inheritance
   - Score progression

## Documentation

The system maintains comprehensive documentation:

1. **Pattern Records**
   - Version history
   - Technique combinations
   - Performance metrics
   - Generated code

2. **System Stats**
   - Model usage statistics
   - Average scores
   - Success rates
   - Innovation metrics

3. **Technical Logs**
   - Generation process
   - Error tracking
   - Performance monitoring
   - System health
