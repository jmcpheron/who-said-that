# 🗣️ Who Said That? - Interactive Transcript Analyzer

**A powerful, client-side web application for analyzing AI-student conversations with advanced speaker identification and engagement metrics.**

[![GitHub Pages](https://img.shields.io/badge/demo-live-brightgreen)](https://jmcpheron.github.io/who-said-that)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

## ✨ Features

### 🎯 **Advanced Speaker Detection**
- Multi-pattern speaker identification with confidence scoring
- Explicit marker detection (`Student:`, `AI:`, `Professor:`)
- Content-based analysis using linguistic patterns
- Real-time processing with visual confidence indicators

### 📊 **Clean Interface**
- Streamlined file-focused interface
- Clickable filenames for quick access
- Modal-based detailed analysis view
- Distraction-free transcript browsing

### 🔍 **Detailed Analysis**
- Segment-by-segment breakdown with speaker confidence
- Word count statistics and engagement ratios
- Enhanced LaTeX mathematical formula rendering
- Speaker filtering and conversation navigation

### 📁 **Easy File Management**
- Drag-and-drop file upload
- Batch processing of multiple transcripts
- One-click demo with educational content
- Simple, focused file analysis workflow

## 🚀 Quick Start

### Option 1: Use Online (Recommended)
1. Visit [**Live Demo**](https://jmcpheron.github.io/who-said-that)
2. Upload your `.txt` transcript files or try the demo
3. Click filenames or "View Details" to analyze conversations

### Option 2: Run Locally
```bash
git clone https://github.com/jmcpheron/who-said-that.git
cd who-said-that
# Open index.html in your browser
```

## 🎮 How to Use

### 1. **Upload Transcripts**
- Drag and drop `.txt` files onto the upload area
- Or click "Browse Files" to select multiple files
- Try "Load Demo" for sample educational content

### 2. **Browse Results**
- View clean list of analyzed transcript files
- See key metrics (engagement, confidence, word count) at a glance
- Files display with essential statistics in compact cards

### 3. **Explore Details**
- Click the filename or "View Details" button
- See segment-by-segment speaker identification
- Review confidence scores and conversation patterns
- Filter by speaker type (AI, Student, etc.)
- View LaTeX mathematical formulas in context

## 📈 Understanding the Analysis

### Speaker Identification Confidence
- **🟢 High (70-100%)**: Clear speaker markers or strong content patterns
- **🟡 Medium (50-70%)**: Moderate confidence, manual review recommended  
- **🔴 Low (0-50%)**: Uncertain classification, requires attention

### Engagement Levels
- **High Engagement (>30%)**: Active student participation
- **Medium Engagement (10-30%)**: Moderate student involvement
- **Low Engagement (<10%)**: Primarily instructor-led

### Quality Indicators
- **Good**: High confidence scores, clear segments
- **Review Needed**: Low confidence or parsing issues detected

## 🔬 Research Applications

Perfect for educational research involving:
- **Classroom Interaction Analysis**: Measure student engagement patterns
- **AI Tutoring Effectiveness**: Compare human vs AI instruction styles
- **Conversation Dynamic Studies**: Analyze turn-taking and response patterns
- **Pedagogy Research**: Identify high-engagement teaching moments

### Sample Research Workflow
1. Upload conversation transcripts
2. Browse file list for quick overview of engagement levels
3. Click high-engagement files to examine patterns
4. Use detailed view to identify successful interaction patterns

## 🛠️ Technical Details

### Client-Side Processing
- **No Server Required**: Everything runs in your browser
- **Privacy First**: Files never leave your computer
- **Offline Capable**: Works without internet after loading
- **Cross-Platform**: Compatible with all modern browsers

### Analysis Engine
- **Multi-Pattern Detection**: Combines explicit markers with content analysis
- **Confidence Scoring**: Machine learning-inspired feature extraction
- **Real-Time Processing**: Instant results as files are uploaded
- **LaTeX Support**: Enhanced mathematical formula rendering

### Built With
- Vanilla JavaScript (no frameworks for maximum compatibility)
- Modern CSS with responsive design and smooth animations
- LaTeX mathematical expression highlighting
- Modal-based detailed analysis interface

## 📊 Sample Results

| Transcript | Student Engagement | Confidence | Words | Features |
|------------|-------------------|------------|-------|----------|
| S01-M5-R7.txt | 10.0% | 96.3% | 1,443 | 🧮 LaTeX Math |
| quantum-tutorial.txt | 24.5% | 89.2% | 1,472 | ✅ High Quality |
| philosophy-debate.txt | 42.3% | 85.6% | 987 | 💬 Interactive |

## 🎯 Comparison with Other Tools

| Feature | Who Said That? | ChatGPT Analysis | Manual Review |
|---------|----------------|------------------|---------------|
| **Consistency** | ✅ Deterministic | ❌ Varies by run | ✅ Consistent |
| **Speed** | ✅ Instant | ⚠️ API limits | ❌ Time-intensive |
| **Confidence Scores** | ✅ Built-in | ❌ No scores | ⚠️ Subjective |
| **Batch Processing** | ✅ Multiple files | ⚠️ One at a time | ❌ Manual |
| **LaTeX Support** | ✅ Enhanced rendering | ❌ No support | ⚠️ Manual formatting |
| **Privacy** | ✅ Client-side | ❌ Sends to API | ✅ Local |

## 📁 Project Structure

```
who-said-that/
├── index.html          # Main application
├── app.js              # Analysis engine
├── styles.css          # Modern styling
├── data/synthetic/     # Demo transcript files
│   ├── S01-M5-R7.txt   # Taylor polynomial tutorial
│   └── S02-K3-Q9.txt   # Neural network analysis
├── .github/workflows/  # GitHub Pages deployment
└── README.md           # This file
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional speaker detection patterns
- Enhanced LaTeX mathematical expression support
- Mobile interface optimizations
- Accessibility improvements

## 📄 License

GNU Affero General Public License v3.0. See `LICENSE` for details.

## 📚 Citation

For academic use, please cite:

```
"Speaker identification and engagement analysis performed using Who Said That? 
Interactive Transcript Analyzer (https://github.com/jmcpheron/who-said-that), 
a client-side web application for educational conversation analysis."
```

## 🆘 Support

- 📖 Check the demo files for examples
- 🐛 Report issues on GitHub
- 💡 Suggest features in discussions

---

**Ready to analyze your transcripts?** [**🚀 Try the Live Demo**](https://jmcpheron.github.io/who-said-that)

Perfect for researchers, educators, and anyone studying conversational dynamics in AI-human interactions!
