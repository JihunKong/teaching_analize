# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TVAS (Teacher Voice Analysis System) is an AI-powered tool that analyzes classroom instruction by automatically extracting and analyzing teacher utterances from lesson videos. The system provides objective, consistent, research-grade diagnostics similar to a medical body composition analysis.

**Core Purpose**: Extract teacher speech from videos, analyze it across 3 dimensions (time × context × cognitive level), and generate coaching feedback with guaranteed consistency for research validity.

## System Architecture

The system operates as a 4-module pipeline:

1. **Module 1: Transcription & Diarization** (`src/transcription/`)
   - Uses WhisperX for speech recognition and speaker separation
   - Automatically identifies teacher vs. student speakers (60-90% teacher ratio validation)
   - Outputs: Teacher utterance timeline with word-level timestamps

2. **Module 2: 3D Matrix Analysis** (`src/analysis/`)
   - Classifies utterances across 3 dimensions:
     - Time axis: Introduction/Development/Closing (수업단계)
     - Context axis: Explain/Question/Feedback/Facilitate/Manage (교수기능)
     - Level axis: L1/L2/L3 cognitive levels (Bloom's Taxonomy)
   - **Critical**: All classification uses binary checklists with 3-run majority voting for consistency

3. **Module 3: Evaluation** (`src/evaluation/` and `src/coaching/`)
   - Rule-based engine calculates 15 quantitative metrics (fully deterministic)
   - AI generates coaching feedback based on metrics (NOT evaluation itself)
   - Outputs: Scores + personalized coaching

4. **Module 4: Report Generation** (`src/reporting/`)
   - Creates "InBody-style" diagnostic reports with radar charts, heatmaps, timelines
   - Multiple formats: PDF (print), HTML (web), CSV (research), JSON (raw)

## Critical Design Principles

### Consistency Guarantees
The system MUST produce identical results for identical inputs (research requirement):

1. **AI for Observation Only**: AI tags utterances using binary checklists, but never evaluates quality
2. **Rules for Evaluation**: All scoring uses deterministic formulas (no AI judgment)
3. **Majority Voting**: Run each checklist 3 times, accept if ≥2/3 agree
4. **Temperature=0**: All AI calls use temperature 0 for minimal variance
5. **Validation Rules**: Detect abnormal patterns (e.g., development phase <50% = warning)

### Data Flow Pattern
```
Video → Audio Extraction → Transcription → Diarization → Teacher Identification
  → Text Preprocessing → Stage Classification → Context Tagging → Level Classification
  → 3D Matrix Building → Metric Calculation → Coaching Generation → Report Output
```

Each module's output is the next module's input. Intermediate results stored as JSON.

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (system-level)
# Ubuntu: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg

# Set up environment variables
cp .env.example .env
# Edit .env with API keys: ANTHROPIC_API_KEY, HF_AUTH_TOKEN, DATABASE_URL
```

### Database Operations
```bash
# Initialize database (PostgreSQL)
python scripts/init_db.py

# Run migrations
python scripts/migrate_db.py
```

### Running the System
```bash
# Development server
python main.py
# OR
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Docker deployment
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Testing
```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=html

# Test specific module
pytest tests/test_transcription.py -v
pytest tests/test_analysis.py -v
pytest tests/test_evaluation.py -v

# Integration test
pytest tests/test_integration.py -v
```

### Performance Benchmarking
```bash
# Benchmark processing speed
python scripts/benchmark.py --video data/sample_videos/lesson_45min.mp4
```

## Key Implementation Details

### Checklist-Based Classification (Module 2)

All utterance tagging uses binary checklists defined in YAML/dict format:

```python
# Example: Stage classification checklist
introduction_signals = {
    "학습목표_언급": bool,
    "시작표현_사용": bool,  # "오늘은", "이번 시간"
    "동기유발_질문": bool,
    "전시학습_상기": bool,
    "수업계획_안내": bool
}
```

**Pattern**: For each utterance, run checklist 3 times via Claude API, take majority vote on each item. If ≥2 introduction signals detected AND time < 30% of total, classify as "introduction".

### Metric Calculation (Module 3)

15 metrics calculated using pure math (no AI):
- Time distribution: `stage_duration / total_duration`
- Context entropy: Shannon entropy `H = -Σ(pi * log2(pi))`
- Cognitive complexity: Weighted average `(L1×1 + L2×2 + L3×3) / total`
- Pattern alignment: Cosine similarity with ideal patterns

**Normalization**: All metrics converted to 0-100 scale based on optimal ranges:
```python
if value in optimal_range:
    score = 80 + 20 * normalized_position  # 80-100
elif value < optimal_range[0]:
    score = 80 * (value / optimal_range[0])  # 0-80
else:
    score = 80 * (1 - excess_ratio)  # 80-0
```

### AI Coaching Generation

AI receives pre-calculated metrics and generates coaching using structured prompts:

```python
prompt = f"""
[System] You are a teaching consultant with 20 years experience.
[Rubric] Strengths = top 20% metrics, Improvements = bottom 20%
[Data] {json.dumps(metrics)}
[Template] {{
  "overall_assessment": "200 chars max",
  "strengths": [3 items with examples],
  "improvements": [3 items with actionable suggestions]
}}
"""
```

**Retry Logic**: If output fails JSON schema validation, retry up to 3 times with error message appended.

### Quality Validation

Automatic checks at each stage:
- **Transcription**: Teacher ratio 60-90%, avg confidence >0.8
- **Analysis**: Development phase 50-80%, no single context >70%
- **Evaluation**: All scores in 0-100 range

Warnings logged but processing continues unless critical error.

## File Structure Context

```
src/
├── api/           # FastAPI endpoints (videos.py, reports.py, auth.py)
├── core/          # 4 main processing modules
│   ├── transcription.py  # Module 1: WhisperX integration
│   ├── analysis.py       # Module 2: 3D classification
│   ├── evaluation.py     # Module 3: Metric calculation
│   └── coaching.py       # Module 3-4: AI feedback generation
├── models/        # SQLAlchemy ORM models (database.py, transcript.py, etc.)
├── schemas/       # Pydantic validation schemas
├── services/      # External service wrappers
│   ├── whisper_service.py   # WhisperX API wrapper
│   ├── claude_service.py    # Anthropic Claude API
│   └── storage_service.py   # File storage operations
└── utils/         # Helper functions
    ├── audio.py         # FFmpeg audio extraction
    ├── text.py          # Korean text preprocessing
    ├── validation.py    # Quality checks
    └── checklist.py     # Checklist execution logic
```

## Database Schema

PostgreSQL with JSONB for flexibility:
- `users`: Teacher accounts
- `videos`: Uploaded lesson videos + metadata
- `transcripts`: Module 1 output (JSONB: full TeacherUtteranceTimeline)
- `analyses`: Module 2 output (JSONB: 3D matrix + tagged utterances)
- `evaluations`: Module 3 output (JSONB: 15 metrics + scores)
- `coaching_feedbacks`: AI-generated coaching (JSONB)
- `reports`: Final report links + metadata

**Index Strategy**: GIN indexes on all JSONB columns for fast querying. B-tree indexes on video_id, user_id, overall_score.

## Technology Stack Specifics

- **Python 3.10+**: Required for match-case statements and type hints
- **FastAPI**: Async web framework, use `@app.post("/api/v1/...")` pattern
- **WhisperX 3.1.1**: Includes Whisper large-v3 + Pyannote 3.1 for diarization
- **PyTorch 2.1.0**: CUDA 11.8 build for GPU acceleration
- **PostgreSQL 15**: JSON support, use SQLAlchemy ORM
- **Anthropic Claude**: Use claude-sonnet-4 model, temperature=0 for consistency
- **FFmpeg**: System-level install required for audio extraction

## Common Patterns

### Adding a New Checklist

1. Define checklist in `src/utils/checklist.py`:
```python
NEW_CHECKLIST = {
    "criterion_1": "Description of what to check",
    "criterion_2": "...",
}
```

2. Add to `AnalysisService._load_checklists()` in `src/core/analysis.py`

3. Use with majority voting:
```python
results = self._run_checklist_with_vote(utterance_text, NEW_CHECKLIST)
```

### Adding a New Metric

1. Calculate in `EvaluationService` (`src/core/evaluation.py`):
```python
def _calc_new_metric(self, matrix, utterances):
    value = # your calculation
    score = self._normalize_score(value, optimal_range)
    return {'value': value, 'score': score}
```

2. Add optimal range to `self.optimal_ranges`

3. Include in `evaluate()` output

### Processing a Video End-to-End

```python
# In main processing pipeline
transcription_service = TranscriptionService()
analysis_service = AnalysisService()
evaluation_service = EvaluationService()
coaching_service = CoachingService()
reporting_service = ReportingService()

# Module 1
transcript_result = transcription_service.process_video(video_path)

# Module 2
analysis_result = analysis_service.analyze(transcript_result['teacher_utterances'])

# Module 3
evaluation_result = evaluation_service.evaluate(
    analysis_result['matrix_3d'],
    analysis_result['utterances_analyzed']
)
coaching_result = coaching_service.generate_coaching(
    evaluation_result,
    analysis_result['utterances_analyzed']
)

# Module 4
report = reporting_service.create_report(
    transcript_result,
    analysis_result,
    evaluation_result,
    coaching_result
)
```

## Research Validity Requirements

This system is designed for academic research, requiring:

1. **Reproducibility**: Same video → same results (95%+ consistency)
2. **Inter-rater Reliability**: Cohen's Kappa >0.8 vs. manual coding
3. **Transparency**: All intermediate data saved for audit
4. **Validation**: Expert comparison on sample videos

When modifying code, preserve these guarantees:
- Never introduce randomness without majority voting
- Always log processing metadata (model versions, timestamps)
- Store complete intermediate results, not just final outputs
- Run consistency tests on sample videos after changes

## Performance Targets

- 45-minute video processing: 15-20 minutes (with GPU)
- Transcription accuracy: 95%+ (Korean)
- Speaker diarization DER: <5%
- Teacher identification: 95%+ accuracy
- Concurrent videos: Up to 5 (configure MAX_CONCURRENT_JOBS)

## Special Considerations

### Korean Language Processing
- Uses KoNLPy for morphological analysis
- Filler removal: "어", "음", "그", "저" (defined in utils/text.py)
- Spacing normalization for Whisper output irregularities

### GPU Memory Management
- WhisperX large-v3 requires ~10GB VRAM
- Use `torch.cuda.empty_cache()` between videos
- Configure batch_size in transcription service based on available VRAM

### Error Recovery
- Video processing can be resumed from last successful module
- Check `videos.processing_status` in database
- Intermediate results cached in `storage/cache/{video_id}/`

## Related Documentation

For deeper details, see:
- **ARCHITECTURE.md**: Full system design and module interactions
- **SPECIFICATION.md**: Functional requirements and acceptance criteria
- **DATA_STRUCTURE.md**: Complete JSON schemas and database structure
- **IMPLEMENTATION.md**: Detailed code examples and deployment
- **RESEARCH_GUIDE.md**: Academic usage guidelines

## Citation

When using this system for research, cite as:
```
Kim, J. (2025). Teacher Voice Analysis System (TVAS):
An AI-Powered Tool for Objective Classroom Discourse Analysis.
[Software]. Available at: https://github.com/your-repo/tvas
```
