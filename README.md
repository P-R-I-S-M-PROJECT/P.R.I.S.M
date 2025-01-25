<div align="center">
  <img src="assets/images/banner.png" alt="PRISM Banner" width="100%">

  <p align="center">
    <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/badge/processing-4.0%2B-orange.svg" alt="Processing Version">
    <img src="https://img.shields.io/badge/platform-windows-lightgrey.svg" alt="Platform">
  </p>
</div>

# PRISM - Pattern Recognition & Interactive Studio Machine

PRISM is an AI-powered creative studio agent that generates both dynamic animated artworks and static visual pieces. It functions as an autonomous creative partner, learning and evolving from each artistic creation while maintaining a comprehensive understanding of its creative journey.

<div align="center">
  <h3>🎨 Dynamic Art • 🖼️ Visual Pieces • 🧬 Creative Evolution • 📊 Artistic Analysis</h3>
</div>

## 🚀 Quick Start

1. Clone and install:
   ```bash
   git clone https://github.com/P-R-I-S-M-PROJECT/P.R.I.S.M.git
   cd P.R.I.S.M
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   FAL_KEY=your_fal_key_here
   ```

3. Run:
   ```bash
   python prism.py
   ```

## 🎯 Core Features

- **🤖 Multi-Model Creative Suite**: OpenAI, Anthropic & FAL models working in harmony
- **🧬 Artistic Evolution**: Adaptive creation based on artistic success
- **📊 Creative Analysis**: Deep evaluation of visual and technical elements
- **📝 Studio Documentation**: AI-powered insights about artistic development

## 💻 Technical Requirements

- Python 3.8+
- Processing 4.0+ (must be installed at "C:\Program Files\processing-4.3\processing-java.exe")
- PowerShell 7+ (Windows)
- FFmpeg (Download from https://ffmpeg.org/download.html and place ffmpeg.exe in the scripts/ directory)
- FAL API key for static artwork creation

## 📁 Studio Structure

```
prism/
├── data/           # Creative database and metadata
├── models/         # AI model integrations
├── renders/        # Generated pieces and metadata
│   └── snapshots/    # Historical artwork files
└── scripts/        # Contains run_sketches.ps1 and ffmpeg.exe
```

## 🎮 Creative Interface

PRISM provides an intuitive creative interface:

### 1. Create Art
- Single Piece Creation
- Multi-Piece Sessions
- Continuous Studio Operation
- Model Selection
- Static Visual Art

### 2. Creative Models
- Random (Equal Representation)
- OpenAI (O1, O1-mini, 4O)
- Claude (3.5 Sonnet, 3 Opus)
- Flux (Static Visuals)

### 3. Studio Tools
- Studio Organization
- Debug Mode
- Model Experimentation

## 🏗️ Studio Architecture

### Core Components
```
├── prism.py              # Studio orchestration
├── code_generator.py     # Dynamic art engine
├── pattern_analyzer.py   # Visual analysis system
├── pattern_evolution.py # Artistic evolution
├── tests.py             # Model experimentation
├── models/              
│   ├── openai_o1.py     # O1 integration
│   ├── openai_4o.py     # 4O integration
│   ├── claude_studio.py # Claude integration
│   └── flux.py          # FAL Flux integration
```

## 🔄 Creative Pipeline

1. **🎯 Artistic Approach**
   - Historical analysis
   - Success evaluation
   - Innovation exploration
   - Style synergy

2. **🤖 Creation**
   - Multi-model creativity
   - Dynamic generation
   - Quality assurance
   - Error resilience

3. **🎨 Realization**
   - Processing animations
   - Static visual art
   - Metadata integration
   - Analysis pipeline

4. **📊 Evaluation**
   - Visual composition
   - Motion quality
   - Aesthetic assessment
   - Performance metrics

5. **🧬 Evolution**
   - Style adaptation
   - Technique development
   - Creative consistency
   - Performance learning

## 🧪 Studio Experiments

Comprehensive testing for all creative models:

1. **O1 Studio Mode**
   - Focused creation
   - Performance analysis
   - Error study

2. **Claude Studio Mode**
   - Model exploration
   - Creation pipeline
   - Quality evaluation

3. **Flux Studio Mode**
   - Visual art creation
   - Style development
   - Quality metrics

## 📄 License

MIT License - See LICENSE file

---

<div align="center">
  <p>
    <a href="https://github.com/P-R-I-S-M-PROJECT/P.R.I.S.M/issues">Report Bug</a>
    ·
    <a href="https://github.com/P-R-I-S-M-PROJECT/P.R.I.S.M/issues">Request Feature</a>
  </p>
</div> 