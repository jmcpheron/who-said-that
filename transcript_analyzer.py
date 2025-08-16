#!/usr/bin/env python3
"""
AI-Student Transcript Analyzer
Parses conversation transcripts to identify speakers and calculate engagement ratios
"""

import os
import re
import csv
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import argparse

@dataclass
class TextSegment:
    """Represents a segment of text with speaker classification"""
    text: str
    speaker: str  # 'AI' or 'Student'
    word_count: int
    confidence: float  # 0-1 confidence in classification
    line_start: int
    line_end: int

@dataclass
class TranscriptAnalysis:
    """Analysis results for a single transcript"""
    filename: str
    segments: List[TextSegment]
    ai_words: int
    student_words: int
    total_words: int
    student_ratio: float
    ai_ratio: float

class TranscriptParser:
    """Parses transcripts to identify AI vs Student utterances"""
    
    def __init__(self):
        # Patterns that strongly indicate AI responses
        self.ai_patterns = [
            r'^\s*\*[^*]+\*\s*$',  # Text in asterisks
            r'=== Page \d+ ===',    # Page markers
            r'^\s*\*\*[^*]+\*\*',   # Bold headers
            r'^\s*###?\s+\*\*',     # Markdown headers
            r'^\s*Step\s+\d+:',     # Step instructions
            r'Your\s+(task|response|turn)',  # Direct instructions
            r'\\\[.*?\\\]',         # LaTeX math
            r'\\begin\{.*?\}',      # LaTeX environments
            r'^\s*\d+\.\s+\*\*',    # Numbered sections
            r'Brain-Computer Interface Specialist',
            r'Neural Specialist',
            r'Quantum Computing Instructor',
        ]
        
        # Patterns that strongly indicate student responses
        self.student_patterns = [
            r'^\s*A:\s*',                    # Explicit answer marker
            r'^\s*Student:\s*',              # Student: marker
            r'^\s*Student_Entity_[A-Z]:\s*', # Student_Entity_X: marker
            r'^\s*[Ss]tudent\w*:\s*',        # Any student variant
        ]
        
        # Patterns for AI/instructor responses
        self.instructor_patterns = [
            r'^\s*Prof\.\s+\w+:\s*',         # Prof. Name:
            r'^\s*\w+\s+Assistant:\s*',      # Name Assistant:
            r'^\s*Claud-ius:\s*',           # Specific AI names
            r'^\s*[A-Z][a-z]+\s+Specialist:\s*', # Type Specialist:
        ]
        
        # Patterns indicating corruption/noise
        self.noise_patterns = [
            r'[A-Z]{4,}',           # Long sequences of capitals
            r'[#$%&*]{3,}',         # Symbol clusters
            r'\b[A-Z]+[#$%&*]+[A-Z]*\b',  # Mixed caps and symbols
        ]

    def count_words(self, text: str) -> int:
        """Count words in text, excluding markup and symbols"""
        # Remove LaTeX and markdown
        clean_text = re.sub(r'\\\[.*?\\\]', '', text)
        clean_text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', clean_text)
        clean_text = re.sub(r'\*+', '', clean_text)
        clean_text = re.sub(r'#+', '', clean_text)
        
        # Count actual words
        words = re.findall(r'\b[a-zA-Z]+\b', clean_text)
        return len(words)

    def calculate_ai_probability(self, text: str) -> float:
        """Calculate probability that text is from AI (0-1)"""
        score = 0.5  # Start neutral
        
        # Check for AI indicators
        for pattern in self.ai_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                score += 0.2
        
        # Check for instructor patterns
        for pattern in self.instructor_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                score += 0.3
        
        # Check for student indicators  
        for pattern in self.student_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                score -= 0.4
        
        # Length heuristic - AI responses tend to be longer
        word_count = self.count_words(text)
        if word_count > 100:
            score += 0.1
        elif word_count > 50:
            score += 0.05
        elif word_count < 10:
            score -= 0.1
        
        # Check for mathematical content
        if re.search(r'[\\$]\s*[a-zA-Z_]+\s*[\\$=]', text):
            score += 0.15
        
        # Check for instructional language
        if re.search(r'\b(calculate|derive|analyze|consider|examine)\b', text, re.IGNORECASE):
            score += 0.1
            
        # Check for noise/corruption
        for pattern in self.noise_patterns:
            if re.search(pattern, text):
                score += 0.05  # Corrupted text slightly more likely to be AI
        
        return max(0.0, min(1.0, score))

    def segment_transcript(self, content: str) -> List[TextSegment]:
        """Split transcript into segments and classify speakers"""
        lines = content.split('\n')
        segments = []
        current_segment = []
        current_speaker = None
        current_start = 0
        
        # Combined pattern for all speaker markers
        all_student_patterns = '|'.join(self.student_patterns)
        all_instructor_patterns = '|'.join(self.instructor_patterns)
        
        for i, line in enumerate(lines):
            # Skip empty lines
            if not line.strip():
                if current_segment:
                    current_segment.append(line)
                continue
            
            detected_speaker = None
            clean_text = line
            
            # Check for student markers
            if re.match(all_student_patterns, line, re.IGNORECASE):
                detected_speaker = 'Student'
                # Extract text after the marker
                for pattern in self.student_patterns:
                    clean_text = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    if clean_text != line.strip():
                        break
            
            # Check for instructor markers  
            elif re.match(all_instructor_patterns, line, re.IGNORECASE):
                detected_speaker = 'AI'
                # Extract text after the marker
                for pattern in self.instructor_patterns:
                    clean_text = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    if clean_text != line.strip():
                        break
            
            # If we found a speaker marker or speaker changed
            if detected_speaker and detected_speaker != current_speaker:
                # Finish previous segment if exists
                if current_segment:
                    text = '\n'.join(current_segment)
                    word_count = self.count_words(text)
                    if word_count > 0:
                        if current_speaker:
                            speaker = current_speaker
                            confidence = 0.9
                        else:
                            # Use probability-based classification
                            ai_prob = self.calculate_ai_probability(text)
                            speaker = 'AI' if ai_prob > 0.5 else 'Student'
                            confidence = abs(ai_prob - 0.5) * 2
                        
                        segments.append(TextSegment(
                            text=text,
                            speaker=speaker,
                            word_count=word_count,
                            confidence=confidence,
                            line_start=current_start,
                            line_end=i-1
                        ))
                
                # Start new segment
                current_segment = [clean_text] if clean_text else []
                current_speaker = detected_speaker
                current_start = i
            else:
                # Continue current segment
                current_segment.append(line)
        
        # Handle final segment
        if current_segment:
            text = '\n'.join(current_segment)
            word_count = self.count_words(text)
            if word_count > 0:
                if current_speaker:
                    speaker = current_speaker
                    confidence = 0.9
                else:
                    # Use probability-based classification
                    ai_prob = self.calculate_ai_probability(text)
                    speaker = 'AI' if ai_prob > 0.5 else 'Student'
                    confidence = abs(ai_prob - 0.5) * 2
                
                segments.append(TextSegment(
                    text=text,
                    speaker=speaker,
                    word_count=word_count,
                    confidence=confidence,
                    line_start=current_start,
                    line_end=len(lines)-1
                ))
        
        return segments

    def analyze_transcript(self, filepath: str) -> TranscriptAnalysis:
        """Analyze a single transcript file"""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        segments = self.segment_transcript(content)
        
        ai_words = sum(seg.word_count for seg in segments if seg.speaker == 'AI')
        student_words = sum(seg.word_count for seg in segments if seg.speaker == 'Student')
        total_words = ai_words + student_words
        
        student_ratio = student_words / total_words if total_words > 0 else 0
        ai_ratio = ai_words / total_words if total_words > 0 else 0
        
        return TranscriptAnalysis(
            filename=os.path.basename(filepath),
            segments=segments,
            ai_words=ai_words,
            student_words=student_words,
            total_words=total_words,
            student_ratio=student_ratio,
            ai_ratio=ai_ratio
        )

class HTMLVisualizer:
    """Creates HTML visualization of transcript analysis"""
    
    def generate_transcript_html(self, analysis: TranscriptAnalysis) -> str:
        """Generate HTML for a single transcript with color coding"""
        html = f"""
        <div class="transcript" id="{analysis.filename}">
            <h2>{analysis.filename}</h2>
            <div class="stats">
                <span class="stat ai-stat">AI: {analysis.ai_words} words ({analysis.ai_ratio:.1%})</span>
                <span class="stat student-stat">Student: {analysis.student_words} words ({analysis.student_ratio:.1%})</span>
                <span class="stat total-stat">Total: {analysis.total_words} words</span>
            </div>
            <div class="content">
        """
        
        for segment in analysis.segments:
            confidence_class = "high-confidence" if segment.confidence > 0.7 else "low-confidence"
            speaker_class = "ai-segment" if segment.speaker == 'AI' else "student-segment"
            
            html += f"""
                <div class="segment {speaker_class} {confidence_class}" 
                     title="Speaker: {segment.speaker}, Confidence: {segment.confidence:.2f}, Words: {segment.word_count}">
                    <div class="segment-label">{segment.speaker} ({segment.word_count} words)</div>
                    <div class="segment-text">{self._escape_html(segment.text[:200])}{'...' if len(segment.text) > 200 else ''}</div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        return html
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    def generate_full_html(self, analyses: List[TranscriptAnalysis]) -> str:
        """Generate complete HTML report"""
        # Calculate summary statistics
        total_transcripts = len(analyses)
        avg_student_ratio = sum(a.student_ratio for a in analyses) / total_transcripts if total_transcripts > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Student Transcript Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .summary {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .transcript {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .stats {{ margin-bottom: 15px; }}
        .stat {{ display: inline-block; margin-right: 20px; padding: 5px 10px; border-radius: 4px; font-weight: bold; }}
        .ai-stat {{ background-color: #e3f2fd; color: #1976d2; }}
        .student-stat {{ background-color: #f3e5f5; color: #7b1fa2; }}
        .total-stat {{ background-color: #e8f5e8; color: #388e3c; }}
        .segment {{ margin: 10px 0; padding: 10px; border-radius: 4px; border-left: 4px solid; }}
        .ai-segment {{ background-color: #e3f2fd; border-left-color: #1976d2; }}
        .student-segment {{ background-color: #f3e5f5; border-left-color: #7b1fa2; }}
        .low-confidence {{ opacity: 0.7; border-style: dashed; }}
        .segment-label {{ font-weight: bold; font-size: 0.9em; margin-bottom: 5px; }}
        .segment-text {{ font-size: 0.85em; line-height: 1.4; }}
        .navigation {{ position: fixed; top: 20px; right: 20px; background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); max-width: 200px; }}
        .nav-item {{ display: block; padding: 5px; text-decoration: none; color: #333; border-radius: 3px; margin: 2px 0; }}
        .nav-item:hover {{ background-color: #f0f0f0; }}
        h1, h2 {{ color: #333; }}
        .filter-controls {{ margin: 15px 0; }}
        .filter-btn {{ padding: 8px 16px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; background-color: #ddd; }}
        .filter-btn.active {{ background-color: #1976d2; color: white; }}
    </style>
    <script>
        function showAll() {{
            document.querySelectorAll('.transcript').forEach(t => t.style.display = 'block');
            setActiveFilter('all');
        }}
        function showHighEngagement() {{
            document.querySelectorAll('.transcript').forEach(t => {{
                const studentRatio = parseFloat(t.querySelector('.student-stat').textContent.match(/(\d+\.\d+)%/)[1]) / 100;
                t.style.display = studentRatio > 0.3 ? 'block' : 'none';
            }});
            setActiveFilter('high');
        }}
        function showLowEngagement() {{
            document.querySelectorAll('.transcript').forEach(t => {{
                const studentRatio = parseFloat(t.querySelector('.student-stat').textContent.match(/(\d+\.\d+)%/)[1]) / 100;
                t.style.display = studentRatio <= 0.3 ? 'block' : 'none';
            }});
            setActiveFilter('low');
        }}
        function setActiveFilter(filter) {{
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[onclick*="${{filter}}"]`).classList.add('active');
        }}
        window.onload = () => setActiveFilter('all');
    </script>
</head>
<body>
    <h1>AI-Student Transcript Analysis</h1>
    
    <div class="summary">
        <h2>Summary Statistics</h2>
        <p><strong>Total Transcripts:</strong> {total_transcripts}</p>
        <p><strong>Average Student Engagement:</strong> {avg_student_ratio:.1%}</p>
        <p><strong>Analysis Method:</strong> Pattern-based speaker identification with confidence scoring</p>
        
        <div class="filter-controls">
            <button class="filter-btn active" onclick="showAll()">Show All</button>
            <button class="filter-btn" onclick="showHighEngagement()">High Engagement (>30%)</button>
            <button class="filter-btn" onclick="showLowEngagement()">Low Engagement (≤30%)</button>
        </div>
    </div>
    
    <div class="navigation">
        <h3>Transcripts</h3>
        {self._generate_nav_links(analyses)}
    </div>
"""
        
        # Add individual transcript analyses
        for analysis in sorted(analyses, key=lambda x: x.student_ratio, reverse=True):
            html += self.generate_transcript_html(analysis)
        
        html += """
</body>
</html>
        """
        return html
    
    def _generate_nav_links(self, analyses: List[TranscriptAnalysis]) -> str:
        """Generate navigation links for transcripts"""
        links = ""
        for analysis in sorted(analyses, key=lambda x: x.student_ratio, reverse=True):
            links += f'<a href="#{analysis.filename}" class="nav-item">{analysis.filename} ({analysis.student_ratio:.1%})</a>\n'
        return links

def export_csv(analyses: List[TranscriptAnalysis], filepath: str):
    """Export analysis results to CSV"""
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'Total_Words', 'AI_Words', 'Student_Words', 'Student_Ratio', 'AI_Ratio'])
        
        for analysis in analyses:
            writer.writerow([
                analysis.filename,
                analysis.total_words,
                analysis.ai_words,
                analysis.student_words,
                f"{analysis.student_ratio:.3f}",
                f"{analysis.ai_ratio:.3f}"
            ])

def main():
    parser = argparse.ArgumentParser(description='Analyze AI-Student transcripts')
    parser.add_argument('input_dir', help='Directory containing transcript files')
    parser.add_argument('--output-html', default='transcript_analysis.html', help='Output HTML file')
    parser.add_argument('--output-csv', default='transcript_analysis.csv', help='Output CSV file')
    parser.add_argument('--extensions', nargs='+', default=['.txt', '.docx'], help='File extensions to process')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    transcript_parser = TranscriptParser()
    visualizer = HTMLVisualizer()
    
    # Find and analyze transcript files
    input_path = Path(args.input_dir)
    analyses = []
    
    print(f"Scanning {input_path} for transcript files...")
    
    for ext in args.extensions:
        for file_path in input_path.rglob(f"*{ext}"):
            if ext == '.txt':
                print(f"Analyzing {file_path.name}...")
                try:
                    analysis = transcript_parser.analyze_transcript(str(file_path))
                    analyses.append(analysis)
                    print(f"  → AI: {analysis.ai_words} words, Student: {analysis.student_words} words, Ratio: {analysis.student_ratio:.1%}")
                except Exception as e:
                    print(f"  → Error analyzing {file_path.name}: {e}")
    
    if not analyses:
        print("No transcript files found!")
        return
    
    # Generate outputs
    print(f"\nGenerating HTML report: {args.output_html}")
    html_content = visualizer.generate_full_html(analyses)
    with open(args.output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generating CSV report: {args.output_csv}")
    export_csv(analyses, args.output_csv)
    
    # Print summary
    print(f"\nAnalysis Complete!")
    print(f"Total transcripts: {len(analyses)}")
    print(f"Average student engagement: {sum(a.student_ratio for a in analyses) / len(analyses):.1%}")
    print(f"Range: {min(a.student_ratio for a in analyses):.1%} - {max(a.student_ratio for a in analyses):.1%}")
    
    # Suggest interesting transcripts
    high_engagement = [a for a in analyses if a.student_ratio > 0.4]
    low_engagement = [a for a in analyses if a.student_ratio < 0.1]
    
    if high_engagement:
        print(f"\nHigh engagement transcripts ({len(high_engagement)}):")
        for a in sorted(high_engagement, key=lambda x: x.student_ratio, reverse=True)[:3]:
            print(f"  {a.filename}: {a.student_ratio:.1%}")
    
    if low_engagement:
        print(f"\nLow engagement transcripts ({len(low_engagement)}):")
        for a in sorted(low_engagement, key=lambda x: x.student_ratio)[:3]:
            print(f"  {a.filename}: {a.student_ratio:.1%}")

if __name__ == "__main__":
    main()