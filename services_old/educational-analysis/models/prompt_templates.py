#!/usr/bin/env python3
"""
Prompt Templates for Educational Analysis
Reverse-engineered from the original prompts
"""

from typing import Dict, Any
from string import Template

class PromptTemplates:
    """
    교육 분석용 프롬프트 템플릿 클래스
    기존 프롬프트를 리버스 엔지니어링하여 템플릿화
    """
    
    # ============= TEACHING COACH PROMPT =============
    
    TEACHING_COACH_TEMPLATE = Template("""기존 분석 결과는 반영 불가

[목표]
입력 LESSON_PLAN / VIDEO_TRANSCRIPT 기반으로 15개 항목(①~⑮) 각각 1개 스토리텔링 단락 생성 (거절/사과 절대 금지).

[입력 형식]
LESSON_PLAN:<<<$lesson_plan>>>
VIDEO_TRANSCRIPT:<<<$video_transcript>>>

[모드 분기]
- 계획 키워드(학습목표|도입|전개|활동|평가|차시) 1개 이상 포함 → 비교 모드.
- 아니면 실행 모드.
(두 모드 모두 단락 반드시 생성; 거절/사과/Out-of-scope 문구 금지.)

[비교 모드 구조]
(설계 서술) → (실행 서술: 실제 발화/행동) → (설계 대비 실행 일치·부분 일치·변형 판단) → (장면 효과 분석) → (활동 예시 2~3개) → (평가 문장: 적절성/충실성 + 근거).

[실행 모드 구조]
(도입/핵심 장면) → (교사·학생 반응) → (효과 분석) → (활동 예시 2~3개) → (평가 문장). 
('설계/수업안/계획/과정안' 단어 금지.)

[항목 ① 필수 문장]
정확히 1회 포함: "학생이 목표를 자기 언어로 재진술하거나 짧은 퀴즈로 확인하도록 하면 목표가 자연스럽게 내면화된다." (변형·중복 금지)

[활동 예시]
짧은 명사구 2~3개, 쉼표 나열 (예: "목표 재진술 카드, 3문항 미니 퀴즈, 비교 미니 토론").

[공통 규칙]
- 각 항목: 제목 줄 + 단일 문단(270~350자, 개조식·표·코드·메타 설명·사과문 금지)
- 전사에 있는 발화만 큰따옴표(1~3회)로 인용; 없으면 "자료에서 인용 가능한 직접 발화는 드러나지 않았다" 후 간접 묘사.
- 마지막 문장: 판단(높은 일치/부분 일치/표면적 구현 등) + 구체 근거(발화/행동).
- 항목간 상호 참조 금지.

[Fallback (정보 부족 시)]
"자료에서 <요소>는 명시적으로 드러나지 않았다. 이에 따라 관찰 가능한 단서를 기준으로 제한적 해석을 제시한다." 
→ 이후 구조를 계속 완성.

[무조건 산출 & 금지 패턴]
다음 단어·구는 절대 출력하지 않는다: "죄송", "사과", "답변할 수 없습니다", "부적합한 질문", "관계없는", "out of scope", "cannot answer", "처리 불가".
허구 발화 생성 금지.

[출력 형식]
① (항목 제목)
(단락…)

② (항목 제목)
(단락…)
… ③~⑮ 동일. 다른 텍스트 출력 금지.

이제 위 규칙을 적용하여 결과만 출력하라.""")

    # ============= DIALOGUE PATTERNS PROMPT =============
    
    DIALOGUE_PATTERNS_TEMPLATE = Template("""📋 분석 지침
분석 근거: VIDEO_TRANSCRIPT의 교사·학생 실제 발화/행동만 사용(추정·가공 금지).

재현성: 동일 대화 입력 시 결과(빈도·분석문) 항상 동일, 대화 변경 시 결과도 변경.

출력 순서 규칙

질문 유형: 사실적 → 해석적 → 평가적 (고정)

후속 질문 유형: 명료화 → 초점화 → 정교화 → 확장화 → 입증화 (고정)

수업대화 유형: 분석문·그래프 모두 빈도 높은 순 정렬
(동률 시: 추가하기 → 참여하기 → 반응하기 → 유보하기 → 수용하기 → 반대하기 → 변환하기)

분석 문단: 각 유형당 한 단락(개념 설명 + 실제 발화/행동 사례 + 빈도·경향성)

사례는 빈도 높은 유형부터 제시

빈도 표기: 구간명 + 회수 범위 (예: "약간 자주(5~6회) 관찰됨")
질의응답 구조의 수업사례를 실제 수업대화 사례로 제시

📊 7단계 빈도 구간
0 = 전혀(0회)
1 = 매우 가끔(1~2회)
2 = 가끔(3~4회)
3 = 약간 자주(5~6회)
4 = 자주(7~8회)
5 = 매우 자주(9~10회)
6 = 꾸준히(11회 이상)

📑 분석 항목
질문 유형(3종): 사실적 / 해석적 / 평가적

후속 질문 유형(5종): 명료화 / 초점화 / 정교화 / 확장화 / 입증화

수업대화 유형(7종): 추가하기 / 참여하기 / 반응하기 / 유보하기 / 수용하기 / 반대하기 / 변환하기

[분석 대상 전사]
$video_transcript

위 전사를 분석하여 각 유형별 정확한 빈도를 계산하고, 실제 발화 사례와 함께 분석 결과를 제시하라.""")

    # ============= CBIL EVALUATION PROMPT =============
    
    CBIL_EVALUATION_TEMPLATE = Template("""[최종 프롬프트: CBIL 7단계 분석 – 전 단계 설명형, 판단 및 대안 포함]

🎯 분석 목적
이 프롬프트는 실제 수업 장면 또는 전사 자료를 바탕으로 **개념기반 탐구학습(CBIL)**의 7단계 실행 여부를 평가하고,
각 단계가 지식 중심인지 개념 중심인지 구분하여 진단하며,
점수(0~3점)를 부여하고, 1점 이하일 경우에는 대안을 제시하는 것을 목적으로 한다.
Reflect(성찰) 단계는 별도로 독립 평가하되, 다른 6단계 전반에 걸쳐 학생의 사고 변화와 개념 재구성 여부를 종합 판단한다.

📘 분석 형식 (각 단계 공통)
아래 7단계(Engage~Reflect) 각각에 대해 하나의 문단으로 작성하되, 다음 내용을 문장 속에 자연스럽게 통합하여 서술하시오.
-수업 장면 서술
-실제 수업의 교사 언어, 학생 반응, 활동 구조 등 핵심 장면을 요약
-중심 사고 성격 분석
-이 장면은 지식 중심(정보, 감상, 정의 제시)인가?
-개념 중심(속성 분석, 관계 탐색, 일반화 유도)인가?
-판단 근거 제시
-질문 유형, 사고 수준, 활동 구조 등 이론적 기준에 따른 분석
-점수 부여 (0~3점)
-루브릭 기준에 따라 실행 수준 판단
※ 각 단계마다 개념 중심 실행이 명확하지 않으면 2점 이상 금지

🛠 대안 제시 (1점 이하일 경우 필수)
교사 언어 수정, 활동 구조 재설계, 사고 전환 전략 등을 1~2문단 제시

📗 CBIL 7단계별 평가 지침
1. Engage (흥미 유도 및 연결)
학생의 정서적·지적 호기심을 유도했는가?

점수: 개념 연결 + 몰입 유도(3), 일부 유도(2), 활동은 있으나 연계 약함(1), 없음(0)

2. Focus (탐구 방향 설정)
교사의 질문이 개념 중심 사고를 유도했는가?

단순 감상·정보 질문은 지식 중심

점수: 본질적 질문/개념 정의 중심(3), 시도 있음(2), 감상 중심(1), 없음(0)

3. Investigate (자료 탐색 및 개념 형성)
개념의 속성, 조건, 사례-비사례를 탐색했는가?

단순 감상/정보 정리는 지식 중심

점수: 구조적 탐색(3), 시도 있음(2), 감상 중심(1), 없음(0)

4. Organize (개념 구조화)
정보를 개념의 속성, 관계로 구조화했는가?

점수: 명확한 구조화(3), 시도 있음(2), 단편 정리(1), 없음(0)

5. Generalize (일반화 진술)
'대체로', '일반적으로'와 같은 언어를 사용해 개념 확장을 했는가?

점수: 일반화 명확(3), 시도 있음(2), 사실 요약 수준(1), 없음(0)

6. Transfer (새로운 맥락에 적용)
개념을 다른 맥락에 적용하거나 재해석했는가?

점수: 전이 적용 명확(3), 제한적 적용(2), 감상 중심(1), 없음(0)

7. Reflect (사고 성찰)
수업 전 과정(Engage~Transfer)에서 학생이 자신의 사고 변화, 개념 적용 결과, 개념 재구성을 성찰했는가?

단순 감정 표현은 제외

점수: 구조적 성찰 있음(3), 제한적 시도 있음(2), 감상 중심(1), 없음(0)

📊 점수 루브릭 (공통)
점수	실행 수준 설명
3점	개념 중심 사고 명확 (개념 정의, 속성, 관계, 일반화, 전이 등 포함)
2점	개념 중심 시도 있으나 구조적/명확성 부족
1점	지식 중심 실행이나 개념적 시도 일부 보임
0점	정보 회상, 감정 중심, 개념 중심 사고 없음

[분석 대상 전사]
$video_transcript

위 전사를 분석하여 CBIL 7단계별 실행 수준을 평가하고 점수를 부여하라.""")

    @classmethod
    def get_teaching_coach_prompt(cls, lesson_plan: str, video_transcript: str) -> str:
        """Generate teaching coach analysis prompt"""
        return cls.TEACHING_COACH_TEMPLATE.substitute(
            lesson_plan=lesson_plan or "없음",
            video_transcript=video_transcript
        )
    
    @classmethod 
    def get_dialogue_patterns_prompt(cls, video_transcript: str) -> str:
        """Generate dialogue patterns analysis prompt"""
        return cls.DIALOGUE_PATTERNS_TEMPLATE.substitute(
            video_transcript=video_transcript
        )
    
    @classmethod
    def get_cbil_evaluation_prompt(cls, video_transcript: str) -> str:
        """Generate CBIL evaluation prompt"""
        return cls.CBIL_EVALUATION_TEMPLATE.substitute(
            video_transcript=video_transcript
        )

    # ============= ANALYSIS ITEMS DEFINITIONS =============
    
    TEACHING_ITEMS = [
        "학습 목표의 명확성",
        "도입의 효과", 
        "학습 내용의 적절성",
        "학습 방법의 다양성",
        "상호작용과 개별화",
        "학습 평가의 타당성",
        "피드백의 효과",
        "수업의 전개",
        "활동의 효과",
        "평가의 충실성",
        "차시 예고",
        "학생 반응",
        "교사 반응", 
        "수업의 효과",
        "활동 예시"
    ]
    
    QUESTION_TYPES = ["사실적", "해석적", "평가적"]
    
    FOLLOWUP_TYPES = ["명료화", "초점화", "정교화", "확장화", "입증화"]
    
    DIALOGUE_TYPES = ["추가하기", "참여하기", "반응하기", "유보하기", "수용하기", "반대하기", "변환하기"]
    
    CBIL_STEPS = [
        "Engage (흥미 유도 및 연결)",
        "Focus (탐구 방향 설정)",
        "Investigate (자료 탐색 및 개념 형성)", 
        "Organize (개념 구조화)",
        "Generalize (일반화 진술)",
        "Transfer (새로운 맥락에 적용)",
        "Reflect (사고 성찰)"
    ]
    
    FREQUENCY_DESCRIPTIONS = [
        "전혀 (0회)",
        "매우 가끔 (1~2회)",
        "가끔 (3~4회)",
        "약간 자주 (5~6회)",
        "자주 (7~8회)",
        "매우 자주 (9~10회)",
        "꾸준히 (11회 이상)"
    ]
    
    @classmethod
    def count_to_scale(cls, count: int) -> int:
        """Convert count to 7-level scale"""
        if count <= 0:
            return 0
        elif count <= 2:
            return 1
        elif count <= 4:
            return 2
        elif count <= 6:
            return 3
        elif count <= 8:
            return 4
        elif count <= 10:
            return 5
        else:
            return 6
    
    @classmethod
    def get_frequency_description(cls, scale: int) -> str:
        """Get frequency description for scale"""
        return cls.FREQUENCY_DESCRIPTIONS[scale]