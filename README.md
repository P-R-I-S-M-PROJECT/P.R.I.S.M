# PRISM - Pattern Recognition & Interactive Sketch Machine

PRISM is an AI-driven creative system that generates sophisticated geometric animations using Processing. It functions as an automated art studio with evolutionary memory, treating each creation as a data point in a living system.

## Core Components

- **Pattern Generation**: Multi-model AI generation (OpenAI & Anthropic) for geometric animations
- **Evolution System**: Tracks technique performance and adapts generation strategy
- **Analysis Pipeline**: Evaluates visual complexity, motion quality, and aesthetics
- **Documentation**: Auto-generates insights about patterns and techniques

## Technical Requirements

- Python 3.8+
- Processing 4.0+ (must be installed at "C:\Program Files\processing-4.3\processing-java.exe")
- Node.js 16+
- PowerShell 7+ (Windows)
- FFmpeg (included in scripts/ffmpeg.exe)

## Important Structure

The project has specific structural requirements:
- Main sketch must be named `auto.pde`
- Project folder must be named `auto`
- Required directories:
  ```
  auto/
  ├── data/           # Database and metadata storage
  ├── models/         # AI model integrations
  ├── renders/        # Generated animations
  ├── scripts/        # Contains run_sketches.ps1 and ffmpeg.exe
  └── web/public/videos/  # Final video outputs
  ```

## Quick Start

1. Clone and install:
   ```bash
   git clone https://github.com/P-R-I-S-M-PROJECT/P.R.I.S.M.git
   cd P.R.I.S.M
   pip install -r requirements.txt
   npm install
   ```

2. Create a `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   ```

3. Run:
   ```bash
   python prism.py
   ```

## System Architecture

### Core Files
```
├── prism.py              # Main orchestration
├── code_generator.py     # Pattern generation engine
├── pattern_analyzer.py   # Frame analysis system
├── pattern_evolution.py  # Technique evolution
├── tests.py             # Model testing framework
├── models/              
│   ├── openai_o1.py     # O1 model - Primary generation
│   ├── openai_4o.py     # 4O model - Basic generation
│   └── claude_generator.py  # Claude integration
```

### Pipeline Overview

1. **Technique Selection**
   - Historical performance analysis (40%)
   - Success rate weighting (30%)
   - Innovation factors (30%)
   - Synergy boosts for proven combinations

2. **Code Generation**
   - Model selection with equal weights (20% each):
     - O1 (Superior reasoning and logic)
     - O1-mini (Fast and efficient)
     - 4O (Basic generation)
     - Claude 3.5 Sonnet (Latest, balanced)
     - Claude 3 Opus (Best quality)
   - Processing code generation
   - Structure validation
   - Error recovery

3. **Rendering**
   - 360 frames @ 60fps
   - 6-second loops
   - FFmpeg conversion

4. **Analysis**
   - Frame-by-frame analysis
   - Complexity scoring
   - Motion quality evaluation
   - Performance metrics

5. **Evolution**
   - Success rate updates
   - Synergy calculations
   - Technique adaptation
   - Pattern lineage tracking

## Testing Framework

The system includes dedicated test modes for different AI models:

1. **O1 Test Mode**
   - Test openai models in isolation
   - Full pattern generation and scoring
   - Performance tracking

2. **Claude Test Mode**
   - Choose between Claude 3.5 Sonnet and Claude 3 Opus
   - Isolated testing for each model
   - Full pattern generation and analysis

Access test modes through the main menu (options 4 and 5).

## License

MIT License - See LICENSE file

---

For technical details about each component, see the docstrings and inline documentation in the respective files. 