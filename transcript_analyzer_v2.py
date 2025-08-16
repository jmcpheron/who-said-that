#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "streamlit",
#     "pandas",
#     "plotly",
#     "textstat",
#     "numpy",
#     "scikit-learn",
# ]
# ///
"""
Advanced AI-Student Transcript Analyzer v2
Uses multiple heuristics and machine learning-like features for better speaker identification
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import textstat
import numpy as np
import re
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import tempfile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import argparse
import sys

@dataclass
class TextSegment:
    """Enhanced text segment with rich features"""
    text: str
    speaker_prediction: str  # 'AI' or 'Student'
    confidence: float
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    reading_level: float
    technical_score: float
    question_count: int
    has_math: bool
    has_code: bool
    formality_score: float
    start_line: int
    end_line: int
    features: Dict[str, float]

@dataclass
class TranscriptAnalysis:
    """Complete transcript analysis with metadata"""
    filename: str
    segments: List[TextSegment]
    ai_words: int
    student_words: int
    total_words: int
    student_ratio: float
    confidence_score: float
    parsing_method: str
    quality_flags: List[str]

class AdvancedTranscriptAnalyzer:
    """Multi-approach transcript analyzer with ML-like features"""
    
    def __init__(self):
        self.setup_patterns()
        
    def setup_patterns(self):
        """Initialize all detection patterns"""
        # Explicit speaker markers
        self.explicit_student_markers = [
            r'^\s*(?:Student|student)(?:\s*\w*)?:\s*',
            r'^\s*A:\s*',
            r'^\s*Answer:\s*',
            r'^\s*Response:\s*',
            r'^\s*Me:\s*',
            r'^\s*User:\s*',
            r'^\s*[A-Z][a-z]*_?(?:Student|User|Entity)_?[A-Z]?:\s*',
        ]
        
        self.explicit_ai_markers = [
            r'^\s*(?:AI|Assistant|Claude|GPT|Bot):\s*',
            r'^\s*(?:Prof|Professor|Dr|Teacher)\.?\s*\w*:\s*',
            r'^\s*\w+\s+(?:Specialist|Assistant|Instructor|Teacher):\s*',
            r'^\s*(?:Claud-ius|DeepSeek|ChatGPT):\s*',
            r'^\s*\*[^*]*\*:\s*',  # Italicized names
        ]
        
        # Content-based patterns
        self.ai_indicators = [
            r'Let\'s\s+(?:explore|examine|calculate|derive|analyze)',
            r'(?:Your\s+)?(?:task|mission|assignment|challenge)(?:\s+is)?:\s*',
            r'Step\s+\d+[:.]',
            r'^\s*\*\*[^*]+\*\*',  # Bold headers
            r'=== Page \d+ ===',
            r'\\[.*?\\]',  # LaTeX
            r'Consider\s+(?:the|this|a)',
            r'Now\s+(?:let\'s|we\'ll|you\'ll)',
            r'(?:Excellent|Perfect|Good|Great)!\s*(?:You|Your)',
        ]
        
        self.student_indicators = [
            r'^(?:yes|no|ok|okay|sure|maybe|i think|i don\'t)',
            r'\b(?:confused|don\'t understand|not sure|help)\b',
            r'\?$',  # Ends with question
            r'\b(?:can you|could you|what if|why|how)\b',
            r'^(?:wait|but|so|um|uh|actually)',
        ]

    def extract_features(self, text: str) -> Dict[str, float]:
        """Extract linguistic and statistical features from text"""
        if not text.strip():
            return {}
            
        features = {}
        
        # Basic metrics
        features['word_count'] = len(text.split())
        features['char_count'] = len(text)
        features['sentence_count'] = max(1, len(re.findall(r'[.!?]+', text)))
        features['avg_word_length'] = np.mean([len(word) for word in re.findall(r'\b\w+\b', text)]) if text else 0
        
        # Reading level
        try:
            features['flesch_reading_ease'] = textstat.flesch_reading_ease(text)
            features['flesch_kincaid_grade'] = textstat.flesch_kincaid_grade(text)
        except:
            features['flesch_reading_ease'] = 50
            features['flesch_kincaid_grade'] = 8
        
        # Question patterns
        features['question_count'] = len(re.findall(r'\?', text))
        features['question_ratio'] = features['question_count'] / max(1, features['sentence_count'])
        
        # Technical content
        features['has_math'] = 1.0 if re.search(r'[\\$]\s*[a-zA-Z_]+|[=<>]+|\d+\s*[+\-*/]\s*\d+', text) else 0.0
        features['has_code'] = 1.0 if re.search(r'\b(?:function|def|class|import|return)\b|[{}()[\]];', text) else 0.0
        features['equation_count'] = len(re.findall(r'\\[.*?\\]|[a-z]\s*=\s*[^=]', text))
        
        # Capitalization patterns
        caps_words = re.findall(r'\b[A-Z]+\b', text)
        features['caps_ratio'] = len(caps_words) / max(1, features['word_count'])
        
        # Punctuation
        features['exclamation_count'] = len(re.findall(r'!', text))
        features['comma_count'] = len(re.findall(r',', text))
        features['semicolon_count'] = len(re.findall(r';', text))
        
        # Formality indicators
        formal_words = len(re.findall(r'\b(?:furthermore|moreover|however|therefore|consequently|thus|hence)\b', text, re.IGNORECASE))
        features['formality_score'] = formal_words / max(1, features['word_count'])
        
        # AI-specific patterns
        features['instruction_score'] = len(re.findall(r'\b(?:calculate|derive|analyze|examine|consider|determine)\b', text, re.IGNORECASE)) / max(1, features['word_count'])
        features['step_pattern'] = 1.0 if re.search(r'Step\s+\d+', text) else 0.0
        features['bullet_pattern'] = len(re.findall(r'^\s*[-*]\s', text, re.MULTILINE)) / max(1, features['sentence_count'])
        
        # Student-specific patterns  
        features['uncertainty_score'] = len(re.findall(r'\b(?:maybe|perhaps|i think|not sure|confused|don\'t understand)\b', text, re.IGNORECASE)) / max(1, features['word_count'])
        features['casual_score'] = len(re.findall(r'\b(?:yeah|ok|wow|cool|awesome|wait|um|uh)\b', text, re.IGNORECASE)) / max(1, features['word_count'])
        
        return features

    def calculate_speaker_probability(self, text: str, features: Dict[str, float]) -> Tuple[str, float]:
        """Calculate probability of speaker being AI vs Student using multiple heuristics"""
        ai_score = 0.0
        
        # Check explicit markers first
        for pattern in self.explicit_ai_markers:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return 'AI', 0.95
                
        for pattern in self.explicit_student_markers:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                return 'Student', 0.95
        
        # Content-based scoring
        for pattern in self.ai_indicators:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                ai_score += 0.15
                
        for pattern in self.student_indicators:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                ai_score -= 0.20
        
        # Feature-based scoring
        if 'word_count' in features:
            if features['word_count'] > 100:
                ai_score += 0.1
            elif features['word_count'] < 20:
                ai_score -= 0.1
                
        if 'instruction_score' in features and features['instruction_score'] > 0.02:
            ai_score += 0.15
            
        if 'uncertainty_score' in features and features['uncertainty_score'] > 0.02:
            ai_score -= 0.15
            
        if 'casual_score' in features and features['casual_score'] > 0.02:
            ai_score -= 0.15
            
        if 'has_math' in features and features['has_math']:
            ai_score += 0.1
            
        if 'formality_score' in features and features['formality_score'] > 0.01:
            ai_score += 0.1
            
        if 'question_ratio' in features and features['question_ratio'] > 0.3:
            ai_score -= 0.1
            
        if 'flesch_kincaid_grade' in features:
            if features['flesch_kincaid_grade'] > 12:
                ai_score += 0.05
            elif features['flesch_kincaid_grade'] < 8:
                ai_score -= 0.05
        
        # Convert to probability
        ai_prob = 1 / (1 + np.exp(-ai_score))  # Sigmoid
        
        if ai_prob > 0.5:
            return 'AI', ai_prob
        else:
            return 'Student', 1 - ai_prob

    def smart_segment_transcript(self, content: str) -> List[TextSegment]:
        """Intelligently segment transcript using multiple approaches"""
        lines = content.split('\n')
        segments = []
        
        # Try explicit marker approach first
        explicit_segments = self._segment_by_markers(lines)
        if explicit_segments:
            return explicit_segments
            
        # Fall back to content-based segmentation
        return self._segment_by_content(lines)

    def _segment_by_markers(self, lines: List[str]) -> List[TextSegment]:
        """Segment using explicit speaker markers"""
        segments = []
        current_segment = []
        current_speaker = None
        start_line = 0
        
        for i, line in enumerate(lines):
            if not line.strip():
                if current_segment:
                    current_segment.append(line)
                continue
                
            detected_speaker = None
            clean_text = line
            
            # Check for speaker markers
            for pattern in self.explicit_student_markers:
                if re.match(pattern, line, re.IGNORECASE):
                    detected_speaker = 'Student'
                    clean_text = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                    break
                    
            if not detected_speaker:
                for pattern in self.explicit_ai_markers:
                    if re.match(pattern, line, re.IGNORECASE):
                        detected_speaker = 'AI'
                        clean_text = re.sub(pattern, '', line, flags=re.IGNORECASE).strip()
                        break
            
            # Handle speaker changes
            if detected_speaker and detected_speaker != current_speaker:
                if current_segment:
                    segments.append(self._create_segment(current_segment, current_speaker, start_line, i-1))
                
                current_segment = [clean_text] if clean_text else []
                current_speaker = detected_speaker
                start_line = i
            else:
                current_segment.append(line)
        
        # Handle final segment
        if current_segment:
            segments.append(self._create_segment(current_segment, current_speaker, start_line, len(lines)-1))
            
        return segments

    def _segment_by_content(self, lines: List[str]) -> List[TextSegment]:
        """Segment based on content patterns and natural breaks"""
        # Combine lines into larger chunks for analysis
        chunks = []
        current_chunk = []
        
        for line in lines:
            if line.strip():
                current_chunk.append(line)
            else:
                if current_chunk and len(current_chunk) > 2:  # Minimum chunk size
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Analyze each chunk
        segments = []
        for i, chunk in enumerate(chunks):
            features = self.extract_features(chunk)
            speaker, confidence = self.calculate_speaker_probability(chunk, features)
            
            segment = TextSegment(
                text=chunk,
                speaker_prediction=speaker,
                confidence=confidence,
                word_count=features.get('word_count', 0),
                sentence_count=features.get('sentence_count', 1),
                avg_sentence_length=features.get('word_count', 0) / max(1, features.get('sentence_count', 1)),
                reading_level=features.get('flesch_kincaid_grade', 8),
                technical_score=features.get('has_math', 0) + features.get('has_code', 0),
                question_count=features.get('question_count', 0),
                has_math=features.get('has_math', 0) > 0,
                has_code=features.get('has_code', 0) > 0,
                formality_score=features.get('formality_score', 0),
                start_line=i * 10,  # Approximate
                end_line=(i + 1) * 10,
                features=features
            )
            segments.append(segment)
            
        return segments

    def _create_segment(self, lines: List[str], speaker: Optional[str], start_line: int, end_line: int) -> TextSegment:
        """Create a TextSegment from lines"""
        text = '\n'.join(lines)
        features = self.extract_features(text)
        
        if speaker:
            predicted_speaker = speaker
            confidence = 0.9
        else:
            predicted_speaker, confidence = self.calculate_speaker_probability(text, features)
        
        return TextSegment(
            text=text,
            speaker_prediction=predicted_speaker,
            confidence=confidence,
            word_count=features.get('word_count', 0),
            sentence_count=features.get('sentence_count', 1),
            avg_sentence_length=features.get('word_count', 0) / max(1, features.get('sentence_count', 1)),
            reading_level=features.get('flesch_kincaid_grade', 8),
            technical_score=features.get('has_math', 0) + features.get('has_code', 0),
            question_count=features.get('question_count', 0),
            has_math=features.get('has_math', 0) > 0,
            has_code=features.get('has_code', 0) > 0,
            formality_score=features.get('formality_score', 0),
            start_line=start_line,
            end_line=end_line,
            features=features
        )

    def analyze_transcript(self, file_path: str) -> TranscriptAnalysis:
        """Analyze a complete transcript file"""
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
                parsing_method='error',
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
                parsing_method='empty',
                quality_flags=['Empty file']
            )
        
        segments = self.smart_segment_transcript(content)
        
        # Calculate statistics
        ai_words = sum(seg.word_count for seg in segments if seg.speaker_prediction == 'AI')
        student_words = sum(seg.word_count for seg in segments if seg.speaker_prediction == 'Student')
        total_words = ai_words + student_words
        
        student_ratio = student_words / total_words if total_words > 0 else 0.0
        avg_confidence = np.mean([seg.confidence for seg in segments]) if segments else 0.0
        
        # Quality assessment
        quality_flags = []
        if avg_confidence < 0.6:
            quality_flags.append('Low confidence predictions')
        if total_words < 100:
            quality_flags.append('Very short transcript')
        if len(segments) < 3:
            quality_flags.append('Few speaker segments detected')
        
        # Determine parsing method
        has_explicit_markers = any(
            re.search(r'^\s*(?:Student|AI|Prof|Assistant):', seg.text, re.IGNORECASE | re.MULTILINE)
            for seg in segments
        )
        parsing_method = 'explicit_markers' if has_explicit_markers else 'content_analysis'
        
        return TranscriptAnalysis(
            filename=Path(file_path).name,
            segments=segments,
            ai_words=ai_words,
            student_words=student_words,
            total_words=total_words,
            student_ratio=student_ratio,
            confidence_score=avg_confidence,
            parsing_method=parsing_method,
            quality_flags=quality_flags
        )

def run_streamlit_app():
    """Run the Streamlit web interface"""
    st.set_page_config(page_title="AI-Student Transcript Analyzer", layout="wide")
    
    st.title("🎓 AI-Student Transcript Analyzer")
    st.markdown("Upload transcript files to analyze student engagement patterns")
    
    # Initialize analyzer
    if 'analyzer' not in st.session_state:
        st.session_state.analyzer = AdvancedTranscriptAnalyzer()
    
    # File upload
    uploaded_files = st.file_uploader(
        "Upload transcript files (.txt)",
        type=['txt'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        analyses = []
        
        # Process files
        progress_bar = st.progress(0)
        for i, uploaded_file in enumerate(uploaded_files):
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read().decode('utf-8'))
                tmp_path = tmp_file.name
            
            # Analyze
            analysis = st.session_state.analyzer.analyze_transcript(tmp_path)
            analysis.filename = uploaded_file.name  # Use original name
            analyses.append(analysis)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        # Display results
        st.header("📊 Analysis Results")
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transcripts", len(analyses))
        
        with col2:
            avg_engagement = np.mean([a.student_ratio for a in analyses])
            st.metric("Avg Student Engagement", f"{avg_engagement:.1%}")
        
        with col3:
            avg_confidence = np.mean([a.confidence_score for a in analyses])
            st.metric("Avg Confidence", f"{avg_confidence:.1%}")
        
        with col4:
            total_words = sum(a.total_words for a in analyses)
            st.metric("Total Words", f"{total_words:,}")
        
        # Engagement distribution chart
        df = pd.DataFrame([{
            'filename': a.filename,
            'student_ratio': a.student_ratio,
            'confidence': a.confidence_score,
            'total_words': a.total_words,
            'quality': 'Good' if not a.quality_flags else 'Needs Review'
        } for a in analyses])
        
        fig = px.scatter(
            df, 
            x='total_words', 
            y='student_ratio',
            size='confidence',
            color='quality',
            hover_name='filename',
            title="Student Engagement vs Transcript Length",
            labels={
                'student_ratio': 'Student Engagement (%)',
                'total_words': 'Total Words',
                'confidence': 'Confidence'
            }
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed transcript view
        st.header("🔍 Detailed Analysis")
        
        selected_file = st.selectbox("Select transcript to examine:", [a.filename for a in analyses])
        
        if selected_file:
            analysis = next(a for a in analyses if a.filename == selected_file)
            
            # Transcript metadata
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Metadata")
                st.write(f"**Student Ratio:** {analysis.student_ratio:.1%}")
                st.write(f"**Confidence:** {analysis.confidence_score:.1%}")
                st.write(f"**Method:** {analysis.parsing_method}")
                st.write(f"**Segments:** {len(analysis.segments)}")
                if analysis.quality_flags:
                    st.warning("Quality Issues: " + ", ".join(analysis.quality_flags))
            
            with col2:
                # Segment distribution
                segment_data = pd.DataFrame([{
                    'Speaker': seg.speaker_prediction,
                    'Words': seg.word_count,
                    'Confidence': seg.confidence
                } for seg in analysis.segments])
                
                if not segment_data.empty:
                    fig = px.pie(
                        segment_data.groupby('Speaker')['Words'].sum().reset_index(),
                        values='Words',
                        names='Speaker',
                        title="Word Distribution"
                    )
                    st.plotly_chart(fig)
            
            # Segment-by-segment view
            st.subheader("Segment Analysis")
            
            for i, segment in enumerate(analysis.segments):
                with st.expander(f"Segment {i+1}: {segment.speaker_prediction} ({segment.word_count} words, {segment.confidence:.1%} confidence)"):
                    
                    # Color code by speaker
                    if segment.speaker_prediction == 'AI':
                        st.markdown(f'<div style="background-color: #e3f2fd; padding: 10px; border-radius: 5px;">{segment.text[:500]}{"..." if len(segment.text) > 500 else ""}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="background-color: #f3e5f5; padding: 10px; border-radius: 5px;">{segment.text[:500]}{"..." if len(segment.text) > 500 else ""}</div>', unsafe_allow_html=True)
                    
                    # Show features
                    st.write(f"**Reading Level:** {segment.reading_level:.1f} | **Questions:** {segment.question_count} | **Math:** {'Yes' if segment.has_math else 'No'}")
        
        # Export functionality
        st.header("📁 Export Results")
        
        if st.button("Generate CSV Export"):
            csv_data = pd.DataFrame([{
                'Filename': a.filename,
                'Student_Ratio': a.student_ratio,
                'AI_Words': a.ai_words,
                'Student_Words': a.student_words,
                'Total_Words': a.total_words,
                'Confidence': a.confidence_score,
                'Parsing_Method': a.parsing_method,
                'Quality_Flags': '; '.join(a.quality_flags)
            } for a in analyses])
            
            st.download_button(
                label="Download CSV",
                data=csv_data.to_csv(index=False),
                file_name="transcript_analysis.csv",
                mime="text/csv"
            )

def run_cli(input_dir: str, output_csv: str = "analysis.csv"):
    """Run command-line analysis"""
    analyzer = AdvancedTranscriptAnalyzer()
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"Error: Directory {input_dir} does not exist")
        return
    
    # Find transcript files
    transcript_files = list(input_path.rglob("*.txt")) + list(input_path.rglob("*.docx"))
    
    if not transcript_files:
        print(f"No transcript files found in {input_dir}")
        return
    
    print(f"Found {len(transcript_files)} transcript files...")
    
    analyses = []
    for file_path in transcript_files:
        print(f"Analyzing {file_path.name}...")
        analysis = analyzer.analyze_transcript(str(file_path))
        analyses.append(analysis)
        print(f"  → Student: {analysis.student_ratio:.1%}, Confidence: {analysis.confidence_score:.1%}")
    
    # Export results
    df = pd.DataFrame([{
        'Filename': a.filename,
        'Student_Ratio': a.student_ratio,
        'AI_Words': a.ai_words,
        'Student_Words': a.student_words,
        'Total_Words': a.total_words,
        'Confidence': a.confidence_score,
        'Parsing_Method': a.parsing_method,
        'Quality_Flags': '; '.join(a.quality_flags)
    } for a in analyses])
    
    df.to_csv(output_csv, index=False)
    print(f"\nResults exported to {output_csv}")
    
    # Summary
    print(f"\nSummary:")
    print(f"Average student engagement: {df['Student_Ratio'].mean():.1%}")
    print(f"Range: {df['Student_Ratio'].min():.1%} - {df['Student_Ratio'].max():.1%}")
    print(f"High engagement (>40%): {len(df[df['Student_Ratio'] > 0.4])} files")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Run Streamlit app
        run_streamlit_app()
    else:
        # Run CLI
        parser = argparse.ArgumentParser(description="Analyze AI-Student transcripts")
        parser.add_argument("input_dir", help="Directory containing transcript files")
        parser.add_argument("--output", "-o", default="analysis.csv", help="Output CSV file")
        args = parser.parse_args()
        
        run_cli(args.input_dir, args.output)