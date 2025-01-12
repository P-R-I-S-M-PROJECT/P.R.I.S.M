# PRISM Technical Overview

## Core Architecture

PRISM is built on a multi-model AI architecture that leverages both OpenAI and Anthropic models for creative code generation. The system employs an evolutionary approach to pattern generation, continuously learning from past successes and failures.

## AI Models

The system integrates multiple AI models with different strengths:

1. **OpenAI Models**
   - O1: Superior reasoning and logic, best overall performance
   - O1-mini: Fast and efficient, strong performance for most patterns
   - 4O: Basic pattern generation, limited reasoning capabilities

2. **Anthropic Models**
   - Claude 3.5 Sonnet: Latest model, balanced performance
   - Claude 3 Opus: Highest quality, best for complex patterns

Each model is weighted equally (20%) in the selection process, ensuring diverse pattern generation.

## Generation Pipeline

1. **Technique Selection**
   - Analyzes historical performance data
   - Weights techniques based on success rates
   - Considers innovation potential
   - Calculates synergy between techniques

2. **Model Selection**
   - Random selection based on configured weights
   - Each model has equal probability (20%)
   - Models can be tested individually using test modes

3. **Code Generation**
   - Selected model generates Processing code
   - Code is validated and sanitized
   - Syntax is converted if needed
   - Error recovery mechanisms in place

4. **Rendering**
   - Processing sketch compilation
   - 360-frame animation @ 60fps
   - FFmpeg video conversion
   - CDN upload for web display

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
