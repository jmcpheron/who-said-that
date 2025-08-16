# 🗣️ Who Said That?

Client-side transcript analyzer for AI-student conversations with speaker identification and engagement metrics.

**[Live Demo](https://jmcpheron.github.io/who-said-that)** | **Created by [Jason J. McPheron](https://github.com/jmcpheron)**

## Features

- **Speaker Detection**: AI vs Student identification with confidence scoring
- **LaTeX Support**: Mathematical formulas rendered in context  
- **Clean Interface**: Clickable filenames, modal details, no clutter
- **File Management**: Drag-and-drop upload, demo content included
- **Privacy**: Everything runs locally in your browser

## Quick Start

1. Visit the [Live Demo](https://jmcpheron.github.io/who-said-that)
2. Upload `.txt` files or click "Load Demo"  
3. Click filenames to view detailed analysis

Or run locally: `git clone https://github.com/jmcpheron/who-said-that.git`

## Technical Details

- **Client-side**: Runs entirely in browser, files never leave your computer
- **Built with**: Vanilla JavaScript, modern CSS, LaTeX rendering
- **Analysis**: Pattern detection + confidence scoring for speaker identification

## Project Structure

```
who-said-that/
├── index.html
├── app.js
├── styles.css
├── data/synthetic/
│   ├── S01-M5-R7.txt
│   └── S02-K3-Q9.txt
├── demo/
│   ├── P01-G8-S4.txt
│   ├── neural-interface-session.txt
│   ├── philosophy-debate.txt
│   └── quantum-computing-tutorial.txt
└── README.md
```

## License

AGPL-3.0

## Citation

Created by **Jason J. McPheron** ([github.com/jmcpheron](https://github.com/jmcpheron))

For academic use:
> McPheron, J.J. (2025). Who Said That? Interactive Transcript Analyzer. https://github.com/jmcpheron/who-said-that
