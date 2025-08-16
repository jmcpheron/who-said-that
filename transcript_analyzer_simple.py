#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pandas",
#     "textstat",
#     "numpy",
# ]
# ///
"""
Simple AI-Student Transcript Analyzer
Focused on reliability and ease of use
"""

import pandas as pd
import textstat
import numpy as np
import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import argparse
import sys

@dataclass
class TextSegment:
    """Text segment with speaker classification"""
    text: str
    speaker: str  # 'AI' or 'Student'
    confidence: float
    word_count: int
    line_start: int
    line_end: int

@dataclass
class TranscriptAnalysis:
    """Complete transcript analysis"""
    filename: str
    segments: List[TextSegment]
    ai_words: int
    student_words: int
    total_words: int
    student_ratio: float
    confidence_score: float
    quality_flags: List[str]

class SmartTranscriptAnalyzer:
    """Reliable transcript analyzer with multiple detection methods"""
    
    def __init__(self):
        # Explicit speaker markers (highest confidence)
        self.student_markers = [
            r'^\s*Student[^:]*:\s*',
            r'^\s*A:\s*',
            r'^\s*Answer:\s*',
            r'^\s*Me:\s*',
            r'^\s*User:\s*',
            r'^\s*Student_Entity_[A-Z]:\s*',
        ]
        
        self.ai_markers = [
            r'^\s*(?:Prof|Professor|Dr)\.?\s*[^:]*:\s*',
            r'^\s*(?:AI|Assistant|Claude|GPT|Bot):\s*',
            r'^\s*\w+\s+(?:Specialist|Assistant|Instructor):\s*',
            r'^\s*Claud-ius:\s*',
            r'^\s*Molecular Gastronomy Assistant:\s*',
            r'^\s*Brain-Computer Interface Specialist:\s*',
        ]
        
        # Content patterns for classification
        self.ai_content_patterns = [
            r'Let\'s\s+(?:explore|examine|calculate)',
            r'Your\s+(?:task|mission):\s*',
            r'Step\s+\d+[:.]',
            r'^\s*\*\*[^*]+\*\*',  # Bold headers
            r'=== Page \d+ ===',
            r'Consider\s+(?:the|this)',
            r'Now\s+(?:let\'s|we\'ll)',
            r'(?:Excellent|Perfect|Good)!\s*(?:You|Your)',
            r'\\[.*?\\]',  # LaTeX math
        ]
        
        self.student_content_patterns = [
            r'^(?:yes|no|ok|okay|sure|maybe)',
            r'(?:confused|don\'t understand|not sure)',
            r'\?$',  # Ends with question
            r'(?:can you|could you|what if|why|how)',
            r'^(?:wait|but|so|um|uh)',
            r'^[a-z]',  # Starts with lowercase (often student)
        ]

    def count_words(self, text: str) -> int:
        """Count words excluding markup"""
        clean_text = re.sub(r'\*+', '', text)
        clean_text = re.sub(r'=+', '', clean_text)
        clean_text = re.sub(r'\\[.*?\\]', '', clean_text)
        words = re.findall(r'\b[a-zA-Z]+\b', clean_text)
        return len(words)

    def classify_speaker(self, text: str) -> Tuple[str, float]:
        """Classify speaker with confidence score"""
        if not text.strip():
            return 'AI', 0.5
        
        # Check explicit markers first
        for pattern in self.student_markers:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return 'Student', 0.95
                
        for pattern in self.ai_markers:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return 'AI', 0.95
        
        # Content-based classification
        ai_score = 0.0
        
        # AI indicators
        for pattern in self.ai_content_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                ai_score += 0.2
        
        # Student indicators
        for pattern in self.student_content_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                ai_score -= 0.25
        
        # Length heuristics
        word_count = self.count_words(text)
        if word_count > 100:
            ai_score += 0.1
        elif word_count < 20:
            ai_score -= 0.1
        
        # Reading level
        try:
            reading_level = textstat.flesch_kincaid_grade(text)
            if reading_level > 12:
                ai_score += 0.05
            elif reading_level < 8:
                ai_score -= 0.05
        except:
            pass
        
        # Math/technical content
        if re.search(r'[\\$]\s*[a-zA-Z_]+|[=<>]+|\d+\s*[+\-*/]\s*\d+', text):
            ai_score += 0.1
        
        # Question patterns
        question_count = len(re.findall(r'\?', text))
        if question_count > 0 and word_count > 0:
            if question_count / word_count > 0.1:
                ai_score -= 0.1
        
        # Convert to probability
        ai_prob = 1 / (1 + np.exp(-ai_score))
        
        if ai_prob > 0.5:
            return 'AI', ai_prob
        else:
            return 'Student', 1 - ai_prob

    def segment_transcript(self, content: str) -> List[TextSegment]:
        """Smart segmentation with speaker detection"""
        lines = content.split('\n')
        segments = []
        current_chunk = []
        current_speaker = None
        start_line = 0
        
        for i, line in enumerate(lines):
            if not line.strip():
                if current_chunk:
                    current_chunk.append(line)
                continue
            
            # Check for speaker markers
            detected_speaker = None
            clean_line = line
            
            for pattern in self.student_markers:
                if re.match(pattern, line, re.IGNORECASE):
                    detected_speaker = 'Student'
                    clean_line = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    break
            
            if not detected_speaker:
                for pattern in self.ai_markers:
                    if re.match(pattern, line, re.IGNORECASE):
                        detected_speaker = 'AI'
                        clean_line = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                        break
            
            # Speaker change or explicit marker found
            if detected_speaker and detected_speaker != current_speaker:
                # Process previous chunk
                if current_chunk:
                    chunk_text = '\n'.join(current_chunk)
                    if current_speaker:
                        speaker = current_speaker
                        confidence = 0.9
                    else:
                        speaker, confidence = self.classify_speaker(chunk_text)
                    
                    word_count = self.count_words(chunk_text)
                    if word_count > 0:
                        segments.append(TextSegment(
                            text=chunk_text,
                            speaker=speaker,
                            confidence=confidence,
                            word_count=word_count,
                            line_start=start_line,
                            line_end=i-1
                        ))
                
                # Start new chunk
                current_chunk = [clean_line] if clean_line else []
                current_speaker = detected_speaker
                start_line = i
            else:
                current_chunk.append(line)
        
        # Handle final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if current_speaker:
                speaker = current_speaker
                confidence = 0.9
            else:
                speaker, confidence = self.classify_speaker(chunk_text)
            
            word_count = self.count_words(chunk_text)
            if word_count > 0:
                segments.append(TextSegment(
                    text=chunk_text,
                    speaker=speaker,
                    confidence=confidence,
                    word_count=word_count,
                    line_start=start_line,
                    line_end=len(lines)-1
                ))
        
        # If no segments found, analyze as single block
        if not segments:
            speaker, confidence = self.classify_speaker(content)
            word_count = self.count_words(content)
            if word_count > 0:
                segments.append(TextSegment(
                    text=content,
                    speaker=speaker,
                    confidence=confidence,
                    word_count=word_count,
                    line_start=0,
                    line_end=len(lines)-1
                ))
        
        return segments

    def analyze_transcript(self, file_path: str) -> TranscriptAnalysis:
        """Analyze complete transcript"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return TranscriptAnalysis(
                filename=Path(file_path).name,
                segments=[],
                ai_words=0,
                student_words=0,
                total_words=0,
                student_ratio=0.0,
                confidence_score=0.0,
                quality_flags=[f'Read error: {e}']
            )
        
        if not content.strip():
            return TranscriptAnalysis(
                filename=Path(file_path).name,
                segments=[],
                ai_words=0,
                student_words=0,
                total_words=0,
                student_ratio=0.0,
                confidence_score=0.0,
                quality_flags=['Empty file']
            )
        
        segments = self.segment_transcript(content)
        
        # Calculate statistics
        ai_words = sum(seg.word_count for seg in segments if seg.speaker == 'AI')
        student_words = sum(seg.word_count for seg in segments if seg.speaker == 'Student')
        total_words = ai_words + student_words
        
        student_ratio = student_words / total_words if total_words > 0 else 0.0
        avg_confidence = np.mean([seg.confidence for seg in segments]) if segments else 0.0
        
        # Quality flags
        quality_flags = []
        if avg_confidence < 0.6:
            quality_flags.append('Low confidence')
        if total_words < 100:
            quality_flags.append('Very short')
        if len(segments) < 2:
            quality_flags.append('Few segments')
        
        return TranscriptAnalysis(
            filename=Path(file_path).name,
            segments=segments,
            ai_words=ai_words,
            student_words=student_words,
            total_words=total_words,
            student_ratio=student_ratio,
            confidence_score=avg_confidence,
            quality_flags=quality_flags
        )

def create_html_report(analyses: List[TranscriptAnalysis], output_file: str):
    """Create clean HTML report"""
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Transcript Analysis Report</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .summary {{ 
            background: white; 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .transcript {{ 
            background: white;
            border: 1px solid #e0e0e0; 
            margin: 15px 0; 
            padding: 20px; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .ai-segment {{ 
            background-color: #e3f2fd; 
            margin: 8px 0; 
            padding: 12px; 
            border-radius: 6px; 
            border-left: 4px solid #1976d2;
        }}
        .student-segment {{ 
            background-color: #f3e5f5; 
            margin: 8px 0; 
            padding: 12px; 
            border-radius: 6px; 
            border-left: 4px solid #7b1fa2;
        }}
        .stats {{ 
            margin: 15px 0; 
            font-weight: bold; 
            color: #555;
            font-size: 1.1em;
        }}
        .confidence {{ 
            font-size: 0.9em; 
            color: #666; 
            font-weight: normal;
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%; 
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{ 
            border: 1px solid #e0e0e0; 
            padding: 12px; 
            text-align: left; 
        }}
        th {{ 
            background-color: #f5f5f5; 
            font-weight: 600;
            color: #333;
        }}
        .good {{ color: #2e7d32; font-weight: bold; }}
        .warning {{ color: #f57f17; font-weight: bold; }}
        h1, h2, h3 {{ color: #1976d2; }}
        .high-engagement {{ background-color: #e8f5e8; }}
        .medium-engagement {{ background-color: #fff3e0; }}
        .low-engagement {{ background-color: #ffebee; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Transcript Analysis Report</h1>
        
        <div class="summary">
            <h2>Summary Statistics</h2>
            <p><strong>Total Transcripts:</strong> {len(analyses)}</p>
            <p><strong>Average Student Engagement:</strong> {np.mean([a.student_ratio for a in analyses]):.1%}</p>
            <p><strong>Range:</strong> {min(a.student_ratio for a in analyses):.1%} - {max(a.student_ratio for a in analyses):.1%}</p>
            <p><strong>High Engagement Files (>40%):</strong> {len([a for a in analyses if a.student_ratio > 0.4])}</p>
        </div>
        
        <h2>Results Table</h2>
        <table>
            <tr>
                <th>Filename</th>
                <th>Student Ratio</th>
                <th>Total Words</th>
                <th>Confidence</th>
                <th>Quality Status</th>
                <th>Recommendation</th>
            </tr>
"""
    
    for analysis in sorted(analyses, key=lambda x: x.student_ratio, reverse=True):
        if not analysis.quality_flags:
            quality_status = '<span class="good">Good</span>'
        else:
            quality_status = '<span class="warning">Issues: ' + ", ".join(analysis.quality_flags) + '</span>'
        
        # Determine engagement level and recommendation
        if analysis.student_ratio > 0.4 and analysis.confidence_score > 0.7:
            recommendation = "High Priority"
            row_class = "high-engagement"
        elif analysis.student_ratio > 0.2 and analysis.confidence_score > 0.8:
            recommendation = "Medium Priority"
            row_class = "medium-engagement"
        else:
            recommendation = "Low Priority"
            row_class = "low-engagement"
        
        html_content += f"""
        <tr class="{row_class}">
            <td><strong>{analysis.filename}</strong></td>
            <td><strong>{analysis.student_ratio:.1%}</strong></td>
            <td>{analysis.total_words:,}</td>
            <td>{analysis.confidence_score:.1%}</td>
            <td>{quality_status}</td>
            <td><strong>{recommendation}</strong></td>
        </tr>
        """
    
    html_content += """
        </table>
        
        <h2>Detailed Analysis</h2>
        <p><em>Click on any transcript below to see the segment-by-segment breakdown with speaker identification.</em></p>
    """
    
    high_priority = [a for a in analyses if a.student_ratio > 0.4 and a.confidence_score > 0.7]
    if high_priority:
        html_content += """
        <h3>Recommended for Pirie-Kieren Framework Analysis</h3>
        """
        for analysis in sorted(high_priority, key=lambda x: x.student_ratio, reverse=True):
            html_content += f"""
            <div class="transcript high-engagement">
                <h4>{analysis.filename}</h4>
                <div class="stats">
                    Student Words: {analysis.student_ratio:.1%} ({analysis.student_words:,} words) | 
                    AI Words: {1-analysis.student_ratio:.1%} ({analysis.ai_words:,} words) | 
                    Confidence: {analysis.confidence_score:.1%}
                </div>
                <p><strong>Why recommended:</strong> High student engagement with reliable speaker detection</p>
            """
            
            for i, segment in enumerate(analysis.segments[:5]):  # Show first 5 segments
                segment_class = "student-segment" if segment.speaker == "Student" else "ai-segment"
                preview = segment.text[:150] + "..." if len(segment.text) > 150 else segment.text
                preview = preview.replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML
                html_content += f"""
                <div class="{segment_class}">
                    <strong>{segment.speaker}</strong> ({segment.word_count} words)
                    <span class="confidence">Confidence: {segment.confidence:.1%}</span><br>
                    {preview}
                </div>
                """
            
            if len(analysis.segments) > 5:
                html_content += f"<p><em>... and {len(analysis.segments) - 5} more segments</em></p>"
            
            html_content += "</div>"
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description='Analyze AI-Student transcripts')
    parser.add_argument('input_dir', help='Directory containing transcript files')
    parser.add_argument('--output-csv', '-c', default='analysis.csv', help='Output CSV file')
    parser.add_argument('--output-html', default='analysis.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    analyzer = SmartTranscriptAnalyzer()
    input_path = Path(args.input_dir)
    
    if not input_path.exists():
        print(f"❌ Directory not found: {args.input_dir}")
        return
    
    # Find transcript files
    transcript_files = list(input_path.rglob("*.txt"))
    
    if not transcript_files:
        print(f"❌ No .txt files found in {args.input_dir}")
        return
    
    print(f"🔍 Found {len(transcript_files)} transcript files...")
    
    analyses = []
    for file_path in transcript_files:
        print(f"📄 Analyzing {file_path.name}...")
        analysis = analyzer.analyze_transcript(str(file_path))
        analyses.append(analysis)
        
        quality_str = " ⚠️" if analysis.quality_flags else " ✅"
        print(f"   → Student: {analysis.student_ratio:.1%}, Confidence: {analysis.confidence_score:.1%}{quality_str}")
    
    # Export CSV
    df = pd.DataFrame([{
        'Filename': a.filename,
        'Student_Ratio': a.student_ratio,
        'AI_Words': a.ai_words,
        'Student_Words': a.student_words,
        'Total_Words': a.total_words,
        'Confidence': a.confidence_score,
        'Quality_Flags': '; '.join(a.quality_flags) if a.quality_flags else 'Good'
    } for a in analyses])
    
    df.to_csv(args.output_csv, index=False)
    print(f"💾 CSV exported to: {args.output_csv}")
    
    # Create HTML report
    create_html_report(analyses, args.output_html)
    print(f"🌐 HTML report created: {args.output_html}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Average student engagement: {df['Student_Ratio'].mean():.1%}")
    print(f"   Range: {df['Student_Ratio'].min():.1%} - {df['Student_Ratio'].max():.1%}")
    
    high_engagement = df[df['Student_Ratio'] > 0.4]
    print(f"   High engagement (>40%): {len(high_engagement)} files")
    
    if len(high_engagement) > 0:
        print(f"\n🎯 Recommended for Pirie-Kieren analysis:")
        for _, row in high_engagement.head(3).iterrows():
            print(f"   • {row['Filename']}: {row['Student_Ratio']:.1%} engagement")

if __name__ == "__main__":
    main()