# AI-Student Transcript Analysis Results

## Analysis Summary

**Total Transcripts Analyzed:** 8 synthetic transcript files  
**Analysis Method:** Pattern-based speaker identification with confidence scoring  
**Date:** August 16, 2025

## Key Findings

- **Average Student Engagement:** 40.3% (measured by word count ratio)
- **Engagement Range:** 0.0% - 95.2%
- **High Engagement Transcripts (>80%):** 3 files
- **Medium Engagement Transcripts (25-30%):** 2 files  
- **Low Engagement Transcripts (0%):** 3 files

## Transcript Classification by Engagement Level

### High Engagement (>80% student words)
| Filename | Student Ratio | Total Words | Notes |
|----------|---------------|-------------|--------|
| S06-B4-J8.txt | 95.2% | 1,433 | Cooking/chemistry dialogue with frequent student responses |
| S04-H9-X1.txt | 86.4% | 1,886 | Heavily corrupted text but identifiable student markers |
| S01-M5-R7.txt | 86.3% | 1,477 | Quantum computing conversation with substantial student participation |

### Medium Engagement (25-30% student words)
| Filename | Student Ratio | Total Words | Notes |
|----------|---------------|-------------|--------|
| S10-R3-Z7.txt | 28.1% | 2,294 | Grammar/linguistics discussion with clear speaker markers |
| S07-C9-M2.txt | 26.8% | 1,402 | Culinary chemistry with character interactions |

### Low Engagement (0% student words)
| Filename | Student Ratio | Total Words | Notes |
|----------|---------------|-------------|--------|
| S02-K3-Q9.txt | 0.0% | 1,154 | Neuroscience discussion - student markers not detected |
| S08-P7-L5.txt | 0.0% | 2,003 | No clear student markers identified |
| S09-E1-K6.txt | 0.0% | 2,035 | No clear student markers identified |

## Research Recommendations

### For Pirie-Kieren Framework Analysis
Based on engagement ratios as a proxy for student participation:

**Recommended for Deep Analysis:**
1. **S06-B4-J8.txt** (95.2%) - Highest student engagement
2. **S10-R3-Z7.txt** (28.1%) - Balanced dialogue with clear educational progression
3. **S01-M5-R7.txt** (86.3%) - Strong student participation in complex topic

**Note:** Files with 0% engagement may indicate either:
- Monologic AI presentations (less suitable for interaction analysis)
- Parsing challenges requiring manual review
- Different conversation formats not captured by current algorithms

## Technical Notes

### Parser Accuracy
- **High Confidence:** Transcripts with explicit speaker markers (Student:, Prof. Name:)
- **Medium Confidence:** Pattern-based classification using linguistic cues
- **Potential Issues:** Corrupted text may affect accuracy (see S04-H9-X1.txt)

### Methodology
The analysis uses multiple criteria to identify speakers:
- Explicit speaker markers (Student:, A:, Prof. Name:, etc.)
- Length patterns (AI responses tend to be longer)
- Language patterns (instructional vs. conversational)
- Mathematical/technical content (more common in AI responses)
- Confidence scoring for each segment classification

## Citation Information

*Analysis performed using custom Python transcript parser*  
*Repository: who-said-that*  
*Date: August 16, 2025*  
*Contact: Jason (on behalf of Todd, Zheng, and Tuto)*