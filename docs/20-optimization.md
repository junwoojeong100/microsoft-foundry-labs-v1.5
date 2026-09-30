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

동봉 native Agent Optimizer 경로:

```bash
python samples/optimizer_lab.py --agent 실제-agent --version 실제숫자 --optimizer-deployment 지원-optimizer-배포 --suite automated-v2
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/optimizer_lab.py --agent 실제-agent --version 실제숫자 --optimizer-deployment 지원-optimizer-배포 --suite automated-v2 --live
```

첫 명령에서 제출될 **automated-v2 dev 20건·holdout 0건**, 후보 최대 2개, stall 최대 1회를 확인합니다.
기존에 노출된 20건은 v2 dev이고, 새로 봉인된 holdout은 optimizer가 파일을 열거나 제출하지 않습니다.
`load_cases(suite, split="dev")`로 dev 파일만 읽습니다. 전체 split을 읽은 뒤 필터링하지 않습니다.
suite·dev ID/hash·실제 제출 설정을 원본 evidence에 기록하며, holdout 기반의 품질 통과를 주장하지 않습니다.
다른 실습의 기본 suite가 바뀌어도 이 비교의 CLI 기본값은 `automated-v2`로 고정합니다.
기존 함수 호출 `payload(...)`는 진단용 `legacy-v1` 기본값을 유지하지만,
CLI 실행은 선택한 suite를 명시적으로 전달하며 새 legacy job은 제출하지 않습니다.

Hosted native 최적화는 `AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd deploy contoso-purchasing-responses --no-prompt`로 준비한
**Responses adapter**를 대상으로 합니다. Invocations agent를 그대로 제출하면 서비스가 400으로 거절합니다.
optimizer 모델은 서비스가 요구하는 모델 계열을 별도 확인합니다.
이번 API는 `gpt-5-mini`를 reflection 모델로 허용하지 않았으며, 지원 목록을 확인한
`gpt-5.1` 배포로 구분했습니다. 추론 모델 지원과 optimizer reflection 모델 지원은 다릅니다.
Hosted 패키지는 `azure-ai-agentserver-optimization==1.0.0b1`의 `load_config()`와
`.agent_configs/baseline/`을 포함합니다. baseline model은 패키징 시 승인된 배포 이름으로 고정하며,
환경이 없을 때 만든 오프라인 패키지는 실행 전에 다시 생성해야 합니다.
client-side 함수를 서버가 실행할 수 없는 agent를 대상으로 삼지 않습니다.
동봉 runner의 명시적 `optimization_config.system_prompt`는 `agent-v4.txt`이며,
이번 실험의 대상은 이를 포함한 `contoso-purchasing-responses` version `2`입니다.
다른 baseline을 대상으로 바꿀 때는 원본 지시와 optimizer 입력이 같은지 먼저 확인합니다.
inline 학습 데이터의 wire 필드는 `train_dataset.items`입니다(`dataset_items`가 아닙니다).

최대 10분은 **job 생성 시각부터** 계산합니다. 모니터링을 재개해도 시간을 다시 주지 않습니다.
SDK 자동 LRO polling 대신 `polling=False`로 제출하고 API 버전이 포함된 명시적 GET으로 조회합니다.
이 서비스의 `Operation-Location`에 API 버전이 없어 자동 polling이 실패했던 원본 기록도 보존합니다.
timeout·조회 실패·중단에서는 `finally`로 cancel하고 terminal 상태를 확인합니다.
native 세션은 azd 목록에 누락될 수 있어, 소유 App Insights에서 같은 agent/version과 job 시간 범위의
session ID도 수집합니다. `show`로 생성 시각과 version을 검증한 새 세션만 stop합니다.
성공한 stop 호출 뒤 같은 ID의 `idle`/`stopped`를 다시 읽습니다.
현재 CLI가 `stopped_at`을 생략한다는 사실도 기록하며, 그 값을 만들어 채우지 않습니다.
취소/중지 확인이 실패하면 **아직 실행 중일 수 있음**으로 보고합니다.
기존 job/receipt를 덮어쓰거나 리소스를 삭제하지 않습니다. 후보는 자동 배포/승격하지 않습니다.

| 관측 결과 | 기록할 판정 |
| --- | --- |
| `succeeded`지만 reflection failure/authentication/timeout 경고 | **operational_failure** — 성공으로 바꾸지 않음 |
| reflection 사용과 모든 native evaluation 완료가 확인되지만 점수 향상 없음 | **executed_no_improvement** — 운영 실행과 품질 개선을 구분 |
| baseline만 있고 reflection 실행 증거 없음 | **reflection_unverified** |
| 후보의 변경 내용 누락, 평가 행 누락/오류, partial 결과 | 불완전한 증거 또는 운영 실패 — 개선 완료가 아님 |

별도 native evaluation의 `completed`, 행 수, `errored=0`도 확인합니다.
서비스 상태나 baseline 점수 하나만으로 정상 최적화/품질 통과를 판단하지 않습니다.
사람의 후보 검토는 선택 안내이며 `human_review_completed=false`를 사실대로 유지합니다.

서비스 접근이 차단되면 **native optimizer 차단**으로 기록합니다. 별도 사람이/개발자가 dev의
실제 실패를 보고 수정한 후보를 native optimizer 결과처럼 표시하지 않습니다.
후보 파일과 변경 사유를 남기고 L08의 같은 dev 기준으로 비교한 뒤 holdout을 한 번 확인합니다.

azd의 자동 suite 생성은 최소 15 samples를 요구할 수 있습니다. 수를 맞추려고 사례를
복제하거나 봉인된 holdout을 넣지 않습니다. 동봉 SDK runner는 승인된 v2 dev 20건만
직접 제출하며, 자동 생성 CLI의 지원 범위와 구분합니다.
기존 legacy-v1 작업은 원래 receipt로 조회만 재개할 수 있고 새 legacy 작업 제출은 거절합니다.
이 경로는 데이터 파일을 다시 읽거나 작업을 재제출하지 않습니다.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/optimizer_lab.py --agent contoso-purchasing-responses --version 2 --optimizer-deployment contoso-reflection --suite legacy-v1 --resume 실제-기록된-job-id --live
```

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

**기존 native optimizer job `opt_f732793c2d284a4f874966ed2caca4bf`는 서비스 상태 `succeeded`였지만 baseline만 반환했습니다.**
새 후보는 0개이고 reflection 모델 오류/timeout 관련 경고가 있었습니다.
baseline의 별도 점수 0.95를 holdout 품질 통과로 사용하지 않았으며 후보를 승격하지 않았습니다.
개선된 v1→v4 지시는 native optimizer 산출물이 아니라 **dev 실패에 근거한 개발 과정의 변경**입니다.
후속 검사에서 같은 로컬 CLI 사용자로 `contoso-reflection`의 Chat Completions 호출은 HTTP 200,
`gpt-5.1-2025-11-13` 응답과 종료를 반환했습니다. 기존 baseline 평가도 10건 완료·오류 0건입니다.
따라서 포괄적인 reflection 경고만으로 권한/토큰/timeout 중 정확한 원인을 단정하거나
Owner/광범위 역할을 추가하지 않았습니다. 직접 모델 접근 성공과 native 서비스 내부 호출 성공은 별개입니다.

별도 v2 로컬 job `opt_15ea242beb4e4e4f945fac6b5abfa868`도 5분 안에
`succeeded`/`stopped_early`로 끝났지만 같은 reflection 경고와 baseline만 반환했습니다.
native 평가 `evalrun_da4f0442f71049ba868dd677b15e310d`는 20건 중 19건 통과·1건 오류이며,
output item `13`의 evaluator 상태는 `error`지만 상세 원인은 서비스 응답에 없었습니다.
0.91875라는 원본 composite score를 품질 통과로 사용하지 않습니다.
suite가 다른 기존 0.95와도 직접 성능 비교하지 않습니다.
두 native 세션은 CLI 목록에 보이지 않아 해당 job의 trace로 찾은 뒤 stop/idle readback을 확인했습니다.
job·오류·세션 중지 기록은 `results/contoso-optimizer-ea97bd8ba694*.json*`와
`results/contoso-optimizer-3cf33582e7d6.jsonl`에 보존합니다.

추가 로컬 job은 제출하지 않았습니다. 남은 차등 진단은 이미 승인된 OIDC CI 주체로
**같은 Responses version 2·dev 20건·task_adherence·judge `contoso-judge`·reflection `contoso-reflection`**
설정을 한 번 실행하는 것입니다. OIDC가 원인/해결책임을 확인한 것은 아닙니다.
CI의 Azure CLI와 azd가 같은 소유 환경에 로그인한 뒤 위 `--suite automated-v2 --live` 명령을 사용하고,
후보 최대 2개·stall 1회·10분·승격/배포 없음·봉인 holdout 접근 없음 제한을 유지합니다.

#### 선택: CI dev에서 OIDC 차등 진단

먼저 데이터셋을 전혀 읽지 않는 단일 모델 probe를 실행합니다. probe 통과도 native optimizer 성공이나
새 Invocations 버전의 품질 통과를 뜻하지 않습니다. 이어지는 비교는 원래 지시와 일치하는
**기존 Responses version 2**만 대상으로 하며, 새 Invocations 버전을 optimizer에 제출하지 않습니다.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill FOUNDRY_AUTH_MODE=cli \
python samples/optimizer_lab.py --probe-reflection --optimizer-deployment contoso-reflection --require-oidc --live

AZURE_DEV_USER_AGENT=microsoft_foundry_skill FOUNDRY_AUTH_MODE=cli \
python samples/optimizer_lab.py --agent contoso-purchasing-responses --version 2 \
  --optimizer-deployment contoso-reflection --suite automated-v2 --require-oidc --live
```

probe는 모델 요청 1회, completion 최대 256 tokens, 모델 응답 timeout 45초, 재시도 0회입니다.
`--require-oidc`는 모델 호출/새 job 제출 전에 `results/azure-environment.json`의
`tenant`, `oidc.principal_id`, `oidc.client_id`와 토큰의 안전한 주체 메타데이터를 비교합니다.
원본 토큰·키·connection string을 출력하거나 저장하지 않습니다.

CI가 전달할 안전한 필드는 프로젝트 endpoint·계정/프로젝트명·subscription/RG ID,
위 OIDC 식별자, `monitoring.appId.value`와 `monitoring.appInsightsId.value`입니다.
일반 환경 변수는 `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat`,
`FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge`이며 azd도 같은 소유 프로젝트로 해석되어야 합니다.
probe evidence에서 `identity.owned_ci_principal=true`, HTTP 200, 실제 response/request ID,
지원 model 이름과 `finish_reason=stop`을 확인합니다. job의 경고·오류는 별도로 보존하고,
이 선택 진단의 결과로 dev/calibration/release 품질 gate를 대체하거나 완화하지 않습니다.

## 막혔을 때

학습 가능한 모델과 추론 가능한 모델은 다릅니다. training region/tier, 파일 형식, 권한, 최소 데이터 수를 확인합니다. 점수 향상이 없으면 먼저 데이터·평가 오염·grader 문제를 봅니다.

## 정리

training job, checkpoint/model, inference deployment, uploaded training file은 별도 객체입니다. inference deployment와 예약/유휴 비용을 특히 확인합니다.
