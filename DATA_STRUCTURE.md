# 데이터 구조 정의 (Data Structure Specification)

## 1. 전체 데이터 흐름

```
Video File → Transcript Data → Analysis Data → Evaluation Data → Report Data
```

---

## 2. 상세 데이터 스키마

### 2.1 Transcript Data (전사 데이터)

#### TeacherUtteranceTimeline
```json
{
  "video_id": "string (UUID)",
  "metadata": {
    "video_file": "string (파일명)",
    "teacher_name": "string",
    "grade": "string",
    "subject": "string", 
    "topic": "string",
    "date": "string (ISO 8601: YYYY-MM-DD)",
    "duration": "float (초)",
    "processing_date": "string (ISO 8601)"
  },
  
  "processing_info": {
    "whisper_model": "string (예: large-v3)",
    "diarization_model": "string (예: pyannote/3.1)",
    "processing_time": "float (초)"
  },
  
  "quality_metrics": {
    "total_segments": "integer",
    "teacher_segments": "integer",
    "student_segments": "integer",
    "teacher_ratio": "float (0-1)",
    "avg_confidence": "float (0-1)",
    "low_confidence_count": "integer (<0.7)",
    "validation_passed": "boolean"
  },
  
  "speaker_stats": {
    "SPEAKER_00": {
      "total_duration": "float (초)",
      "total_words": "integer",
      "utterance_count": "integer",
      "avg_utterance_length": "float (단어)"
    },
    "SPEAKER_01": { ... }
  },
  
  "teacher_speaker_id": "string (예: SPEAKER_00)",
  
  "teacher_utterances": [
    {
      "id": "integer",
      "start": "float (초)",
      "end": "float (초)",
      "duration": "float (초)",
      "text": "string",
      "word_count": "integer",
      "confidence": "float (0-1)",
      "original_speaker_id": "string",
      
      "words": [
        {
          "word": "string",
          "start": "float",
          "end": "float",
          "confidence": "float"
        }
      ],
      
      "preprocessing": {
        "original_text": "string (정제 전)",
        "removed_fillers": ["string"],
        "corrections": [
          {
            "type": "string (예: spacing, typo)",
            "original": "string",
            "corrected": "string"
          }
        ]
      }
    }
  ],
  
  "excluded_utterances": [
    {
      "id": "integer",
      "text": "string",
      "speaker": "string (student, noise, etc)",
      "confidence": "float",
      "reason": "string (제외 사유)"
    }
  ]
}
```

---

### 2.2 Analysis Data (분석 데이터)

#### ThreeDimensionalMatrix
```json
{
  "video_id": "string (UUID)",
  "analysis_timestamp": "string (ISO 8601)",
  
  "stage_boundaries": {
    "introduction": {
      "start": "float (초)",
      "end": "float (초)",
      "duration": "float (초)",
      "utterance_ids": ["integer"]
    },
    "development": { ... },
    "closing": { ... }
  },
  
  "matrix_3d": {
    "introduction": {
      "explain": {
        "L1": "integer (빈도)",
        "L2": "integer",
        "L3": "integer"
      },
      "question": { "L1": "integer", "L2": "integer", "L3": "integer" },
      "feedback": { "L1": "integer", "L2": "integer", "L3": "integer" },
      "facilitate": { "L1": "integer", "L2": "integer", "L3": "integer" },
      "manage": { "L1": "integer", "L2": "integer", "L3": "integer" }
    },
    "development": { ... },
    "closing": { ... }
  },
  
  "utterances_analyzed": [
    {
      "utterance_id": "integer",
      "text": "string",
      "start": "float",
      "end": "float",
      
      "stage": {
        "label": "string (introduction/development/closing)",
        "confidence": "float (0-1)",
        "signals": {
          "introduction_signals": ["string"],
          "development_signals": ["string"],
          "closing_signals": ["string"]
        },
        "signal_count": {
          "introduction": "integer",
          "development": "integer",
          "closing": "integer"
        }
      },
      
      "context": {
        "primary": "string (explain/question/feedback/facilitate/manage)",
        "secondary": ["string"] (다중 태그 가능),
        "confidence": "float (0-1)",
        "checklist_results": {
          "explain": {
            "개념_정의": "boolean",
            "예시_제시": "boolean",
            "절차_설명": "boolean",
            "인과_설명": "boolean"
          },
          "question": { ... },
          "feedback": { ... },
          "facilitate": { ... },
          "manage": { ... }
        }
      },
      
      "cognitive_level": {
        "level": "integer (1/2/3)",
        "confidence": "float (0-1)",
        "checklist_results": {
          "level_1": {
            "단순사실_확인": "boolean",
            "정의개념_반복": "boolean",
            "교과서_내용_그대로": "boolean"
          },
          "level_2": { ... },
          "level_3": { ... }
        }
      },
      
      "interaction_pattern": {
        "type": "string (teacher_led/simple_IRF/extended_dialogue)",
        "confidence": "float (0-1)",
        "checklist_results": {
          "teacher_led": { ... },
          "simple_IRF": { ... },
          "extended_dialogue": { ... }
        }
      }
    }
  ],
  
  "validation_results": {
    "stage_distribution_normal": "boolean",
    "context_distribution_normal": "boolean",
    "cognitive_level_distribution_normal": "boolean",
    "warnings": ["string"],
    "errors": ["string"]
  }
}
```

---

### 2.3 Evaluation Data (평가 데이터)

#### QuantitativeMetrics
```json
{
  "video_id": "string (UUID)",
  "evaluation_timestamp": "string (ISO 8601)",
  
  "metrics": {
    "time_distribution": {
      "introduction_ratio": {
        "value": "float (0-1)",
        "score": "float (0-100)",
        "percentile": "float (0-100)",
        "optimal_range": [0.1, 0.2]
      },
      "development_ratio": { ... },
      "closing_ratio": { ... },
      "utterance_density": {
        "value": "float (개/분)",
        "score": "float",
        "percentile": "float",
        "optimal_range": [2.0, 4.0]
      }
    },
    
    "context_distribution": {
      "question_ratio": {
        "value": "float (0-1)",
        "score": "float (0-100)",
        "percentile": "float",
        "optimal_range": [0.3, 0.5]
      },
      "explain_ratio": { ... },
      "feedback_ratio": { ... },
      "context_entropy": {
        "value": "float (0-2.32)",
        "score": "float",
        "percentile": "float",
        "optimal_range": [1.5, 2.0]
      }
    },
    
    "cognitive_complexity": {
      "avg_cognitive_level": {
        "value": "float (1-3)",
        "score": "float",
        "percentile": "float",
        "optimal_range": [1.8, 2.3]
      },
      "higher_order_ratio": {
        "value": "float (0-1)",
        "score": "float",
        "percentile": "float",
        "optimal_range": [0.4, 0.6]
      },
      "cognitive_progression": {
        "intro_to_dev": "float",
        "dev_to_close": "float",
        "score": "float",
        "percentile": "float"
      }
    },
    
    "interaction_quality": {
      "extended_dialogue_ratio": {
        "value": "float (0-1)",
        "score": "float",
        "percentile": "float",
        "optimal_range": [0.4, 0.7]
      },
      "avg_wait_time": {
        "value": "float (초)",
        "score": "float",
        "percentile": "float",
        "optimal_range": [3.0, 5.0]
      },
      "simple_IRF_ratio": { ... }
    },
    
    "composite_patterns": {
      "dev_question_depth": {
        "value": "float (0-1)",
        "score": "float",
        "percentile": "float",
        "description": "전개 단계의 고차원 질문 비율"
      },
      "feedback_specificity": { ... },
      "pattern_alignment": {
        "best_match": "string (패턴명)",
        "similarity": "float (0-1)",
        "score": "float",
        "percentile": "float"
      }
    }
  },
  
  "overall_score": {
    "total": "float (0-100)",
    "percentile": "float (0-100)",
    "grade": "string (A+/A/B+/B/C+/C/D/F)"
  },
  
  "strengths": [
    {
      "metric_name": "string",
      "score": "float",
      "percentile": "float",
      "rank": "integer"
    }
  ],
  
  "improvements": [
    {
      "metric_name": "string",
      "score": "float",
      "percentile": "float",
      "rank": "integer"
    }
  ]
}
```

---

### 2.4 Coaching Data (코칭 데이터)

#### AICoachingFeedback
```json
{
  "video_id": "string (UUID)",
  "coaching_timestamp": "string (ISO 8601)",
  "model_used": "string (예: claude-sonnet-4-20250514)",
  
  "overall_assessment": "string (200자 이내)",
  
  "strengths": [
    {
      "area": "string",
      "metric_name": "string",
      "score": "float",
      "description": "string (100자 이내)",
      "example": {
        "utterance_id": "integer",
        "text": "string",
        "timestamp": "string (MM:SS)"
      }
    }
  ],
  
  "improvements": [
    {
      "area": "string",
      "metric_name": "string",
      "score": "float",
      "description": "string (100자 이내)",
      "example": {
        "utterance_id": "integer",
        "text": "string",
        "timestamp": "string (MM:SS)"
      },
      "suggestion": {
        "what": "string (무엇을)",
        "how": "string (어떻게)",
        "why": "string (왜)"
      }
    }
  ],
  
  "next_steps": [
    {
      "goal": "string",
      "action": "string",
      "measurable": "string (측정 가능한 기준)",
      "timeline": "string (예: 다음 수업)"
    }
  ],
  
  "references": [
    {
      "title": "string",
      "url": "string",
      "description": "string"
    }
  ],
  
  "generation_metadata": {
    "prompt_tokens": "integer",
    "completion_tokens": "integer",
    "generation_time": "float (초)",
    "temperature": "float",
    "retries": "integer"
  }
}
```

---

### 2.5 Report Data (리포트 데이터)

#### DiagnosticReport
```json
{
  "report_id": "string (UUID)",
  "video_id": "string (UUID)",
  "generation_timestamp": "string (ISO 8601)",
  
  "teacher_info": {
    "name": "string",
    "school": "string",
    "subject": "string",
    "experience_years": "integer"
  },
  
  "lesson_info": {
    "date": "string",
    "grade": "string",
    "topic": "string",
    "duration": "float (초)"
  },
  
  "charts": {
    "radar_chart": {
      "labels": ["string"],
      "scores": ["float"],
      "image_url": "string (PNG)",
      "data": { ... }
    },
    
    "time_distribution_pie": {
      "labels": ["도입", "전개", "정리"],
      "values": ["float"],
      "image_url": "string",
      "data": { ... }
    },
    
    "context_distribution_bar": {
      "labels": ["설명", "질문", "피드백", "촉진", "관리"],
      "values": ["float"],
      "image_url": "string",
      "data": { ... }
    },
    
    "heatmap_3d": {
      "rows": ["string"],
      "columns": ["string"],
      "values": [["float"]],
      "image_url": "string",
      "data": { ... }
    },
    
    "timeline_chart": {
      "time_points": ["float"],
      "cognitive_levels": ["integer"],
      "image_url": "string",
      "data": { ... }
    }
  },
  
  "comparison": {
    "enabled": "boolean",
    "previous_lesson": {
      "video_id": "string",
      "date": "string",
      "topic": "string"
    },
    "changes": [
      {
        "metric_name": "string",
        "previous_score": "float",
        "current_score": "float",
        "change": "float",
        "change_percent": "float",
        "trend": "string (improved/declined/stable)"
      }
    ]
  },
  
  "outputs": {
    "pdf_url": "string",
    "html_url": "string",
    "csv_url": "string",
    "json_url": "string"
  }
}
```

---

## 3. 데이터베이스 스키마

### PostgreSQL Tables

#### users
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    school VARCHAR(200),
    subject VARCHAR(100),
    experience_years INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### videos
```sql
CREATE TABLE videos (
    video_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    duration FLOAT,
    
    lesson_date DATE,
    grade VARCHAR(50),
    subject VARCHAR(100),
    topic TEXT,
    
    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(50), -- pending, processing, completed, failed
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    
    CONSTRAINT valid_status CHECK (processing_status IN 
        ('pending', 'processing', 'completed', 'failed'))
);
```

#### transcripts
```sql
CREATE TABLE transcripts (
    transcript_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(video_id) ON DELETE CASCADE,
    
    transcript_data JSONB NOT NULL, -- TeacherUtteranceTimeline 전체
    
    total_segments INTEGER,
    teacher_segments INTEGER,
    teacher_ratio FLOAT,
    avg_confidence FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transcripts_video_id ON transcripts(video_id);
CREATE INDEX idx_transcripts_data ON transcripts USING GIN (transcript_data);
```

#### analyses
```sql
CREATE TABLE analyses (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(video_id) ON DELETE CASCADE,
    transcript_id UUID REFERENCES transcripts(transcript_id),
    
    analysis_data JSONB NOT NULL, -- ThreeDimensionalMatrix 전체
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analyses_video_id ON analyses(video_id);
CREATE INDEX idx_analyses_data ON analyses USING GIN (analysis_data);
```

#### evaluations
```sql
CREATE TABLE evaluations (
    evaluation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(video_id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES analyses(analysis_id),
    
    evaluation_data JSONB NOT NULL, -- QuantitativeMetrics 전체
    
    overall_score FLOAT,
    overall_percentile FLOAT,
    grade VARCHAR(10),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evaluations_video_id ON evaluations(video_id);
CREATE INDEX idx_evaluations_score ON evaluations(overall_score);
```

#### coaching_feedbacks
```sql
CREATE TABLE coaching_feedbacks (
    feedback_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(video_id) ON DELETE CASCADE,
    evaluation_id UUID REFERENCES evaluations(evaluation_id),
    
    feedback_data JSONB NOT NULL, -- AICoachingFeedback 전체
    
    model_used VARCHAR(100),
    generation_time FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coaching_video_id ON coaching_feedbacks(video_id);
```

#### reports
```sql
CREATE TABLE reports (
    report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES videos(video_id) ON DELETE CASCADE,
    
    report_data JSONB NOT NULL, -- DiagnosticReport 전체
    
    pdf_path TEXT,
    html_path TEXT,
    csv_path TEXT,
    json_path TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_video_id ON reports(video_id);
```

---

## 4. 파일 스토리지 구조

```
/storage/
├── videos/
│   └── {user_id}/
│       └── {video_id}.mp4
│
├── audio/
│   └── {user_id}/
│       └── {video_id}.wav  (임시, 처리 후 삭제)
│
├── reports/
│   └── {user_id}/
│       ├── {report_id}.pdf
│       ├── {report_id}.html
│       ├── {report_id}.csv
│       └── {report_id}.json
│
├── charts/
│   └── {report_id}/
│       ├── radar.png
│       ├── time_pie.png
│       ├── context_bar.png
│       ├── heatmap.png
│       └── timeline.png
│
└── cache/
    └── {video_id}/
        ├── whisper_result.json
        └── diarization_result.rttm
```

---

## 5. API 요청/응답 형식

### 5.1 영상 업로드 API

**Request**
```http
POST /api/v1/videos/upload
Content-Type: multipart/form-data

{
  "file": <binary>,
  "metadata": {
    "lesson_date": "2025-11-08",
    "grade": "고등학교 2학년",
    "subject": "국어",
    "topic": "문학의 갈래"
  }
}
```

**Response**
```json
{
  "success": true,
  "data": {
    "video_id": "uuid",
    "upload_timestamp": "ISO 8601",
    "processing_status": "pending",
    "estimated_completion_time": "ISO 8601"
  }
}
```

### 5.2 처리 상태 조회 API

**Request**
```http
GET /api/v1/videos/{video_id}/status
```

**Response**
```json
{
  "success": true,
  "data": {
    "video_id": "uuid",
    "processing_status": "processing",
    "current_step": "transcription",
    "progress": 45,
    "steps": {
      "transcription": {"status": "in_progress", "progress": 60},
      "analysis": {"status": "pending", "progress": 0},
      "evaluation": {"status": "pending", "progress": 0},
      "coaching": {"status": "pending", "progress": 0},
      "report": {"status": "pending", "progress": 0}
    },
    "estimated_completion": "ISO 8601"
  }
}
```

### 5.3 리포트 조회 API

**Request**
```http
GET /api/v1/videos/{video_id}/report
```

**Response**
```json
{
  "success": true,
  "data": {
    "report_id": "uuid",
    "video_id": "uuid",
    "overall_score": 72.5,
    "grade": "B+",
    "outputs": {
      "pdf": "https://storage.../report.pdf",
      "html": "https://storage.../report.html",
      "csv": "https://storage.../data.csv",
      "json": "https://storage.../data.json"
    },
    "preview": {
      "strengths": ["질문 빈도 우수", "시간 배분 적정"],
      "improvements": ["대기 시간 부족", "고차원 질문 부족"]
    }
  }
}
```

---

## 6. 데이터 유효성 검증

### Checklist Result 검증
```python
def validate_checklist(checklist: dict) -> bool:
    """체크리스트 결과가 유효한지 검증"""
    # 모든 값이 boolean이어야 함
    return all(isinstance(v, bool) for v in checklist.values())
```

### Score 범위 검증
```python
def validate_score(score: float) -> bool:
    """점수가 유효한 범위인지 검증"""
    return 0 <= score <= 100
```

### Confidence 검증
```python
def validate_confidence(confidence: float) -> bool:
    """신뢰도가 유효한 범위인지 검증"""
    return 0 <= confidence <= 1
```

### Stage Distribution 검증
```python
def validate_stage_distribution(stages: dict) -> tuple[bool, list[str]]:
    """수업 단계 분포가 정상인지 검증"""
    warnings = []
    
    intro_ratio = stages['introduction']['duration'] / total_duration
    dev_ratio = stages['development']['duration'] / total_duration
    close_ratio = stages['closing']['duration'] / total_duration
    
    if dev_ratio < 0.5:
        warnings.append("전개 단계가 50% 미만입니다")
    
    if intro_ratio > 0.3:
        warnings.append("도입 단계가 30% 초과입니다")
    
    return len(warnings) == 0, warnings
```

---

## 7. 데이터 백업 및 복원

### 백업 전략
- **증분 백업**: 매일 자정
- **전체 백업**: 매주 일요일
- **보관 기간**: 90일

### 백업 대상
1. PostgreSQL 데이터베이스
2. 영상 파일 (선택적)
3. 생성된 리포트 파일
4. 차트 이미지

### 복원 절차
```bash
# 데이터베이스 복원
pg_restore -d tvas_db backup_file.dump

# 파일 스토리지 복원
rsync -avz backup_storage/ /storage/
```

---

## 8. 데이터 보안 및 프라이버시

### 암호화
- **저장 시**: AES-256 암호화
- **전송 시**: TLS 1.3

### 개인정보 비식별화
```python
def anonymize_transcript(data: dict) -> dict:
    """전사 데이터에서 개인정보 제거"""
    # 학생 이름 치환
    data = replace_names_with_tokens(data)
    
    # 학교명 제거 (옵션)
    if config.anonymize_school:
        data['metadata']['school'] = "***"
    
    return data
```

### 데이터 삭제
- 사용자 요청 시 즉시 삭제
- 영상 파일: 처리 완료 후 30일 자동 삭제 (옵션)
- 분석 결과: 사용자가 명시적으로 삭제 요청 시
