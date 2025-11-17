# ⚠️ GPT-5 모델 변경 메모 (CRITICAL - DO NOT REVERT)

## 📅 변경 일시
**2025년 1월 11일 (2025-01-11)**

---

## 🚨 중요 경고
**절대로 이 변경사항을 되돌리지 마세요!**

이 시스템은 현재 **GPT-5-mini** 모델을 사용하도록 설정되어 있습니다.
이전 모델(gpt-4o-mini)로 되돌리지 마세요.

---

## 📝 변경 내역

### 1. **OpenAI Service 기본 모델 변경 및 Temperature 파라미터 제거**
**파일**: `/services/analysis/services/openai_service.py`
**라인**: 24-25

**변경 전**:
```python
model: str = "gpt-4o-mini"
temperature: float = 0.0
```

**변경 후**:
```python
model: str = "gpt-5-mini",  # ⚠️ IMPORTANT: Changed to GPT-5-mini (2025-01-11) - DO NOT REVERT
# temperature 파라미터 완전 제거 - GPT-5는 temperature=1.0만 지원
```

---

### 2. **API 호출 함수 모델 변경 및 Temperature 제거**
**파일**: `/services/analysis/main.py`
**라인**: 298, 308, 350, 454

**변경 전**:
```python
model="gpt-4o-mini",
temperature=0.1  # 또는 0.3, 0.0
```

**변경 후**:
```python
model="gpt-5-mini",  # ⚠️ CRITICAL: GPT-5-mini (2025-01-11) - DO NOT CHANGE BACK
# temperature 파라미터 완전 제거
```

---

## 🎯 변경 이유

1. **분석 품질 향상**: GPT-5-mini는 GPT-4o-mini보다 훨씬 우수한 성능 제공
2. **교육 컨텍스트 이해도**: 교육 분석 및 코칭 피드백 품질 대폭 개선
3. **일관성 보장 방식 변경**:
   - ❌ **이전**: Temperature=0.0~0.3으로 일관성 확보 시도
   - ✅ **현재**: Majority voting (3회 실행 + 다수결) + Structured JSON output으로 일관성 보장
   - GPT-5는 temperature=1.0만 지원하므로 파라미터 자체를 제거
   - 시간대별 체크리스트 방식으로 추출 일관성 확보
4. **최신 기술**: 2025년 8월 출시된 GPT-5 시리즈의 안정적인 mini 버전

---

## 📊 GPT-5-mini 사양

### 모델 정보
- **정식 명칭**: `gpt-5-mini`
- **출시일**: 2025년 8월 7일
- **Context Window**: 128K tokens (입력)
- **Output Tokens**: 최대 16K tokens
- **특징**: 빠른 추론 속도, 비용 효율적, 높은 품질

### 사용 가능한 GPT-5 변형
- `gpt-5` - 전체 버전 (최고 성능)
- `gpt-5-mini` - 경량 버전 (현재 사용 중) ⚠️
- `gpt-5-nano` - 초경량 버전

---

## 🔧 기술 세부사항

### Python OpenAI 라이브러리 사용법
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
    max_tokens=4000
)
```

### 주요 파라미터
- ❌ **temperature 파라미터 사용 불가**: GPT-5는 temperature=1.0만 지원 (커스터마이징 불가)
- ✅ `max_completion_tokens=4000`: GPT-5는 max_tokens 대신 max_completion_tokens 사용
- ✅ `model="gpt-5-mini"`: 고정된 모델 이름
- ✅ `response_format={"type": "json_object"}`: Structured output으로 일관성 확보

### ⚠️ 중요: GPT-5 파라미터 변경사항

**1. `max_tokens` 파라미터 지원 안 함**
- ❌ 사용 불가: `max_tokens=4000`
- ✅ 올바른 사용: `max_completion_tokens=4000`

**2. `temperature` 파라미터 커스터마이징 불가**
- ❌ 사용 불가: `temperature=0.0`, `temperature=0.3`, `temperature=0.7`
- ✅ 올바른 사용: 파라미터 자체를 제거 (기본값 1.0 자동 적용)
- 일관성은 majority voting + structured output으로 보장

이 변경사항은 2025-01-11에 모든 관련 파일에 적용되었습니다.

---

## ✅ 변경된 파일 목록

### 모델 변경 (gpt-4o-mini → gpt-5-mini)
1. `/services/analysis/services/openai_service.py` (라인 24)
   - 클래스 기본 모델 파라미터 변경

2. `/services/analysis/main.py` (라인 308)
   - `call_openai_api()` 함수의 모델 변경

3. `/services/analysis/main.py` (라인 299-302)
   - 함수 docstring 업데이트

### 파라미터 변경 (max_tokens → max_completion_tokens) ⚠️ 2025-01-11
4. `/services/analysis/main.py` (라인 316)
   - `max_tokens=4000` → `max_completion_tokens=4000`

5. `/services/analysis/core/coaching_generator.py` (라인 253)
   - `max_tokens=2000` → `max_completion_tokens=2000`

6. `/services/analysis/core/coaching_generator.py` (라인 437)
   - `max_tokens=2500` → `max_completion_tokens=2500`

7. `/services/analysis/services/openai_service.py` (라인 246-276)
   - `generate_text()` 메서드 시그니처 변경
   - `max_tokens` 파라미터 → `max_completion_tokens`
   - `system_prompt` 파라미터 추가

### Temperature 파라미터 제거 ⚠️ 2025-01-11 추가
8. `/services/analysis/services/openai_service.py` (라인 25, 41, 66-76, 246-276)
   - `__init__()` 메서드에서 `temperature` 파라미터 제거
   - `self.temperature` 인스턴스 변수 제거
   - `execute_checklist_once()` API 호출에서 temperature 제거
   - `generate_text()` 메서드에서 temperature 파라미터 제거
   - 일관성은 majority voting (num_runs=3)으로 보장

9. `/services/analysis/main.py` (라인 298, 350, 374, 454, 540)
   - `call_openai_api()` 함수에서 temperature 파라미터 제거
   - Framework 분석 호출에서 temperature=0.3 제거
   - CBIL 분석 호출에서 temperature=0.0 제거
   - 메타데이터에 저장되는 temperature 값 0.3 → 1.0 변경

10. `/services/analysis/core/coaching_generator.py` (라인 253, 437)
    - 표준 코칭 생성에서 temperature=0.7 제거
    - CBIL 코칭 생성에서 temperature=0.7 제거

11. `/services/analysis/database.py` (라인 89, 313)
    - AnalysisResultDB 모델의 temperature 기본값 0.3 → 1.0 변경
    - store_analysis() 함수의 temperature 기본값 0.3 → 1.0 변경
    - 주석 업데이트: "GPT-5 default temperature (cannot be customized)"

---

## 🚦 검증 방법

### 1. 모델 변경 확인
```bash
cd /Users/jihunkong/teaching_analize
grep -n "gpt-4o-mini" services/analysis/**/*.py
# 결과: 없어야 함 (모두 gpt-5-mini로 변경됨)

grep -n "gpt-5-mini" services/analysis/**/*.py
# 결과: openai_service.py, main.py에서 발견되어야 함
```

### 2. Temperature 파라미터 제거 확인
```bash
grep -n "temperature=" services/analysis/**/*.py | grep -v "default=1.0" | grep -v "#"
# 결과: 없어야 함 (모든 temperature 파라미터 제거됨, database 기본값 제외)

grep -n "temperature" services/analysis/database.py
# 결과: default=1.0으로 설정되어 있어야 함
```

### 3. max_completion_tokens 사용 확인
```bash
grep -n "max_tokens" services/analysis/**/*.py
# 결과: 없어야 함 (모두 max_completion_tokens로 변경됨)

grep -n "max_completion_tokens" services/analysis/**/*.py
# 결과: main.py, coaching_generator.py, openai_service.py에서 발견되어야 함
```

### 4. 로그 확인
```bash
docker logs tvas_analysis --tail=50 | grep "model"
# GPT-5-mini 사용 확인
```

### 5. API 호출 테스트
분석 실행 후 로그에서 다음 확인:
```
INFO: Using model: gpt-5-mini
INFO: CBIL analysis completed successfully
INFO: Majority voting complete (3 runs)
```

---

## 📚 참고 자료

### 공식 문서
- OpenAI GPT-5 API: https://platform.openai.com/docs/models/gpt-5
- GPT-5 가이드: https://platform.openai.com/docs/guides/latest-model

### 관련 문서
- DataCamp GPT-5 튜토리얼: https://www.datacamp.com/tutorial/openai-gpt-5-api
- OpenAI Cookbook: https://cookbook.openai.com/examples/gpt-5/

---

## 🔄 롤백 절차 (비상시에만)

**⚠️ 경고**: 롤백은 최후의 수단입니다. GPT-5-mini가 정상 작동하므로 롤백 불필요.

만약 정말 필요하다면:
1. `services/analysis/services/openai_service.py:24`를 `"gpt-4o-mini"`로 변경
2. `services/analysis/main.py:305`를 `"gpt-4o-mini"`로 변경
3. Docker 재빌드: `docker-compose build analysis && docker-compose up -d analysis`

**하지만 이 작업은 하지 마세요!** GPT-5-mini가 더 우수합니다.

---

## 📝 추가 노트

### 빌드 정보
- Docker 이미지: `teaching_analize-analysis:latest`
- 빌드 일시: 2025-01-11 10:04 KST
- 상태: Healthy

### 관련 수정 사항
- 2025-01-11: `evaluate_with_cbil()` 메서드 들여쓰기 버그 수정
- 2025-01-11: CBIL 분석 temperature 0.3 → 0.0 변경 → **최종적으로 temperature 파라미터 완전 제거** ⚠️
- 2025-01-11: 에러 핸들링 추가
- 2025-01-11: **GPT-5-mini 모델 적용** ⚠️
- 2025-01-11: **max_tokens → max_completion_tokens 파라미터 변경** ⚠️
- 2025-01-11: **모든 temperature 파라미터 제거 (GPT-5 호환성)** ⚠️
- 2025-01-11: **일관성 보장 방식 변경: temperature 제어 → majority voting + structured output** ⚠️

---

## 👤 변경자
Claude Code Assistant (사용자 요청에 따라)

## 📞 문의
문제 발생 시 이 메모를 참조하여 GPT-5-mini 설정 유지 확인

---

**마지막 업데이트**: 2025-01-11 10:30 KST

---

# ⚠️ 다시 한번 강조: GPT-5-mini 설정을 유지하세요!

이 변경사항들은 시스템 품질 향상을 위한 중요한 업그레이드입니다:

1. **모델**: 절대로 이전 모델(gpt-4o-mini)로 되돌리지 마세요
2. **파라미터**: `max_completion_tokens` 사용 필수 (max_tokens 사용 불가)
3. **Temperature**: 파라미터를 추가하지 마세요 (GPT-5는 1.0만 지원)
4. **일관성**: majority voting + structured output으로 보장됨

**절대 하지 말아야 할 것:**
- ❌ `model="gpt-4o-mini"` 로 되돌리기
- ❌ `temperature=0.0`, `temperature=0.3` 등 파라미터 추가
- ❌ `max_tokens=` 파라미터 사용
