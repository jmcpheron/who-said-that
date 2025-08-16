// Who Said That? - Interactive Transcript Analyzer
// Main JavaScript Application Logic

class TranscriptAnalyzer {
    constructor() {
        this.transcripts = [];
        this.charts = {};
        this.currentSort = { field: 'filename', order: 'asc' };
        this.filters = { engagement: 0, confidence: 0, search: '', speaker: 'all' };
        
        this.initializeApp();
        this.setupEventListeners();
    }

    initializeApp() {
        console.log('🗣️ Who Said That? Analyzer initialized');
        this.updateDashboard();
    }

    setupEventListeners() {
        // File upload
        document.getElementById('browse-btn').addEventListener('click', () => {
            document.getElementById('file-input').click();
        });
        
        document.getElementById('file-input').addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Drag and drop
        const uploadArea = document.getElementById('upload-area');
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            this.handleFiles(e.dataTransfer.files);
        });

        // Demo button
        document.getElementById('demo-btn').addEventListener('click', () => {
            this.loadDemoData();
        });

        // Filters
        document.getElementById('engagement-filter').addEventListener('input', (e) => {
            this.filters.engagement = parseInt(e.target.value);
            document.getElementById('engagement-value').textContent = `${e.target.value}%`;
            this.applyFilters();
        });

        document.getElementById('confidence-filter').addEventListener('input', (e) => {
            this.filters.confidence = parseInt(e.target.value);
            document.getElementById('confidence-value').textContent = `${e.target.value}%`;
            this.applyFilters();
        });

        // Search
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.filters.search = e.target.value.toLowerCase();
            this.applyFilters();
        });

        document.getElementById('clear-search').addEventListener('click', () => {
            document.getElementById('search-input').value = '';
            this.filters.search = '';
            this.applyFilters();
        });
        
        // Speaker filter
        document.getElementById('speaker-filter').addEventListener('change', (e) => {
            this.filters.speaker = e.target.value;
            this.applyFilters();
        });

        // Sorting
        document.getElementById('sort-select').addEventListener('change', (e) => {
            this.currentSort.field = e.target.value;
            this.applySort();
        });

        document.getElementById('sort-order').addEventListener('click', () => {
            this.currentSort.order = this.currentSort.order === 'asc' ? 'desc' : 'asc';
            document.getElementById('sort-order').textContent = this.currentSort.order === 'asc' ? '↓' : '↑';
            this.applySort();
        });

        // Export
        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportAnalysis();
        });

        // Modal
        document.getElementById('close-modal').addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('close-modal-btn').addEventListener('click', () => {
            this.closeModal();
        });

        // Close modal on outside click
        document.getElementById('detail-modal').addEventListener('click', (e) => {
            if (e.target.id === 'detail-modal') {
                this.closeModal();
            }
        });
    }

    async handleFiles(files) {
        const validFiles = Array.from(files).filter(file => 
            file.type === 'text/plain' || file.name.endsWith('.txt')
        );

        if (validFiles.length === 0) {
            alert('Please select valid .txt files');
            return;
        }

        this.showLoading(true);
        this.showProgress(true);

        try {
            for (let i = 0; i < validFiles.length; i++) {
                const file = validFiles[i];
                const progress = ((i + 1) / validFiles.length) * 100;
                this.updateProgress(progress, `Processing ${file.name}...`);

                const text = await this.readFile(file);
                const analysis = this.analyzeTranscript(text, file.name);
                this.transcripts.push(analysis);

                // Small delay to show progress
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            this.showDashboard();
            this.updateDashboard();
            this.renderFileList();
            this.createCharts();

        } catch (error) {
            console.error('Error processing files:', error);
            alert('Error processing files. Please try again.');
        } finally {
            this.showLoading(false);
            this.showProgress(false);
        }
    }

    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    analyzeTranscript(text, filename) {
        const lines = text.split('\n'); // Don't filter empty lines - keep ALL content
        const result = this.identifySegments(lines);
        const segments = result.segments;
        
        let aiWords = 0;
        let studentWords = 0;
        let unknownWords = 0;

        segments.forEach(segment => {
            if (segment.speaker === 'AI') {
                aiWords += segment.wordCount;
            } else if (segment.speaker === 'Student') {
                studentWords += segment.wordCount;
            } else {
                unknownWords += segment.wordCount;
            }
        });

        const totalWords = aiWords + studentWords + unknownWords;
        const studentRatio = totalWords > 0 ? (studentWords / totalWords) * 100 : 0;
        const avgConfidence = segments.length > 0 
            ? segments.reduce((sum, seg) => sum + seg.confidence, 0) / segments.length * 100
            : 0;
        
        // Calculate coverage - what percentage of the file was analyzed
        const totalTextLines = lines.filter(line => line.trim()).length;
        const analyzedLines = result.analyzedLines;
        const coverage = totalTextLines > 0 ? (analyzedLines / totalTextLines) * 100 : 0;

        return {
            filename,
            segments,
            aiWords,
            studentWords,
            unknownWords,
            totalWords,
            studentRatio,
            avgConfidence,
            coverage,
            totalLines: lines.length,
            analyzedLines,
            rawText: text
        };
    }

    identifySegments(lines) {
        const segments = [];
        let currentSegment = null;
        let analyzedLines = 0;

        // Enhanced speaker identification patterns based on real transcript analysis
        const studentPatterns = [
            {
                pattern: /^A:\s*(.*)$/i,  // Primary student answer marker
                confidence: 0.98,
                captureGroup: 1 // Capture the content after "A:"
            },
            {
                pattern: /^Student:\s*(.*)$/i,
                confidence: 0.95,
                captureGroup: 1
            },
            {
                pattern: /^Answer:\s*(.*)$/i,
                confidence: 0.9,
                captureGroup: 1
            },
            {
                pattern: /^Response:\s*(.*)$/i,
                confidence: 0.9,
                captureGroup: 1
            }
        ];

        const aiPatterns = [
            {
                pattern: /^\*".*"\*?$/,  // Quoted instructions - highest priority
                confidence: 0.98,
                captureGroup: 0
            },
            {
                pattern: /^\*.*\*$/,  // Any italicized content - very high priority
                confidence: 0.95,
                captureGroup: 0
            },
            {
                pattern: /^\*\*.*\*\*$/,  // Bold headers
                confidence: 0.97,
                captureGroup: 0
            },
            {
                pattern: /^### .+$/,  // Markdown headers
                confidence: 0.96,
                captureGroup: 0
            },
            {
                pattern: /^(Step \d+|STEP \d+)[:.].*$/i,
                confidence: 0.97,
                captureGroup: 0
            },
            {
                pattern: /^(Excellent|Outstanding|Perfect|Great|Good|Correct)\b.*$/i,  // AI feedback
                confidence: 0.95,
                captureGroup: 0
            },
            {
                pattern: /^(Got it|Let's|Your task|Welcome|Greetings|Preparation)\b.*$/i,
                confidence: 0.9,
                captureGroup: 0
            },
            {
                pattern: /^[—–-]\s*.+$/,  // Bullet points with various dashes
                confidence: 0.88,
                captureGroup: 0
            },
            {
                pattern: /^\d+\.\s*.+$/,  // Numbered lists
                confidence: 0.87,
                captureGroup: 0
            },
            {
                pattern: /^\([a-z]\)\s*.+$/i,  // Lettered lists (a), (b), etc.
                confidence: 0.85,
                captureGroup: 0
            },
            {
                pattern: /^".*"$/,  // Direct quotes (without asterisks)
                confidence: 0.83,
                captureGroup: 0
            }
        ];

        // Metadata patterns (content that's not from AI or student speakers)
        const metadataPatterns = [
            {
                pattern: /^=== Page \d+ ===$/,
                confidence: 1.0
            },
            {
                pattern: /^\s*$/,  // Empty lines
                confidence: 1.0
            },
            {
                pattern: /^\\\[(.*)\\\]$/,  // LaTeX display math
                confidence: 0.9
            },
            {
                pattern: /^\\\((.*)\\\)$/,  // LaTeX inline math
                confidence: 0.9
            }
        ];

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            const trimmedLine = line.trim();
            
            // Handle metadata lines
            let isMetadata = false;
            for (const meta of metadataPatterns) {
                if (meta.pattern.test(trimmedLine)) {
                    if (trimmedLine) {  // Only count non-empty metadata
                        if (currentSegment) {
                            segments.push({ ...currentSegment });
                        }
                        segments.push({
                            text: line,
                            speaker: 'Metadata',
                            confidence: meta.confidence,
                            startLine: i,
                            endLine: i,
                            wordCount: this.countWords(trimmedLine)
                        });
                        currentSegment = null;
                    }
                    isMetadata = true;
                    break;
                }
            }
            
            if (isMetadata) continue;

            if (!trimmedLine) {
                // Preserve empty lines within segments
                if (currentSegment) {
                    currentSegment.text += '\n';
                }
                continue;
            }

            analyzedLines++;
            
            let speaker = null;
            let confidence = 0.5;
            let cleanText = trimmedLine;

            // Check for explicit student markers first (highest priority)
            for (const studentMarker of studentPatterns) {
                const match = trimmedLine.match(studentMarker.pattern);
                if (match) {
                    speaker = 'Student';
                    confidence = studentMarker.confidence;
                    // Extract the content after the marker, or use the captured group
                    if (studentMarker.captureGroup && match[studentMarker.captureGroup]) {
                        cleanText = match[studentMarker.captureGroup].trim();
                    } else {
                        cleanText = trimmedLine.replace(studentMarker.pattern, '').trim();
                    }
                    break;
                }
            }

            // Check for AI markers if no student marker found
            if (!speaker) {
                for (const aiMarker of aiPatterns) {
                    const match = trimmedLine.match(aiMarker.pattern);
                    if (match) {
                        speaker = 'AI';
                        confidence = aiMarker.confidence;
                        // Extract the content after the marker, or use the captured group
                        if (aiMarker.captureGroup !== undefined && match[aiMarker.captureGroup]) {
                            cleanText = match[aiMarker.captureGroup].trim();
                        } else {
                            cleanText = trimmedLine.replace(aiMarker.pattern, '').trim();
                        }
                        break;
                    }
                }
            }

            // Content-based analysis if no explicit markers
            if (!speaker) {
                const result = this.classifyBySpeakerContent(trimmedLine);
                speaker = result.speaker;
                confidence = result.confidence;
                cleanText = trimmedLine;
                
                // If still no clear classification, use better defaults
                if (speaker === 'Unknown' || confidence < 0.6) {
                    // Default to AI for long instructional content
                    if (trimmedLine.length > 50 && this.hasInstructionalWords(trimmedLine)) {
                        speaker = 'AI';
                        confidence = 0.75;
                    }
                    // Default to student for short responses or after seeing student content
                    else if (currentSegment && currentSegment.speaker === 'Student' && trimmedLine.length < 30) {
                        speaker = 'Student';
                        confidence = 0.7;
                    }
                }
            }

            // Create or extend segment with improved logic
            if (currentSegment && this.shouldContinueSegment(currentSegment, speaker, confidence, trimmedLine)) {
                // Continue current segment
                currentSegment.text += (currentSegment.text ? '\n' : '') + line;
                currentSegment.wordCount += this.countWords(cleanText);
                currentSegment.confidence = Math.max(currentSegment.confidence, confidence);
                currentSegment.endLine = i;
            } else {
                // Start new segment
                if (currentSegment) {
                    segments.push({ ...currentSegment });
                }
                currentSegment = {
                    text: line,
                    speaker,
                    confidence,
                    startLine: i,
                    endLine: i,
                    wordCount: this.countWords(cleanText),
                    debug: {
                        originalLine: trimmedLine,
                        cleanedText: cleanText,
                        detectionReason: speaker === 'Student' ? 'Student marker' : 
                                       speaker === 'AI' ? 'AI marker' : 'Content analysis'
                    }
                };
            }
        }

        // Add final segment
        if (currentSegment) {
            segments.push(currentSegment);
        }

        return { segments, analyzedLines };
    }

    shouldContinueSegment(currentSegment, newSpeaker, newConfidence, trimmedLine) {
        // Always continue if same speaker with high confidence
        if (currentSegment.speaker === newSpeaker && newConfidence > 0.8) {
            return true;
        }
        
        // Strong continuation for student responses after A:
        if (currentSegment.speaker === 'Student' && newSpeaker !== 'AI') {
            // Continue student responses unless we hit a clear AI marker
            if (!this.isStrongAIMarker(trimmedLine)) {
                return true;
            }
        }
        
        // Continue AI instructional content
        if (currentSegment.speaker === 'AI' && newSpeaker !== 'Student') {
            // Continue AI unless we hit student marker
            if (!trimmedLine.match(/^A:/i) && newConfidence < 0.9) {
                return true;
            }
        }
        
        // If current segment has low confidence and new detection is high confidence, switch
        if (currentSegment.confidence < 0.7 && newConfidence > 0.9) {
            return false;
        }
        
        // Otherwise, only continue if same speaker
        return currentSegment.speaker === newSpeaker;
    }
    
    hasInstructionalWords(text) {
        const instructionalPatterns = [
            /\b(calculate|solve|analyze|determine|explain|describe|write|sketch)\b/i,
            /\b(your task|assignment|exercise|problem)\b/i,
            /\b(let's|now|here's|this|we'll)\b/i,
            /\b(step|approach|method|solution)\b/i
        ];
        return instructionalPatterns.some(pattern => pattern.test(text));
    }
    
    isStrongAIMarker(text) {
        // Check if this line has a strong AI indicator that should break student continuation
        const strongAIPatterns = [
            /^\*.*\*/,  // Italicized
            /^\*\*.*\*\*/,  // Bold
            /^### /,  // Headers
            /^(Step \d+|STEP \d+)[:.]/ ,
            /^(Excellent|Outstanding|Perfect|Great|Good)/i,
            /^\d+\./,  // Numbered lists
            /^[—–-]\s/  // Bullet points
        ];
        return strongAIPatterns.some(pattern => pattern.test(text));
    }
    
    isLikelyAIContent(text) {
        // Quick heuristics to identify AI content without explicit markers
        const aiIndicators = [
            /^\*\*[^*]+\*\*$/,  // Bold headers
            /^\d+\./,  // Numbered lists
            /^[—–-]\s/,  // Bullet points
            /^(Excellent|Great|Perfect|Outstanding|Good)/i,
            /^(Let\'s|Your|Now|Here\'s|This)/i,
            /\*[^*]+\*/,  // Any italicized content
            /["\u201c\u201d]/  // Quotes
        ];
        
        return aiIndicators.some(pattern => pattern.test(text));
    }

    classifyBySpeakerContent(text) {
        const features = this.analyzeTextFeatures(text);
        let aiScore = 0;
        
        // Enhanced content-based classification with higher thresholds
        
        // Quoted content (very strong AI indicator)
        if (features.hasQuotedInstructions) {
            aiScore += 1.2;
        }
        
        // Instructional language (strong AI indicator)
        if (features.hasInstructional) {
            aiScore += 0.8;
        }
        
        // Structured format (strong AI indicator)
        if (features.hasStructuredFormat) {
            aiScore += 0.7;
        }
        
        // Feedback patterns (very strong AI indicator)
        if (features.hasFeedback) {
            aiScore += 1.0;
        }
        
        // Length-based heuristics (refined)
        if (features.wordCount < 3) {
            aiScore -= 0.6; // Very short responses likely student
        } else if (features.wordCount > 40) {
            aiScore += 0.4; // Longer explanations more likely AI
        }

        // Content pattern analysis
        if (features.isQuestion && features.wordCount < 15) {
            aiScore -= 0.7; // Short questions more likely from students
        }
        
        // Mathematical expressions (context dependent)
        if (features.hasLatex || features.hasComplexMath) {
            if (features.hasInstructional) {
                aiScore += 0.5; // Math + instruction = AI
            } else {
                aiScore -= 0.2; // Math alone could be student work
            }
        }
        
        // Uncertainty and casual language (student indicators)
        if (features.hasUncertainty) {
            aiScore -= 0.5;
        }
        
        if (features.hasCasual) {
            aiScore -= 0.6;
        }
        
        // Mathematical calculations (could be student work)
        if (features.hasCalculations && !features.hasInstructional) {
            aiScore -= 0.3;
        }

        // Convert score to probability with higher confidence
        const aiProbability = 1 / (1 + Math.exp(-1.5 * aiScore));
        
        if (aiProbability > 0.8) {
            return { speaker: 'AI', confidence: Math.min(0.9, aiProbability) };
        } else if (aiProbability < 0.2) {
            return { speaker: 'Student', confidence: Math.min(0.9, 1 - aiProbability) };
        } else {
            // Reduce Unknown classifications - default to AI for instructional content
            if (features.wordCount > 20 && (features.hasInstructional || features.hasQuotedInstructions)) {
                return { speaker: 'AI', confidence: 0.75 };
            }
            return { speaker: 'Unknown', confidence: 0.5 };
        }
    }

    analyzeTextFeatures(text) {
        const wordCount = this.countWords(text);
        const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
        
        return {
            wordCount,
            sentenceCount: sentences.length,
            isQuestion: /[?]/.test(text),
            
            // Enhanced mathematical content detection
            hasLatex: /\\\([^)]+\\\)|\\\[[^\]]+\\\]|\\[a-zA-Z]+\{/.test(text),
            hasComplexMath: /[∑∏∫√π∞≈≤≥∈∀∃⊕⊗]|\\frac\{|\\text\{/.test(text),
            hasCalculations: /\d+\s*[+\-*/=]\s*\d+|\d+\.\d+|\([^)]*\d[^)]*\)|\d+\s*%/.test(text),
            
            // Instructional patterns
            hasInstructional: /\b(let's|step|calculate|derive|analyze|examine|explore|determine|construct|formulate|consider|write|sketch|solve|grab|think|address)\b/i.test(text),
            hasQuotedInstructions: /\*?["\u201c\u201d][^"\u201c\u201d]*["\u201c\u201d]\*?|\*.*\*/.test(text),
            
            // Structure indicators  
            hasStructuredFormat: /^\s*[\d•–—-]|^\s*\([a-z]\)|^\s*[ivx]+\.|^\*\*|^###/i.test(text),
            hasBold: /\*\*[^*]+\*\*/.test(text),
            hasItalics: /\*[^*]+\*/.test(text),
            
            // Feedback and response patterns
            hasFeedback: /\b(excellent|outstanding|perfect|exceptional|correct|good|great|well done|got it|right|exactly)\b/i.test(text),
            hasUncertainty: /\b(maybe|perhaps|might|could|probably|think|guess|not sure|i believe|seems like)\b/i.test(text),
            hasCasual: /\b(yeah|ok|cool|awesome|hmm|uh|er|wow|nice)\b/i.test(text),
            
            // Educational content
            hasExamples: /\b(example|for instance|e\.g\.|such as)\b/i.test(text),
            hasTask: /\b(your task|assignment|exercise|problem|challenge)\b/i.test(text),
            
            avgWordsPerSentence: sentences.length > 0 ? wordCount / sentences.length : 0
        };
    }

    countWords(text) {
        return text.trim().split(/\s+/).filter(word => word.length > 0).length;
    }

    showDashboard() {
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        document.getElementById('export-btn').disabled = false;
    }

    updateDashboard() {
        if (this.transcripts.length === 0) return;

        const totalFiles = this.transcripts.length;
        const totalWords = this.transcripts.reduce((sum, t) => sum + t.totalWords, 0);
        const avgEngagement = this.transcripts.reduce((sum, t) => sum + t.studentRatio, 0) / totalFiles;
        const avgConfidence = this.transcripts.reduce((sum, t) => sum + t.avgConfidence, 0) / totalFiles;

        document.getElementById('total-files').textContent = totalFiles;
        document.getElementById('total-words').textContent = totalWords.toLocaleString();
        document.getElementById('avg-engagement').textContent = `${avgEngagement.toFixed(1)}%`;
        document.getElementById('avg-confidence').textContent = `${avgConfidence.toFixed(1)}%`;
        
        // Add coverage information if element exists
        const avgCoverage = this.transcripts.reduce((sum, t) => sum + (t.coverage || 100), 0) / totalFiles;
        const coverageElement = document.getElementById('avg-coverage');
        if (coverageElement) {
            coverageElement.textContent = `${avgCoverage.toFixed(1)}%`;
        }
    }

    renderFileList() {
        const container = document.getElementById('file-list');
        const filteredTranscripts = this.getFilteredTranscripts();
        
        container.innerHTML = '';

        filteredTranscripts.forEach(transcript => {
            const card = this.createFileCard(transcript);
            container.appendChild(card);
        });

        if (filteredTranscripts.length === 0) {
            container.innerHTML = '<div class="no-results">No transcripts match your filters</div>';
        }
    }

    createFileCard(transcript) {
        const card = document.createElement('div');
        card.className = 'file-card';
        
        const engagementClass = transcript.studentRatio > 30 ? 'high' : 
                               transcript.studentRatio > 10 ? 'medium' : 'low';
        
        const confidenceClass = transcript.avgConfidence > 70 ? 'high' : 
                               transcript.avgConfidence > 50 ? 'medium' : 'low';

        card.innerHTML = `
            <div class="file-card-header">
                <h4>${transcript.filename}</h4>
                <button class="view-details-btn" data-filename="${transcript.filename}">
                    View Details
                </button>
            </div>
            <div class="file-card-stats">
                <div class="stat-item">
                    <span class="stat-label">Student Engagement:</span>
                    <span class="stat-value engagement-${engagementClass}">
                        ${transcript.studentRatio.toFixed(1)}%
                    </span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Confidence:</span>
                    <span class="stat-value confidence-${confidenceClass}">
                        ${transcript.avgConfidence.toFixed(1)}%
                    </span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Total Words:</span>
                    <span class="stat-value">${transcript.totalWords.toLocaleString()}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">AI vs Student:</span>
                    <span class="stat-value">${transcript.aiWords} vs ${transcript.studentWords}${transcript.unknownWords > 0 ? ` (+${transcript.unknownWords} unknown)` : ''}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Coverage:</span>
                    <span class="stat-value coverage-${transcript.coverage > 95 ? 'high' : transcript.coverage > 80 ? 'medium' : 'low'}">
                        ${transcript.coverage ? transcript.coverage.toFixed(1) : '100.0'}%
                    </span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Lines Analyzed:</span>
                    <span class="stat-value">${transcript.analyzedLines || transcript.totalLines} / ${transcript.totalLines}</span>
                </div>
            </div>
            <div class="engagement-bar">
                <div class="engagement-fill" style="width: ${transcript.studentRatio}%"></div>
            </div>
        `;

        // Add click handler for details
        card.querySelector('.view-details-btn').addEventListener('click', () => {
            this.showTranscriptDetails(transcript);
        });

        return card;
    }

    showTranscriptDetails(transcript) {
        const modal = document.getElementById('detail-modal');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');

        title.textContent = `${transcript.filename} - Detailed Analysis`;

        const coverageWarning = transcript.coverage < 90 ? 
            `<div class="coverage-warning">⚠️ Only ${transcript.coverage.toFixed(1)}% of the file was analyzed. Some content may be missing.</div>` : '';
        
        const speakerStats = {
            AI: transcript.segments.filter(s => s.speaker === 'AI').length,
            Student: transcript.segments.filter(s => s.speaker === 'Student').length,
            Unknown: transcript.segments.filter(s => s.speaker === 'Unknown').length,
            Metadata: transcript.segments.filter(s => s.speaker === 'Metadata').length
        };

        body.innerHTML = `
            ${coverageWarning}
            <div class="detail-stats">
                <div class="detail-stat">
                    <h4>📊 Overall Statistics</h4>
                    <p><strong>Student Engagement:</strong> ${transcript.studentRatio.toFixed(1)}%</p>
                    <p><strong>Average Confidence:</strong> ${transcript.avgConfidence.toFixed(1)}%</p>
                    <p><strong>Total Segments:</strong> ${transcript.segments.length}</p>
                    <p><strong>Word Distribution:</strong> AI: ${transcript.aiWords}, Student: ${transcript.studentWords}${transcript.unknownWords > 0 ? `, Unknown: ${transcript.unknownWords}` : ''}</p>
                    <p><strong>Coverage:</strong> ${transcript.coverage ? transcript.coverage.toFixed(1) : '100.0'}% (${transcript.analyzedLines}/${transcript.totalLines} lines)</p>
                    <p><strong>Speaker Segments:</strong> AI: ${speakerStats.AI}, Student: ${speakerStats.Student}${speakerStats.Unknown > 0 ? `, Unknown: ${speakerStats.Unknown}` : ''}${speakerStats.Metadata > 0 ? `, Metadata: ${speakerStats.Metadata}` : ''}</p>
                </div>
                <div class="debug-controls">
                    <button id="toggle-debug" class="btn btn-secondary">Show Debug Info</button>
                    <div id="debug-info" style="display: none;">
                        <h5>🔧 Debug Information</h5>
                        <div class="debug-summary"></div>
                    </div>
                </div>
            </div>
            
            <div class="segments-container">
                <div class="segments-header">
                    <h4>💬 Conversation Segments</h4>
                    <div class="segment-filters">
                        <button class="segment-filter-btn active" data-speaker="all">All</button>
                        <button class="segment-filter-btn" data-speaker="AI">AI (${speakerStats.AI})</button>
                        <button class="segment-filter-btn" data-speaker="Student">Student (${speakerStats.Student})</button>
                        ${speakerStats.Unknown > 0 ? `<button class="segment-filter-btn" data-speaker="Unknown">Unknown (${speakerStats.Unknown})</button>` : ''}
                        ${speakerStats.Metadata > 0 ? `<button class="segment-filter-btn" data-speaker="Metadata">Metadata (${speakerStats.Metadata})</button>` : ''}
                    </div>
                </div>
                ${transcript.segments.map((segment, index) => `
                    <div class="segment-detail ${segment.speaker.toLowerCase()}-segment" data-speaker="${segment.speaker}" data-confidence="${segment.confidence}">
                        <div class="segment-header">
                            <span class="speaker-label">${segment.speaker}</span>
                            <span class="line-info">Lines ${segment.startLine + 1}${segment.endLine !== segment.startLine ? `-${segment.endLine + 1}` : ''}</span>
                            <span class="word-count">${segment.wordCount} words</span>
                            <span class="confidence-badge confidence-${this.getConfidenceClass(segment.confidence)}">
                                ${(segment.confidence * 100).toFixed(0)}% confidence
                            </span>
                            ${segment.debug ? `<span class="debug-toggle" data-segment="${index}" title="Show debug info">🔍</span>` : ''}
                        </div>
                        <div class="segment-text">${this.highlightText(segment.text)}</div>
                        ${segment.debug ? `
                            <div class="segment-debug" id="debug-${index}" style="display: none;">
                                <h6>Debug Info:</h6>
                                <p><strong>Detection:</strong> ${segment.debug.detectionReason}</p>
                                <p><strong>Original:</strong> <code>${segment.debug.originalLine}</code></p>
                                <p><strong>Cleaned:</strong> <code>${segment.debug.cleanedText}</code></p>
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
        
        // Add segment filter functionality
        const filterButtons = modal.querySelectorAll('.segment-filter-btn');
        const segments = modal.querySelectorAll('.segment-detail');
        
        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active button
                filterButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const targetSpeaker = btn.dataset.speaker;
                
                // Show/hide segments
                segments.forEach(segment => {
                    if (targetSpeaker === 'all' || segment.dataset.speaker === targetSpeaker) {
                        segment.style.display = 'block';
                    } else {
                        segment.style.display = 'none';
                    }
                });
            });
        });
        
        // Add debug functionality
        const debugToggleBtn = modal.querySelector('#toggle-debug');
        const debugInfo = modal.querySelector('#debug-info');
        const debugToggles = modal.querySelectorAll('.debug-toggle');
        
        if (debugToggleBtn) {
            debugToggleBtn.addEventListener('click', () => {
                const isVisible = debugInfo.style.display !== 'none';
                debugInfo.style.display = isVisible ? 'none' : 'block';
                debugToggleBtn.textContent = isVisible ? 'Show Debug Info' : 'Hide Debug Info';
                
                // Generate debug summary
                if (!isVisible) {
                    this.generateDebugSummary(transcript, debugInfo.querySelector('.debug-summary'));
                }
            });
        }
        
        debugToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const segmentIndex = toggle.dataset.segment;
                const debugDiv = modal.querySelector(`#debug-${segmentIndex}`);
                if (debugDiv) {
                    const isVisible = debugDiv.style.display !== 'none';
                    debugDiv.style.display = isVisible ? 'none' : 'block';
                    toggle.textContent = isVisible ? '🔍' : '🔎';
                }
            });
        });

        modal.style.display = 'flex';
    }

    getConfidenceClass(confidence) {
        return confidence > 0.7 ? 'high' : confidence > 0.5 ? 'medium' : 'low';
    }

    generateDebugSummary(transcript, container) {
        const detectionStats = {
            'Student marker': 0,
            'AI marker': 0,
            'Content analysis': 0,
            'Unknown': 0
        };
        
        const confidenceRanges = {
            'High (90-100%)': 0,
            'Good (70-89%)': 0,
            'Medium (50-69%)': 0,
            'Low (0-49%)': 0
        };
        
        transcript.segments.forEach(segment => {
            if (segment.debug && segment.debug.detectionReason) {
                detectionStats[segment.debug.detectionReason] = (detectionStats[segment.debug.detectionReason] || 0) + 1;
            }
            
            const conf = segment.confidence * 100;
            if (conf >= 90) confidenceRanges['High (90-100%)']++;
            else if (conf >= 70) confidenceRanges['Good (70-89%)']++;
            else if (conf >= 50) confidenceRanges['Medium (50-69%)']++;
            else confidenceRanges['Low (0-49%)']++;
        });
        
        container.innerHTML = `
            <div class="debug-section">
                <h6>Detection Methods Used:</h6>
                ${Object.entries(detectionStats).map(([method, count]) => 
                    `<p>${method}: ${count} segments</p>`
                ).join('')}
            </div>
            <div class="debug-section">
                <h6>Confidence Distribution:</h6>
                ${Object.entries(confidenceRanges).map(([range, count]) => 
                    `<p>${range}: ${count} segments</p>`
                ).join('')}
            </div>
        `;
    }
    
    highlightText(text) {
        // Enhanced highlighting for better readability
        return text
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>') // Bold text
            .replace(/\*([^*]+)\*/g, '<em>$1</em>') // Italic text
            .replace(/([?])/g, '<span class="question-mark">$1</span>') // Questions
            .replace(/([∑∏∫√π∞≈≤≥∈∀∃⊕⊗])/g, '<span class="math-symbol">$1</span>') // Math symbols
            .replace(/(A:|Student:|AI:|Assistant:)/gi, '<span class="speaker-marker">$1</span>') // Speaker markers
            .replace(/(=== Page \d+ ===)/g, '<span class="page-marker">$1</span>') // Page markers
            .replace(/\\\([^)]+\\\)/g, '<span class="latex-inline">$&</span>') // LaTeX inline math
            .replace(/\\\[[^\]]+\\\]/g, '<span class="latex-display">$&</span>') // LaTeX display math
            .replace(/\\([^\s]+)\{/g, '<span class="latex-command">\\$1{</span>') // LaTeX commands
            .replace(/\|([^|]+)\|/g, '<span class="math-expression">|$1|</span>'); // Math expressions
    }

    closeModal() {
        document.getElementById('detail-modal').style.display = 'none';
    }

    getFilteredTranscripts() {
        return this.transcripts.filter(transcript => {
            const matchesEngagement = transcript.studentRatio >= this.filters.engagement;
            const matchesConfidence = transcript.avgConfidence >= this.filters.confidence;
            const matchesSearch = this.filters.search === '' || 
                transcript.filename.toLowerCase().includes(this.filters.search) ||
                transcript.rawText.toLowerCase().includes(this.filters.search);
            
            // Speaker filter logic
            let matchesSpeaker = true;
            if (this.filters.speaker !== 'all') {
                const hasTargetSpeaker = transcript.segments.some(segment => 
                    segment.speaker.toLowerCase() === this.filters.speaker.toLowerCase());
                matchesSpeaker = hasTargetSpeaker;
            }

            return matchesEngagement && matchesConfidence && matchesSearch && matchesSpeaker;
        });
    }

    applyFilters() {
        this.renderFileList();
        this.updateCharts();
    }

    applySort() {
        this.renderFileList();
    }

    createCharts() {
        this.createEngagementChart();
        this.createScatterChart();
        this.createConfidenceDistributionChart();
    }

    createEngagementChart() {
        const ctx = document.getElementById('engagement-chart').getContext('2d');
        
        if (this.charts.engagement) {
            this.charts.engagement.destroy();
        }

        const data = this.transcripts.map(t => t.studentRatio);
        const labels = this.transcripts.map(t => t.filename);

        this.charts.engagement = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Student Engagement %',
                    data: data,
                    backgroundColor: data.map(val => 
                        val > 30 ? '#22c55e' : val > 10 ? '#f59e0b' : '#ef4444'
                    ),
                    borderColor: '#374151',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Student Engagement (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Transcript Files'
                        }
                    }
                }
            }
        });
    }

    createScatterChart() {
        const ctx = document.getElementById('scatter-chart').getContext('2d');
        
        if (this.charts.scatter) {
            this.charts.scatter.destroy();
        }

        const data = this.transcripts.map(t => ({
            x: t.avgConfidence,
            y: t.studentRatio,
            label: t.filename
        }));

        this.charts.scatter = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Transcripts',
                    data: data,
                    backgroundColor: '#3b82f6',
                    borderColor: '#1d4ed8',
                    pointRadius: 8,
                    pointHoverRadius: 12
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const point = context.parsed;
                                const filename = data[context.dataIndex].label;
                                return `${filename}: ${point.y.toFixed(1)}% engagement, ${point.x.toFixed(1)}% confidence`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Average Confidence (%)'
                        },
                        min: 0,
                        max: 100
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Student Engagement (%)'
                        },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    createConfidenceDistributionChart() {
        const ctx = document.getElementById('confidence-dist-chart').getContext('2d');
        
        if (this.charts.confidenceDist) {
            this.charts.confidenceDist.destroy();
        }

        // Create confidence bins
        const bins = {
            'Low (0-50%)': 0,
            'Medium (50-70%)': 0,
            'High (70-90%)': 0,
            'Very High (90-100%)': 0
        };

        this.transcripts.forEach(transcript => {
            const confidence = transcript.avgConfidence;
            if (confidence < 50) bins['Low (0-50%)']++;
            else if (confidence < 70) bins['Medium (50-70%)']++;
            else if (confidence < 90) bins['High (70-90%)']++;
            else bins['Very High (90-100%)']++;
        });

        this.charts.confidenceDist = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(bins),
                datasets: [{
                    data: Object.values(bins),
                    backgroundColor: [
                        '#ef4444', // Red for low
                        '#f59e0b', // Orange for medium  
                        '#22c55e', // Green for high
                        '#3b82f6'  // Blue for very high
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} files (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    updateCharts() {
        const filtered = this.getFilteredTranscripts();
        
        // Update engagement chart
        if (this.charts.engagement) {
            this.charts.engagement.data.labels = filtered.map(t => t.filename);
            this.charts.engagement.data.datasets[0].data = filtered.map(t => t.studentRatio);
            this.charts.engagement.update();
        }

        // Update scatter chart
        if (this.charts.scatter) {
            const scatterData = filtered.map(t => ({
                x: t.avgConfidence,
                y: t.studentRatio,
                label: t.filename
            }));
            this.charts.scatter.data.datasets[0].data = scatterData;
            this.charts.scatter.update();
        }
        
        // Update confidence distribution chart
        if (this.charts.confidenceDist) {
            const bins = {
                'Low (0-50%)': 0,
                'Medium (50-70%)': 0,
                'High (70-90%)': 0,
                'Very High (90-100%)': 0
            };

            filtered.forEach(transcript => {
                const confidence = transcript.avgConfidence;
                if (confidence < 50) bins['Low (0-50%)']++;
                else if (confidence < 70) bins['Medium (50-70%)']++;
                else if (confidence < 90) bins['High (70-90%)']++;
                else bins['Very High (90-100%)']++;
            });
            
            this.charts.confidenceDist.data.datasets[0].data = Object.values(bins);
            this.charts.confidenceDist.update();
        }
    }

    exportAnalysis() {
        const data = this.transcripts.map(t => ({
            filename: t.filename,
            student_ratio: t.studentRatio.toFixed(2),
            ai_words: t.aiWords,
            student_words: t.studentWords,
            total_words: t.totalWords,
            avg_confidence: t.avgConfidence.toFixed(2),
            segments: t.segments.length
        }));

        this.downloadCSV(data, 'transcript_analysis.csv');
    }

    downloadCSV(data, filename) {
        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    async loadDemoData() {
        // Load real transcript data for testing
        this.showLoading(true);
        
        try {
            // First try to load the real transcript file
            const response = await fetch('./demo/P01-G8-S4.txt');
            if (response.ok) {
                const realTranscriptContent = await response.text();
                const realTranscript = {
                    filename: 'P01-G8-S4.txt (Real Transcript)',
                    content: realTranscriptContent
                };
                
                // Process the real transcript
                this.transcripts = [];
                const analysis = this.analyzeTranscript(realTranscript.content, realTranscript.filename);
                this.transcripts.push(analysis);
                
                this.showDashboard();
                this.updateDashboard();
                this.renderFileList();
                this.createCharts();
                this.showLoading(false);
                return;
            }
        } catch (error) {
            console.log('Could not load real transcript, using synthetic data:', error);
        }
        
        // Fallback to enhanced demo data
        const demoData = [
            {
                filename: 'quantum-computing-tutorial.txt',
                content: `=== Page 00 ===
**STEP 1: LEARNING ASSESSMENT**

*Quantum Computing Instructor Introduction:*
"Greetings! I'm here to determine your optimal quantum learning pathway. I'll pose several focused questions to assess your mathematical background and learning preferences."

**First Question:**
"When exploring quantum mechanics, do you prefer abstract mathematical formulations or concrete physical analogies?"

A: abstract mathematical formulations

Excellent. You flourish with mathematical rigor, formal structures, and precise notation—no metaphors needed, just focused quantum mechanics. Let's commence.

### **STEP 3: QUANTUM EXPLORATION**

**Your Task:** Propose your own quantum advantage scenario where classical approaches fail.

A: A cryptographic system must factor a 2048-bit RSA modulus. The classical approach requires testing approximately 2^1024 potential factors—computationally infeasible even with modern supercomputers.

Exceptional selection. Your scenario demonstrates a fundamental constraint: **exponential classical complexity** versus **polynomial quantum advantage**.

**Why is the quantum state |ψ⟩ = (1/√N)Σ|x⟩ fundamentally unachievable classically?**

A: The quantum state represents a uniform superposition over N computational basis states simultaneously. Classically, this would require storing and manipulating N separate probability amplitudes, where N = 2^n for n qubits.

Perfect mathematical insight. You've identified the core limitation: **exponential classical storage requirements** versus **linear quantum register capacity**.`
            },
            {
                filename: 'mixed-conversation.txt',
                content: `AI: Welcome to today's session on machine learning fundamentals.

Student: What's the difference between supervised and unsupervised learning?

AI: Excellent question! Supervised learning uses labeled training data, where we know the correct answers. The algorithm learns to map inputs to outputs based on examples.

Unsupervised learning, on the other hand, works with unlabeled data to find hidden patterns or structures.

Student: Can you give me some examples?

AI: Sure! For supervised learning:
- Email spam detection (emails labeled as spam or not spam)
- Image classification (photos labeled with objects they contain)
- Stock price prediction (historical prices with known outcomes)

For unsupervised learning:
- Customer segmentation (grouping customers by behavior)
- Anomaly detection (finding unusual patterns)
- Topic modeling (discovering themes in text)

Student: That makes sense! What about reinforcement learning?

AI: Great follow-up question! Reinforcement learning is a third paradigm where an agent learns through trial and error by receiving rewards or penalties for its actions.

Think of it like training a dog - you give treats for good behavior and corrections for bad behavior. The agent learns to maximize its rewards over time.

Student: Like a game where you get points for good moves?

AI: Exactly! Video games are perfect examples. The AI learns to play by trying different strategies and getting feedback through scores or winning/losing.`
            },
            {
                filename: 'philosophy-debate.txt',
                content: `**Dr. Martinez:** Welcome to our exploration of consciousness studies. What are your thoughts on whether philosophical zombies are logically possible?

Student: I think philosophical zombies are conceptually incoherent. If consciousness arises from neural activity, then identical neural states must produce identical conscious experiences.

**Dr. Martinez:** Fascinating position! But consider this challenge: If consciousness is purely physical, why does subjective experience feel so different from objective neural processes?

Student: The "something it is like" might be an emergent property of complex information processing, similar to how wetness emerges from H2O molecules.

**Dr. Martinez:** An interesting emergence argument. But notice the asymmetry - we can fully explain wetness in terms of molecular behavior, yet the "hard problem" of consciousness resists such reduction.

Student: Perhaps the redness isn't a separate property but rather how the brain represents certain wavelengths. The subjective experience might be identical to the neural representation.

**Dr. Martinez:** You're approaching an identity theory position. This connects to current debates about AI consciousness. If a sufficiently complex artificial system exhibited all the functional properties we associate with consciousness, would you consider it genuinely conscious?

Student: Yes, I believe consciousness could be substrate-independent. What matters is the functional organization, not the specific material implementation.

**Dr. Martinez:** A bold conclusion! You've traversed from materialism through functionalism to computational consciousness.`
            }
        ];

        setTimeout(() => {
            this.transcripts = [];
            demoData.forEach(demo => {
                const analysis = this.analyzeTranscript(demo.content, demo.filename);
                this.transcripts.push(analysis);
            });

            this.showDashboard();
            this.updateDashboard();
            this.renderFileList();
            this.createCharts();
            this.showLoading(false);
        }, 1000);
    }

    showLoading(show) {
        document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
    }

    showProgress(show) {
        document.getElementById('upload-progress').style.display = show ? 'block' : 'none';
    }

    updateProgress(percent, text) {
        document.getElementById('progress-fill').style.width = `${percent}%`;
        document.getElementById('progress-text').textContent = text;
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new TranscriptAnalyzer();
});