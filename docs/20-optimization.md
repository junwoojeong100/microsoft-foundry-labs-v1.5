> **완성할 결과:** 개선할 대상을 올바르게 선택하고, 학습 가능한 데이터와 과적합을 막는 비교 절차를 준비합니다.

## 목표

**새로운 사실은 RAG, 지시 문제는 prompt, 반복적으로 학습할 행동은 fine-tuning**부터 검토합니다. 기본 모델이 최신이라고 모든 학습 방식을 지원하지는 않습니다.

## 준비

L08의 baseline과 실패 사례, 별도 dev/holdout, 학습/평가/배포 비용 승인이 필요합니다. 실제 training job 제출은 선택이며 수십 분~수시간 이상 대기할 수 있습니다.

## 실행

### 1. 원인을 먼저 분류하기

| 실패 원인 | 우선 해결 |
| --- | --- |
| 회사 규정을 모름 | 문서 검색·지식 연결 |
| 올바른 문서를 못 찾음 | chunk·검색·권한·freshness |
| 도구 선택/설명이 모호함 | schema·description·instructions |
| 출력 형식만 흔들림 | structured outputs·검증 |
| 충분한 예시가 필요한 반복 행동 | fine-tuning 비교 |

### 2. Prompt / Agent Optimizer 실험

Agent의 **Optimize** 경험이 제공되면 baseline version, dev 데이터, 평가 기준, judge/optimizer 모델, 후보 수와 예상 비용을 확인합니다. **Agent Optimizer는 GA 표 기준 Limited preview**입니다. 접근이 없으면 실패 3개를 보고 사람이 prompt를 수정하는 같은 비교 루프를 수행합니다.

Prompt agent는 instructions·함수 description·모델 선택 등을, Hosted agent는 optimizer-ready 구성에 따라 instructions·skills·tool description·모델 등을 개선합니다. 모델 가중치를 학습하는 fine-tuning과 다릅니다.

도구를 포함한 optimizer/evaluation은 실제 도구를 여러 번 호출할 수 있습니다. 비운영 읽기/초안 도구로 제한합니다. client-side 함수의 description 최적화가 실제 함수 실행 품질까지 평가했다는 뜻은 아닙니다.

후보를 무조건 최신 버전으로 승격하지 마세요. 변경 diff·품질·토큰·지연을 확인하고 **사용하지 않은 holdout**으로 다시 평가합니다.

### 3. 로컬 SFT 데이터 준비하기

이번 추가 과제는 응답 내용을 외우게 하는 것이 아니라 문의를 `POLICY`, `STOCK`, `DRAFT`, `CLARIFY`로 분류하는 간단한 행동 학습입니다.

```bash
python samples/prepare_tuning.py
```

`results/tuning-.../train.jsonl`과 `validation.jsonl`이 생성됩니다. 샘플은 각각 16건/8건의 **형식 학습용 seed**입니다. 서비스의 최소 10건 조건을 만족하는 것과 유의미한 품질 개선은 다릅니다. 실제 학습에는 수십~수백 건 이상의 대표성 있는 고품질 데이터를 검토하세요.

SFT의 기본 모양:

```json
{"messages":[{"role":"system","content":"문의 유형을 POLICY, STOCK, DRAFT, CLARIFY 중 하나로만 분류한다."},{"role":"user","content":"노트북 교체 규정을 알려줘."},{"role":"assistant","content":"POLICY"}]}
```

현재 fine-tuning 문서의 파일 인코딩 요구에 맞춰 출력은 UTF-8 BOM을 포함합니다. 포털 업로드 전 파일 검증 결과와 대상 모델의 요구를 다시 확인합니다. 평가용 query/response JSONL을 SFT 데이터로 그대로 업로드하지 않습니다.

### 4. SFT / DPO / RFT 선택하기

| 방식 | 필요한 데이터 | 적합한 문제 | 함정 |
| --- | --- | --- | --- |
| SFT | 입력 + 바람직한 출력 | 형식·분류·반복 업무 행동 | 품질 나쁜 예시 학습 |
| DPO | 같은 입력의 선호/비선호 출력 | 응답 선호와 스타일 | 모호한 선호 기준 |
| RFT | 입력 + 검증 가능한 grader | 보상으로 판별 가능한 복합 행동 | reward hacking·grader 오류 |

Vision fine-tuning, tool calling, distillation, open-model training도 모델별 지원·라이선스·데이터 권한을 각각 확인합니다. SFT/DPO/RFT가 모든 모델에서 동시 지원되는 것이 아닙니다. 일부 GA 학습도 접근 제한이 있을 수 있습니다.

### 5. 조건부: 실제 training job 실행

**Build → Fine-tune → Fine-tune a model**에서 지원 base model·method·training tier를 선택합니다. train/validation을 분리 업로드하고 auto-deploy는 처음에는 끕니다. 비용·데이터 처리 위치를 확인한 후 담당자가 Submit합니다.

job status, training/validation curve, checkpoints를 확인합니다. 마지막 checkpoint가 항상 최선은 아닙니다. 승인된 임시 deployment에 배포하고, baseline과 같은 held-out 데이터·judge 설정으로 비교합니다.

## 성공 기준

로컬 데이터 형식과 split을 검증했습니다. 실제 학습을 진행했다면 **품질·지연·토큰·총비용**을 baseline과 비교하고 선택 이유를 기록합니다. 데이터 준비만 했다면 학습 완료로 표시하지 않습니다.

## 막혔을 때

학습 가능한 모델과 추론 가능한 모델은 다릅니다. training region/tier, 파일 형식, 권한, 최소 데이터 수를 확인합니다. 점수 향상이 없으면 먼저 데이터·평가 오염·grader 문제를 봅니다.

## 정리

training job, checkpoint/model, inference deployment, uploaded training file은 별도 객체입니다. inference deployment와 예약/유휴 비용을 특히 확인합니다.
