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

### 📊 **Interactive Analytics**
- Dynamic engagement distribution charts
- Confidence vs engagement scatter plots
- Filterable transcript library
- Real-time search and sorting

### 🔍 **Detailed Analysis**
- Segment-by-segment breakdown with speaker confidence
- Word count statistics and engagement ratios
- Mathematical expression and question highlighting
- Quality assessment with actionable flags

### 📁 **Easy File Management**
- Drag-and-drop file upload
- Batch processing of multiple transcripts
- Demo data for immediate testing
- Export results to CSV format

## 🚀 Quick Start

### Option 1: Use Online (Recommended)
1. Visit [**Live Demo**](https://jmcpheron.github.io/who-said-that)
2. Upload your `.txt` transcript files or try the demo
3. Analyze engagement patterns and export results

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
- Try "Load Demo" for sample data

### 2. **Analyze Results**
- View summary statistics cards
- Use filters to focus on specific engagement levels
- Search transcripts by filename or content

### 3. **Explore Details**
- Click "View Details" on any transcript
- See segment-by-segment speaker identification
- Review confidence scores and patterns

### 4. **Export Data**
- Click "Export Analysis" to download CSV
- Perfect for research and further analysis

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
2. Filter for high-engagement sessions (>40% student ratio)
3. Export data for statistical analysis
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
- **Export Ready**: CSV output for research tools

### Built With
- Vanilla JavaScript (no frameworks for maximum compatibility)
- Chart.js for interactive visualizations
- Modern CSS with responsive design
- Progressive Web App capabilities

## 📊 Sample Results

| Transcript | Student Engagement | Confidence | Words | Quality |
|------------|-------------------|------------|-------|---------|
| quantum-tutorial.txt | 24.5% | 89.2% | 1,472 | ✅ Good |
| neural-interface.txt | 18.7% | 92.1% | 1,154 | ✅ Good |
| philosophy-debate.txt | 42.3% | 85.6% | 987 | ✅ Good |

## 🎯 Comparison with Other Tools

| Feature | Who Said That? | ChatGPT Analysis | Manual Review |
|---------|----------------|------------------|---------------|
| **Consistency** | ✅ Deterministic | ❌ Varies by run | ✅ Consistent |
| **Speed** | ✅ Instant | ⚠️ API limits | ❌ Time-intensive |
| **Confidence Scores** | ✅ Built-in | ❌ No scores | ⚠️ Subjective |
| **Batch Processing** | ✅ Multiple files | ⚠️ One at a time | ❌ Manual |
| **Export Ready** | ✅ CSV format | ⚠️ Copy/paste | ⚠️ Manual entry |
| **Privacy** | ✅ Client-side | ❌ Sends to API | ✅ Local |

## 📁 Project Structure

```
who-said-that/
├── index.html          # Main application
├── app.js              # Analysis engine
├── styles.css          # Modern styling
├── demo/               # Sample transcript files
│   ├── quantum-computing-tutorial.txt
│   ├── neural-interface-session.txt
│   └── philosophy-debate.txt
├── .github/workflows/  # GitHub Pages deployment
└── README.md           # This file
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional speaker detection patterns
- New visualization types
- Export format options
- Mobile interface enhancements

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
