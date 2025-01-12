# PRISM - Pattern Recognition & Interactive Sketch Machine

PRISM is an AI-driven creative system that generates sophisticated geometric animations using Processing. It functions as an automated art studio with evolutionary memory, treating each creation as a data point in a living system.

## Core Components

- **Pattern Generation**: AI models generate Processing code for geometric animations
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

2. Create a `.env` file with your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
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
├── models/              
│   ├── openai_o1.py     # O1 model integration
│   └── openai_4o.py     # 4O model integration
```

### Pipeline Overview

1. **Technique Selection**
   - Historical performance analysis (40%)
   - Success rate weighting (30%)
   - Innovation factors (30%)
   - Synergy boosts for proven combinations

2. **Code Generation**
   - Model selection (o1: 33%, o1-mini: 33%, 4o: 34%)
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

## License

MIT License - See LICENSE file

---

For technical details about each component, see the docstrings and inline documentation in the respective files. 