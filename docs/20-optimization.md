> **이 모듈에서 만드는 것:** 지침 개선과 모델 학습을 구분하고, v1→v2 비교에서 확인한 원인에 맞는 다음 방법을 선택합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · 기존 평가 읽기와 로컬 학습 파일 준비부터 합니다.

**먼저 할 일:** L08의 실제 답변 한 쌍을 보고 지침·검색·도구 중 어디를 바꿔야 할지 적습니다.

**확인할 결과:** 개선 방법의 이유와 학습 16행·검증 8행의 의미를 설명합니다. Optimizer 제출이나 실제 학습은 필수가 아닙니다.

</div>

## 목표

**새로운 사실은 RAG, 답변 절차와 누락은 지침 개선, 반복적으로 배울 행동은 fine-tuning**부터 검토합니다.
이 실습의 개선 지침은 [v2](../data/prompts/agent-v2.txt) 하나입니다. 수정할 때마다 v3·v4 파일이나 검증 실행 번호를 만들지 않습니다.

## 개념과 실습 지도

**경험할 기능:** 지침 개선, 같은 입력의 비교, 선택적인 Agent Optimizer, SFT 데이터 준비입니다.

**무엇이며 왜 중요한가요?** 지침 개선은 모델이 주어진 정보로 답하는 절차를 바꿉니다. Fine-tuning은 예시로 행동을 학습시킵니다.
둘 다 없는 계약·환율·권한을 사실로 만들어 주지 않습니다.

**어떻게 사용하나요?** L08에서 한 번 비교한 실제 답과 문항별 Foundry 평가 이유를 읽고 원인을 분류합니다.
동점이나 하락도 그대로 해석하며, 높은 점수를 얻기 위한 반복 실행은 실습의 목표가 아닙니다.

**어디서 실행하나요?** [L08 Prompt Agent 비교](../samples/instruction_prompt_agent_lab.py), [선택적 Optimizer 코드](../samples/optimizer_lab.py),
[학습 데이터 준비](../samples/prepare_tuning.py)를 사용합니다. 포털은 Optimize/Fine-tune의 입력·제한·결과를 이해할 때 활용합니다.

## 준비

L08의 12개 고정 질문에 대한 v1/v2 Prompt Agent 원문, 보조 체크리스트, native 점수와 행별 이유가 있으면 됩니다. 이미 비교했다면 다시 호출하지 않습니다.
Optimizer와 실제 training job은 별도 승인·지원 모델·권한이 필요하며 기본 코스의 완료 조건이 아닙니다.

## 실행

### 1. 어떤 개선이 필요한지 구분하기

| 관찰한 문제 | 먼저 적용할 방법 |
| --- | --- |
| 새 정책을 모름 | 검색·문서·최신성·접근 범위 확인 |
| 일부 하위 질문이나 근거 누락 | v2의 질문 분리·주장별 근거·최종 확인 절차 |
| 잘못된 도구 입력이나 과도한 실행 | 함수 schema와 서버 권한·수량 검사 |
| 반복되는 형식·스타일 문제 | 충분한 예시를 준비한 뒤 fine-tuning 검토 |

v1을 일부러 약하게 고치거나 질문별 정답을 v2에 붙이지 않습니다. 두 지침에 같은 문맥·모델·질문·기준을 적용합니다.
이번 교육용 v1은 역할과 목표를 담은 단순한 초기 지침입니다. v2는 관측된 누락 가능성을 겨냥해 요청을 나누고, 검증된 사실과 미확인 정보를 구분하고, 주장별 근거를 고르고, 경계와 도구 조건을 확인한 뒤 누락을 점검하는 일반 절차를 추가합니다. 점수를 낮추기 위해 v1을 일부러 틀리게 하거나 답변을 제한하지 않습니다.

**한 행으로 판단하기:** L08의 한국어 `compound-request-no-tools` 원문과 native 이유를 나란히 엽니다. 관련성 4→5만 보고 “v2가 전반적으로 우수”라고 쓰지 않습니다. 두 답이 어떤 하위 요청을 다뤘는지 표시하고, 점수 이유가 실제 차이를 설명하는지 확인한 뒤 **관찰 → 가능한 원인 → 다음 방법 → 아직 모르는 것**을 한 줄씩 적습니다. 영어는 관련성이 동점이므로 한국어 결론을 옮겨 쓰지 않습니다. 새 측정 없이 할 수 있는 분석 과제입니다.

### 2. 선택: Agent Optimizer의 역할 이해하기

로컬 학습 데이터 준비가 목적이면 **3단계로 바로 이동**합니다. 이 선택 기능을 실행해야 v2를 사용할 수 있는 것은 아닙니다.

<details class="optional-path" markdown="1">
<summary>선택 참고: Optimizer의 조건과 제출 계획</summary>

Agent Optimizer는 Limited preview이며, 사용 가능 여부와 모델 지원 범위를 별도로 확인합니다.
기본 실습은 L08의 단일 비교로 충분합니다. Optimizer를 계속 제출하거나 후보를 자동 승격할 필요가 없습니다.
현재 저장소의 Hosted Responses agent는 `contoso-chat`(GPT-4.1-mini)을 사용하지만 L08은 GPT-6 Sol 기반 Prompt Agent 버전으로 평가했습니다. 이 Hosted 경로의 모델은 비교 대상과 달라 같은 조건의 Optimizer 후보를 만들 수 없습니다. 이번 비교의 두 Prompt Agent는 평가 전용으로 생성했으며 Hosted agent를 재배포·변경하지 않았습니다. 직접 작성한 v2를 Optimizer 산출물로 표현하지 않습니다.

```bash
python samples/optimizer_lab.py --agent ACTUAL_RESPONSES_AGENT --version ACTUAL_NUMERIC_VERSION --optimizer-deployment APPROVED_OPTIMIZER_DEPLOYMENT --prompt-file data/prompts/agent-v2.txt
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `optimizer_lab.py` | 실제 Responses agent/version·reflection 배포·현재 v2 지침의 제출 계획을 확인합니다. placeholder는 본인 환경의 값으로 바꿉니다. | `--live`가 없어 Azure 요청은 없습니다. 과거 배포 번호나 예전 검증을 새 v2의 증거로 사용하지 않습니다. |

</div>

실제 실행을 따로 승인할 때만 배포된 지침과 입력 데이터·평가 기준을 일치시킵니다.
기존 고급 도구의 동결 검사·dev-only 입력·후보 최대 2개·stall 1회·시간 제한·취소·소유 세션 정리 보호는 유지됩니다.
현재 수정본과 일치하지 않는 과거 동결이나 이미 소비한 시험지를 우회해서는 안 됩니다.
서비스의 `succeeded`와 후보 개선은 다릅니다. 누락·오류·실패를 확인하고 개선이 없으면 그대로 기록합니다.
서비스 생성 후보, 운영자가 수정한 후보, 직접 작성한 지침은 서로 다른 출처로 기록합니다. 영어 dev로 생성한 지침을 한국어로 옮긴 경우에는 번역·검토본이며, 한국어 응답은 별도 측정이 필요합니다.
이 고급 경로를 준비하는 작업은 v1→v2 학습 비교의 필수 단계가 아닙니다.

</details>

### 3. 로컬 SFT 데이터 형식 익히기

```bash
python samples/prepare_tuning.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `prepare_tuning.py` | 체크인된 합성 예시로 training/validation JSONL을 준비합니다. | 로컬 파일만 만듭니다. Azure 업로드·학습·배포를 실행하지 않습니다. |

</div>

터미널의 `Prepared train=16, validation=8 in results/tuning-…` 경로를 편집기로 엽니다. 원본은 [tuning/examples.json](../data/tuning/examples.json)이며 결과는 `train.jsonl`과 `validation.jsonl`입니다. **한 줄이 한 학습 예제**입니다. 생성될 첫 줄은 다음과 같습니다. 모델 응답을 실측한 것이 아니라 체크인 예제를 변환한 결과입니다.

```json
{"messages":[{"role":"system","content":"문의 유형을 POLICY, STOCK, DRAFT, CLARIFY 중 하나로만 분류한다."},{"role":"user","content":"노트북 정기 교체 기간을 알려줘."},{"role":"assistant","content":"POLICY"}]}
```

| 확인할 것 | 어떻게 판단하나요? | 실패하면 다음 행동 |
| --- | --- | --- |
| `system` / `user` / `assistant` | 분류 규칙 / 문의 / 학습할 정답 라벨 순서 | 역할 순서와 라벨을 원본 예제에 대조 |
| 네 라벨 | `POLICY` 규정, `STOCK` 조회, `DRAFT` 초안 요청, `CLARIFY` 모호한 요청 | 같은 뜻의 문의에 다른 라벨이 붙었는지 검토 |
| train 16행 / validation 8행 | 입력 중복 없이 학습 예제와 별도 점검 예제를 분리 | 생성기 오류를 보존하고 빈 입력·중복·split/라벨 오타 확인 |
| `DRAFT` 예제와 실제 실행 | **의도 분류**일 뿐 재고 확보·초안 생성 성공이 아님 | 품절이어도 요청 의도는 DRAFT일 수 있음. 실행 가능 여부는 L06 함수가 판단 |

`validation.jsonl`은 학습 과정의 점검용이며 L08 dev 비교나 봉인된 release holdout과 다릅니다. 이 작은 seed는 형식 연습이지 유용한 모델 학습 효과를 보장하지 않습니다. 정답/holdout을 복사해 데이터를 늘리지 않습니다.

### 4. 학습 방식을 선택하기

| 방식 | 데이터 | 주의점 |
| --- | --- | --- |
| SFT | 입력과 바람직한 출력 | 틀린 응답을 모방하지 않기 |
| DPO | 선호 응답과 비선호 응답 | 선호 기준의 일관성 |
| RFT | 문제와 검증 가능한 grader | 보상 편법과 grader 오류 |

![Fine-tuning 화면. 제품 예시와 실제 실습 job을 구분합니다.](../assets/portal/14-fine-tuning.png)

실제 학습은 지원 모델·지역·데이터 처리·비용을 확인하고 별도 승인 후 수행합니다.
학습 job 완료, 모델 배포, 평가 개선은 각각 다른 상태입니다. 자동 배포·승격을 기본값으로 삼지 않습니다.

## 성공 기준

v2의 개선 의도와 실제 답의 차이를 설명하고, 검색·지침·도구 제약·학습 중 적절한 방법을 선택할 수 있습니다.
학습 파일을 만들었다고 모델 학습이나 점수 향상을 완료했다고 쓰지 않습니다.

### L08의 실제 결과를 다음 개선 판단에 연결하기

| 언어 | 보조 체크리스트 v1→v2 | Native 완결성·관련성·근거성 |
| --- | ---: | --- |
| 한국어 | 33/40→33/40 (동점) | 완결성·근거성 5.0→5.0; 관련성 4.9167→5.0 (+0.0833) |
| English | 29/40→28/40 (−1) | 세 지표 모두 5.0→5.0 동점 |

한국어 Native 관련성에서 `compound-request-no-tools` 한 행만 4→5로 바뀌었고, 그 외 모든 지표는 동점입니다. 이는 작고 노출된 dev 비교에서 관측한 제한적인 관련성 향상이지 통계적 유의성·일반화·운영 승격 근거가 아닙니다. 체크리스트는 한국어 동점, 영어 −1이며 모든 변경 critical 플래그를 원문으로 검토했습니다. 일부는 v2가 권한·초안·자격 경계를 명시했지만 정규식이 표현을 놓쳤습니다. [문항별 원문과 Native 이유](../validation/current/report.json)를 확인하고 결과에 맞춰 지침이나 기준을 바꾸지 않습니다. v2 토큰은 한국어 +7,376·영어 +5,157, 평균 지연은 각각 +0.427초·+0.496초 늘었습니다.

[현재 Prompt Agent 비교](../validation/current/report.json)에 국문·영문 v1/v2의 12개 문항, Agent 버전, 평가 점수와 실제 변화가 기록됩니다. Hosted Optimizer 경로의 GPT-4.1-mini가 비교 대상 GPT-6 Sol과 달라 같은 조건을 만들 수 없어 Optimizer job은 제출하지 않았습니다. v2는 직접 작성본이지 Optimizer 생성 후보가 아닙니다. 기존 holdout도 열지 않았습니다. [이전 Optimizer 원본](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/validation/english/automated-v5/optimizer.json)의 실제 실행·실패 판정은 보존하며 현재 비교로 바꾸지 않습니다.

## 막혔을 때

Optimizer 계획이 막히면 Preview 접근·Responses protocol·대상 모델/배포 지침 일치부터 확인합니다. 보조 체크와 native 점수가 다르면 원문·체크 조건·judge 이유를 대조하고 한쪽 점수를 정답으로 단정하지 않습니다. SFT 생성 오류는 위 표의 입력/라벨/split부터 확인합니다. 조건이 준비되지 않은 cloud 작업은 미실행으로 남깁니다.

## 정리

로컬 데이터 준비만 했다면 cloud job은 없습니다. 별도 승인으로 job을 실행했다면 해당 소유 job·세션의 종료를 확인합니다.
리소스 삭제나 권한 변경은 별도 승인 없이 수행하지 않습니다.
