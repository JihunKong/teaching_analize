# 구현 가이드 (Implementation Guide)

## 1. 개발 환경 설정

### 1.1 시스템 요구사항

**최소 사양**
- OS: Ubuntu 20.04+ / macOS 12+ / Windows 11
- CPU: 4코어 이상
- RAM: 16GB
- 저장공간: 100GB SSD
- GPU: NVIDIA GPU (CUDA 11.0+) 권장

**권장 사양**
- CPU: 8코어 이상
- RAM: 32GB
- GPU: NVIDIA RTX 3060 이상 (12GB VRAM)

### 1.2 Python 환경 설정

```bash
# Python 3.10 설치 확인
python --version  # Python 3.10+

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 기본 패키지 업그레이드
pip install --upgrade pip setuptools wheel
```

### 1.3 의존성 설치

**requirements.txt**
```txt
# 음성 인식 및 화자 분리
openai-whisper==20231117
whisperx==3.1.1
pyannote.audio==3.1.1
torch==2.1.0+cu118
torchaudio==2.1.0+cu118

# 음성 처리
ffmpeg-python==0.2.0
pydub==0.25.1

# 한국어 처리
kiwipiepy==0.17.0
konlpy==0.6.0
py-hanspell==1.1

# 웹 프레임워크
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# 데이터베이스
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1

# AI API
anthropic==0.7.0

# 데이터 처리
pandas==2.1.3
numpy==1.26.2
scipy==1.11.4

# 차트 생성
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.18.0

# PDF 생성
reportlab==4.0.7
weasyprint==60.1

# 유틸리티
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

**설치 명령**
```bash
pip install -r requirements.txt

# FFmpeg 설치 (시스템 레벨)
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows: https://ffmpeg.org/download.html 에서 다운로드
```

### 1.4 환경 변수 설정

**.env.example**
```bash
# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/tvas_db

# AI API
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# HuggingFace (Pyannote 사용)
HF_AUTH_TOKEN=hf_your-token-here

# JWT 인증
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 파일 스토리지
STORAGE_PATH=/path/to/storage
MAX_VIDEO_SIZE_MB=5000

# 처리 설정
GPU_ENABLED=true
MAX_CONCURRENT_JOBS=5
AUTO_DELETE_VIDEO_DAYS=30
```

---

## 2. 프로젝트 구조

```
tvas/
├── README.md
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
│
├── main.py                    # FastAPI 애플리케이션 진입점
├── config.py                  # 설정 관리
│
├── src/
│   ├── __init__.py
│   │
│   ├── api/                   # API 엔드포인트
│   │   ├── __init__.py
│   │   ├── videos.py
│   │   ├── reports.py
│   │   └── auth.py
│   │
│   ├── core/                  # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── transcription.py  # Module 1
│   │   ├── analysis.py        # Module 2
│   │   ├── evaluation.py      # Module 3
│   │   ├── coaching.py        # Module 4 (일부)
│   │   └── reporting.py       # Module 4 (일부)
│   │
│   ├── models/                # 데이터 모델
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── transcript.py
│   │   ├── analysis.py
│   │   ├── evaluation.py
│   │   └── report.py
│   │
│   ├── schemas/               # Pydantic 스키마
│   │   ├── __init__.py
│   │   ├── transcript.py
│   │   ├── analysis.py
│   │   └── report.py
│   │
│   ├── services/              # 외부 서비스 통합
│   │   ├── __init__.py
│   │   ├── whisper_service.py
│   │   ├── claude_service.py
│   │   └── storage_service.py
│   │
│   └── utils/                 # 유틸리티 함수
│       ├── __init__.py
│       ├── audio.py
│       ├── text.py
│       ├── validation.py
│       └── checklist.py
│
├── tests/                     # 테스트
│   ├── __init__.py
│   ├── test_transcription.py
│   ├── test_analysis.py
│   ├── test_evaluation.py
│   └── test_integration.py
│
├── scripts/                   # 유틸리티 스크립트
│   ├── init_db.py
│   ├── migrate_db.py
│   └── benchmark.py
│
├── data/                      # 샘플 데이터
│   ├── sample_videos/
│   ├── test_cases/
│   └── ideal_patterns/
│
└── docs/                      # 문서
    ├── API.md
    ├── DEPLOYMENT.md
    └── TROUBLESHOOTING.md
```

---

## 3. 핵심 모듈 구현

### 3.1 Module 1: 전사 및 화자 분리

**src/core/transcription.py**
```python
import whisperx
import torch
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class TranscriptionService:
    def __init__(self, device: str = "cuda", model_size: str = "large-v3"):
        self.device = device
        self.model_size = model_size
        self.model = None
        self.diarize_model = None
    
    def load_models(self):
        """모델 로드"""
        logger.info(f"Loading Whisper model: {self.model_size}")
        self.model = whisperx.load_model(
            self.model_size, 
            self.device, 
            language="ko"
        )
        
        logger.info("Loading diarization model")
        self.diarize_model = whisperx.DiarizationPipeline(
            use_auth_token=os.getenv("HF_AUTH_TOKEN"),
            device=self.device
        )
    
    def process_video(self, video_path: str) -> Dict:
        """영상 처리 전체 파이프라인"""
        logger.info(f"Processing video: {video_path}")
        
        # 1. 오디오 추출
        audio_path = self._extract_audio(video_path)
        
        # 2. 전사
        audio = whisperx.load_audio(audio_path)
        result = self.model.transcribe(audio)
        
        # 3. 정렬 (타임스탬프 정확도 향상)
        align_model, metadata = whisperx.load_align_model(
            language_code="ko",
            device=self.device
        )
        result = whisperx.align(
            result["segments"],
            align_model,
            metadata,
            audio
        )
        
        # 4. 화자 분리
        diarize_segments = self.diarize_model(audio)
        result = whisperx.assign_word_speakers(diarize_segments, result)
        
        # 5. 교사 화자 식별
        teacher_speaker, speaker_stats = self._identify_teacher(result)
        
        # 6. 교사 발화 추출
        teacher_utterances = self._extract_teacher_utterances(
            result, 
            teacher_speaker
        )
        
        # 7. 텍스트 정제
        teacher_utterances = self._preprocess_text(teacher_utterances)
        
        # 8. 품질 검증
        validation_result = self._validate_quality(
            teacher_utterances,
            result,
            speaker_stats
        )
        
        return {
            "teacher_utterances": teacher_utterances,
            "teacher_speaker_id": teacher_speaker,
            "speaker_stats": speaker_stats,
            "quality_metrics": validation_result,
            "all_segments": result
        }
    
    def _identify_teacher(self, segments: List[Dict]) -> tuple:
        """교사 화자 식별"""
        speaker_stats = {}
        
        for seg in segments:
            if 'speaker' not in seg:
                continue
                
            spk = seg['speaker']
            duration = seg['end'] - seg['start']
            
            if spk not in speaker_stats:
                speaker_stats[spk] = {
                    'total_duration': 0,
                    'total_words': 0,
                    'count': 0
                }
            
            speaker_stats[spk]['total_duration'] += duration
            speaker_stats[spk]['total_words'] += len(seg['text'].split())
            speaker_stats[spk]['count'] += 1
        
        # 가장 많이 말한 화자 = 교사
        teacher = max(
            speaker_stats.items(),
            key=lambda x: x[1]['total_duration']
        )[0]
        
        return teacher, speaker_stats
    
    def _extract_teacher_utterances(
        self, 
        segments: List[Dict], 
        teacher_speaker: str
    ) -> List[Dict]:
        """교사 발화만 추출"""
        utterances = []
        utterance_id = 1
        
        for seg in segments:
            if seg.get('speaker') == teacher_speaker:
                utterances.append({
                    'id': utterance_id,
                    'start': seg['start'],
                    'end': seg['end'],
                    'duration': seg['end'] - seg['start'],
                    'text': seg['text'],
                    'word_count': len(seg['text'].split()),
                    'confidence': seg.get('confidence', 1.0),
                    'words': seg.get('words', [])
                })
                utterance_id += 1
        
        return utterances
    
    def _preprocess_text(self, utterances: List[Dict]) -> List[Dict]:
        """텍스트 정제"""
        from src.utils.text import remove_fillers, normalize_spacing
        
        for utt in utterances:
            original = utt['text']
            
            # 간투사 제거
            cleaned = remove_fillers(original)
            
            # 띄어쓰기 정규화
            cleaned = normalize_spacing(cleaned)
            
            utt['text'] = cleaned
            utt['preprocessing'] = {
                'original_text': original
            }
        
        return utterances
    
    def _validate_quality(
        self, 
        teacher_utterances: List[Dict],
        all_segments: List[Dict],
        speaker_stats: Dict
    ) -> Dict:
        """품질 검증"""
        teacher_ratio = len(teacher_utterances) / len(all_segments)
        avg_confidence = sum(u['confidence'] for u in teacher_utterances) / len(teacher_utterances)
        
        warnings = []
        
        if teacher_ratio < 0.6 or teacher_ratio > 0.9:
            warnings.append(f"교사 발화 비율이 {teacher_ratio:.1%}로 비정상적입니다")
        
        if avg_confidence < 0.8:
            warnings.append(f"평균 신뢰도가 {avg_confidence:.2f}로 낮습니다")
        
        return {
            'total_segments': len(all_segments),
            'teacher_segments': len(teacher_utterances),
            'teacher_ratio': teacher_ratio,
            'avg_confidence': avg_confidence,
            'validation_passed': len(warnings) == 0,
            'warnings': warnings
        }
```

### 3.2 Module 2: 3차원 매트릭스 분석

**src/core/analysis.py**
```python
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self):
        self.checklists = self._load_checklists()
    
    def analyze(self, utterances: List[Dict]) -> Dict:
        """3차원 분석 수행"""
        logger.info(f"Analyzing {len(utterances)} utterances")
        
        # 1. 수업 단계 분류
        utterances_with_stage = self._classify_stages(utterances)
        
        # 2. 맥락 태깅
        utterances_with_context = self._tag_context(utterances_with_stage)
        
        # 3. 수준 분류
        utterances_analyzed = self._classify_levels(utterances_with_context)
        
        # 4. 3D 매트릭스 생성
        matrix_3d = self._build_matrix(utterances_analyzed)
        
        # 5. 검증
        validation = self._validate_analysis(matrix_3d, utterances_analyzed)
        
        return {
            'utterances_analyzed': utterances_analyzed,
            'matrix_3d': matrix_3d,
            'validation_results': validation
        }
    
    def _classify_stages(self, utterances: List[Dict]) -> List[Dict]:
        """수업 단계 분류"""
        from src.utils.checklist import check_stage_signals
        
        total_duration = utterances[-1]['end']
        
        for utt in utterances:
            # 체크리스트 실행 (3회 다수결)
            signals = self._run_checklist_with_vote(
                utt['text'],
                self.checklists['stage']
            )
            
            # 단계 결정
            stage = self._determine_stage(
                signals,
                utt['start'],
                total_duration
            )
            
            utt['stage'] = {
                'label': stage,
                'signals': signals,
                'confidence': self._calculate_confidence(signals)
            }
        
        return utterances
    
    def _tag_context(self, utterances: List[Dict]) -> List[Dict]:
        """교수학적 맥락 태깅"""
        for utt in utterances:
            context_results = {}
            
            # 5가지 맥락 타입 각각 체크
            for context_type in ['explain', 'question', 'feedback', 'facilitate', 'manage']:
                checklist = self.checklists[context_type]
                results = self._run_checklist_with_vote(
                    utt['text'],
                    checklist
                )
                context_results[context_type] = results
            
            # 주 맥락 결정 (다중 태그 가능)
            primary_contexts = self._determine_primary_contexts(context_results)
            
            utt['context'] = {
                'primary': primary_contexts[0] if primary_contexts else 'manage',
                'secondary': primary_contexts[1:] if len(primary_contexts) > 1 else [],
                'checklist_results': context_results,
                'confidence': self._calculate_confidence(context_results)
            }
        
        return utterances
    
    def _classify_levels(self, utterances: List[Dict]) -> List[Dict]:
        """인지/상호작용 수준 분류"""
        for utt in utterances:
            # 인지 수준
            cognitive_results = {}
            for level in ['level_1', 'level_2', 'level_3']:
                checklist = self.checklists[f'cognitive_{level}']
                results = self._run_checklist_with_vote(
                    utt['text'],
                    checklist
                )
                cognitive_results[level] = results
            
            cognitive_level = self._determine_cognitive_level(cognitive_results)
            
            # 상호작용 패턴
            interaction_results = {}
            for pattern in ['teacher_led', 'simple_IRF', 'extended_dialogue']:
                checklist = self.checklists[f'interaction_{pattern}']
                results = self._run_checklist_with_vote(
                    utt['text'],
                    checklist
                )
                interaction_results[pattern] = results
            
            interaction_type = self._determine_interaction(interaction_results)
            
            utt['cognitive_level'] = {
                'level': cognitive_level,
                'checklist_results': cognitive_results,
                'confidence': self._calculate_confidence(cognitive_results)
            }
            
            utt['interaction_pattern'] = {
                'type': interaction_type,
                'checklist_results': interaction_results,
                'confidence': self._calculate_confidence(interaction_results)
            }
        
        return utterances
    
    def _run_checklist_with_vote(
        self, 
        text: str, 
        checklist: Dict
    ) -> Dict:
        """체크리스트를 3회 실행하고 다수결"""
        from src.services.claude_service import ClaudeService
        
        claude = ClaudeService()
        results = []
        
        # 3회 실행
        for _ in range(3):
            result = claude.run_checklist(text, checklist)
            results.append(result)
        
        # 다수결
        final_result = {}
        for key in checklist.keys():
            votes = [r[key] for r in results]
            final_result[key] = sum(votes) >= 2  # 2/3 이상
        
        return final_result
    
    def _build_matrix(self, utterances: List[Dict]) -> Dict:
        """3D 매트릭스 생성"""
        matrix = {
            'introduction': self._init_stage_matrix(),
            'development': self._init_stage_matrix(),
            'closing': self._init_stage_matrix()
        }
        
        for utt in utterances:
            stage = utt['stage']['label']
            context = utt['context']['primary']
            level = utt['cognitive_level']['level']
            
            matrix[stage][context][f'L{level}'] += 1
        
        return matrix
    
    def _init_stage_matrix(self) -> Dict:
        """단계별 빈 매트릭스 초기화"""
        return {
            'explain': {'L1': 0, 'L2': 0, 'L3': 0},
            'question': {'L1': 0, 'L2': 0, 'L3': 0},
            'feedback': {'L1': 0, 'L2': 0, 'L3': 0},
            'facilitate': {'L1': 0, 'L2': 0, 'L3': 0},
            'manage': {'L1': 0, 'L2': 0, 'L3': 0}
        }
```

### 3.3 Module 3: 평가 (규칙 엔진)

**src/core/evaluation.py**
```python
from typing import Dict
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EvaluationService:
    def __init__(self):
        self.optimal_ranges = self._load_optimal_ranges()
    
    def evaluate(self, matrix: Dict, utterances: List[Dict]) -> Dict:
        """정량 평가 수행 (완전 결정론적)"""
        logger.info("Calculating quantitative metrics")
        
        metrics = {}
        
        # 1. 시간 배분 지표
        metrics['time_distribution'] = self._calc_time_metrics(utterances)
        
        # 2. 맥락 분포 지표
        metrics['context_distribution'] = self._calc_context_metrics(matrix, utterances)
        
        # 3. 인지 복잡도 지표
        metrics['cognitive_complexity'] = self._calc_cognitive_metrics(matrix, utterances)
        
        # 4. 상호작용 지표
        metrics['interaction_quality'] = self._calc_interaction_metrics(utterances)
        
        # 5. 복합 패턴 지표
        metrics['composite_patterns'] = self._calc_composite_metrics(matrix, utterances)
        
        # 6. 전체 점수 계산
        overall_score = self._calc_overall_score(metrics)
        
        # 7. 강점/개선점 식별
        strengths, improvements = self._identify_strengths_improvements(metrics)
        
        return {
            'metrics': metrics,
            'overall_score': overall_score,
            'strengths': strengths,
            'improvements': improvements
        }
    
    def _calc_time_metrics(self, utterances: List[Dict]) -> Dict:
        """시간 배분 지표"""
        total_duration = utterances[-1]['end']
        
        stage_durations = {
            'introduction': 0,
            'development': 0,
            'closing': 0
        }
        
        for utt in utterances:
            stage = utt['stage']['label']
            stage_durations[stage] += utt['duration']
        
        metrics = {}
        for stage, duration in stage_durations.items():
            ratio = duration / total_duration
            score = self._normalize_score(
                ratio,
                self.optimal_ranges[f'{stage}_ratio']
            )
            metrics[f'{stage}_ratio'] = {
                'value': ratio,
                'score': score
            }
        
        # 발화 밀도
        utterance_density = len(utterances) / (total_duration / 60)
        metrics['utterance_density'] = {
            'value': utterance_density,
            'score': self._normalize_score(
                utterance_density,
                self.optimal_ranges['utterance_density']
            )
        }
        
        return metrics
    
    def _normalize_score(
        self, 
        value: float, 
        optimal_range: tuple
    ) -> float:
        """0-100 점수로 정규화"""
        lower, upper = optimal_range
        
        if lower <= value <= upper:
            # 최적 범위 내: 80-100점
            return 80 + 20 * ((value - lower) / (upper - lower))
        elif value < lower:
            # 최적 범위 미만
            return 80 * (value / lower)
        else:
            # 최적 범위 초과
            return 80 * (1 - (value - upper) / (1 - upper))
```

---

## 4. 배포

### 4.1 Docker 배포

**Dockerfile**
```dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Python 설치
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./storage:/app/storage
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tvas
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - HF_AUTH_TOKEN=${HF_AUTH_TOKEN}
    depends_on:
      - db
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=tvas
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### 4.2 실행

```bash
# 빌드 및 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

---

## 5. 테스트

```bash
# 전체 테스트
pytest

# 커버리지
pytest --cov=src --cov-report=html

# 특정 모듈 테스트
pytest tests/test_transcription.py -v
```

---

## 6. 모니터링

```python
# src/utils/monitoring.py
import logging
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        
        logging.info(f"{func.__name__} took {duration:.2f}s")
        return result
    
    return wrapper
```

---

이상으로 핵심 구현 가이드를 작성했습니다. 실제 구현 시 점진적으로 개발하시면 됩니다!
