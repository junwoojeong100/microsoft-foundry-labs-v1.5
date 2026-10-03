> **완성할 결과:** 초안 작성자와 검토자가 역할을 나누되, 실제 승인은 모델이 대신하지 않는 2단계 흐름.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · 로컬 두 역할과 원격 A2A는 서로 다른 실험입니다.

**먼저 할 일:** `python samples/multi_agent.py --mode compare`로 단일 기준선과 작성자 → 검토자의 최대 3회 호출 계획을 읽습니다.

**확인할 결과:** 실행했다면 역할별 출력·추가 지연과 A2A 위임 근거를 따로 기록합니다. 검토자의 답은 실제 구매 승인이 아닙니다.

</div>

## 목표

**에이전트 수를 늘리는 것이 목적이 아닙니다.** 역할·도구·평가 기준이 실제로 분리될 때만 orchestration을 추가합니다.

**중요:** Foundry 포털 Workflows는 Preview이며 **2026-12-01 종료 예정**입니다. 이 모듈은 **Microsoft Agent Framework**로 새 구현을 진행합니다.

## 개념과 실습 지도

**경험할 기능:** 작성자 → 검토자 두 역할을 단일 에이전트와 비교합니다.

**무엇이며 왜 중요한가요?** Orchestration은 역할별 순서와 결과 전달을 정하는 코드입니다. A2A는 다른 서비스의 에이전트에 요청하는 별도 통신 방식입니다. 역할을 늘리면 호출·시간도 늘며 검토자의 말이 구매 승인은 아닙니다.

**어떻게 사용하나요?** 같은 질문의 단일 답·작성자 초안·검토자 답을 읽고 추가 토큰·시간을 비교합니다. A2A는 실제 하위 호출 근거로 별도 확인합니다.

**어디서 실행하나요?** [multi_agent.py](../samples/multi_agent.py)는 별도 MAF 환경, [a2a_lab.py](../samples/a2a_lab.py)는 기본 SDK 환경입니다. 두 Python 환경을 섞지 않습니다.

## 준비

L01의 프로젝트·모델·`.env`, 별도 Python 환경이 필요합니다. 기본 코스의 환경을 그대로 덮어쓰지 마세요.
실제 호출에는 관리자가 제공한 `results/azure-environment.json` 소유 기록이 필요합니다. 프로젝트 주소·언어가 `.env`와 다르면 중단합니다. 기록이 없다면 임의로 만들지 말고 관리자에게 받으며, 아래 계획·코드 읽기까지만 진행합니다.

2026-09-29 확인 기준 `agent-framework-foundry==1.13.1`은 `azure-ai-projects<2.7.0`을 요구합니다. 기본 코스는 2.7.0입니다. **각각 호환되는 환경을 분리**했습니다.

## 실행

### 1. 로컬 계획 확인하기

```bash
python samples/multi_agent.py --mode compare
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `multi_agent.py --mode compare` | 단일 기준선 1회와 작성자→검토자 2회, 합계 최대 3회 호출 계획을 읽습니다. | `--live`가 없으므로 SDK 초기화·Azure 호출 없음. |

</div>

`mode=compare`, `model_calls_if_approved=3`, 180초·응답당 2,048토큰·재시도 0회를 확인합니다. 기본 `--mode sequential`은 기존의 두 역할 경로이며 비교 모드와 호출 수가 다릅니다.

### 2. 심화 환경 설치하기

```bash
python3 -m venv .venv-advanced
.venv-advanced/bin/python -m pip install -r requirements-advanced.txt
.venv-advanced/bin/python -m pip check
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python3 -m venv .venv-advanced` | 기본 SDK와 분리할 MAF 환경을 만듭니다. 설치된 Python의 버전 요구도 확인합니다. | 로컬 환경 생성. 기본 `.venv`는 변경하지 않습니다. |
| 2. `.venv-advanced/bin/python -m pip install` | 심화 환경의 Python을 직접 지정하고 `-r requirements-advanced.txt`의 호환 조합을 설치합니다. | 패키지 다운로드·심화 환경 변경. Azure 호출 없음. |
| 3. `.venv-advanced/bin/python -m pip check` | 바로 그 심화 환경의 의존성 충돌을 검사합니다. | 실패하면 기본 환경 패키지를 무작정 합치지 말고 설치 조합을 확인합니다. |

</div>

Windows는 `.venv-advanced\Scripts\python.exe`를 사용합니다. 관리 정책에 맞는 패키지 저장소를 이용하세요.

### 3. 같은 질문으로 단일·두 agent 비교하기

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode compare --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `multi_agent.py --mode compare --live` | 같은 구매 질문·모델·정책으로 단일 기준선을 한 번, 작성자→검토자 흐름을 한 번 실행합니다. | 최대 3회 모델 호출·180초. 중간/최종 답, 실제 토큰과 경과 시간을 출력하고 고유 `Evidence:` JSONL에 보존합니다. Hosted 배포·실제 승인은 없습니다. |

</div>

이 예제는 로컬에서 Microsoft Agent Framework를 실행하고 Foundry 모델을 호출합니다. **Hosted Agent를 배포하는 명령이 아닙니다.** 두 역할에는 동일한 합성 정책을 명시적으로 제공하며, 검색 품질을 평가하는 RAG 예제도 아닙니다.

| 역할 | 입력 | 결과 | 금지 |
| --- | --- | --- | --- |
| drafter | 요청과 정책 | 구매 안내 초안 | 사실 없는 주문 완료 |
| reviewer | 초안과 정책 | 경계값·승인 규칙 검토 후 최종 안내 | 실제 업무 승인 |

핵심 흐름은 다음과 같습니다.

```python
workflow = WorkflowBuilder(
    start_executor=drafter,
    output_from=[reviewer],
    intermediate_output_from=[drafter],
    max_iterations=4,
).add_edge(drafter, reviewer).build()
```

### 4. 중간 답을 읽고 질문 하나 바꿔 보기

<div class="practice-block" markdown="1">

**직접 해보기:** 터미널의 `paths`를 읽습니다. 파일로 읽을 때는 `Evidence:` 경로의 마지막 `event=completed` 행에서 `payload.paths`를 엽니다. 예시 숫자가 아니라 자신의 반환값을 기록합니다.

| 결과 경로 | 읽을 내용 |
| --- | --- |
| `single.stages[0].answer` | 작성자와 같은 지침·정책을 사용한 단일 기준선 |
| `sequential.stages[0].answer` | 실제 작성자 중간 초안. 새로 요약하거나 추정한 답이 아님 |
| `sequential.stages[1].answer` | 중간 초안을 받은 검토자의 최종 안내 |
| 각 stage의 `response_id`, `input_tokens`, `output_tokens` | 그 호출의 식별자와 실제 SDK 사용량 |
| 각 path의 `elapsed_seconds`, `total_tokens` | 경로 전체 경과 시간과 호출별 토큰 합 |
| `sequential_minus_single` | 두 단계 − 단일의 시간·토큰 차이. 정답 개선 점수가 아님 |

작성자가 290만 원의 승인 역할을 빠뜨렸는지, 검토자가 보완했는지 **정책 3절**과 대조합니다. 둘 다 맞으면 “추가 품질 이득을 관측하지 못함”도 올바른 결론입니다. 토큰이 `null`이면 미수집이며 0으로 채우지 않습니다. 전체 경로 시간에 각 작업 시간을 다시 더하지 않습니다.
시간은 객체 구성 후 각 경로의 실행 구간입니다. 단일 경로를 먼저 실행하므로 인증·캐시·초기 지연의 영향을 받을 수 있습니다. 한 번의 시간 차이를 모델 자체의 성능 차이로 단정하지 않습니다.

**한 가지 바꾸기:** 원하면 별도 승인 후 질문만 경계값 사례로 바꿉니다. 모델·정책·지침은 그대로입니다. 이 명령은 이전 결과 조회가 아니라 최대 3회의 **추가 호출**입니다.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode compare --case boundary --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--case boundary` | 합계 200만 원과 200만 1원의 승인 경계를 같은 두 실행 경로로 비교합니다. | 새 모델 호출 최대 3회·새 evidence. 두 사례를 모두 실행하면 합계 최대 6회이며 각각 승인 범위가 필요합니다. |

</div>

**결과 설명하기:** `사례 / 단일 답의 오류 / 작성자 오류 / 검토 후 남은 오류 / 추가 토큰·시간 / 두 역할을 유지할 이유`를 적습니다. 200만 원은 팀장, 200만 1원은 팀장+구매 담당자입니다. 한 번씩의 호출은 변동성이 있는 관찰이지 통계적 우월성 증명이 아닙니다. 사람 승인과 A2A 위임도 이 비교의 결과로 합산하지 않습니다.

</div>

<details markdown="1">
<summary>다른 orchestration 패턴 선택 기준</summary>

| 패턴 | 선택할 상황 | 비용/실패 주의 |
| --- | --- | --- |
| Sequential | 전 단계 결과를 다음 단계가 검토 | 전체 지연 누적 |
| Concurrent | 독립적인 조사·평가 | 병렬 토큰 비용·결과 충돌 |
| Handoff | 전문 담당자로 대화 제어 이전 | 권한·히스토리 범위 |
| Group/Magentic | 계획·역할 조정이 필요한 복합 업무 | 반복 제한·중단 조건 |
| 명시적 workflow graph | 조건 분기·체크포인트·사람 입력 | 실패/재개 상태의 관리 |

</details>

### 5. 실제 A2A 위임하기

A2A는 다른 서비스·벤더의 agent를 호출하는 통합입니다. 위의 in-process MAF와 다릅니다.
이 경로는 **기본/`.venv-live` SDK 환경**에서 실행합니다. A2A 1.0 GA와 0.3 Preview를 혼용하지 않습니다.

```bash
python samples/a2a_lab.py create
python samples/a2a_lab.py create --live
python scripts/runtime_roles.py --agent results/a2a.json의-caller --live
python samples/a2a_lab.py card --live
python samples/a2a_lab.py invoke --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — 먼저 기본/`.venv-live` SDK 환경으로 돌아옵니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `a2a_lab.py create` | worker·coordinator·연결의 생성 계획을 읽습니다. | Azure 요청 없음. |
| 2. `create --live` | 새 정책 worker와 coordinator 및 A2A 연결을 실제 구성합니다. | 원격 객체·`results/a2a.json` 생성. 기존 agent를 재사용한다고 가정하지 않습니다. |
| 3. `runtime_roles.py --agent ... --live` | `results/a2a.json의-caller`를 그 JSON의 `caller` 값으로 바꿉니다. 소유 caller의 runtime ID에 프로젝트 범위 호출 역할을 부여합니다. | 실제 권한 변경이므로 관리자 작업입니다. JSON 파일 경로 자체가 agent 이름은 아닙니다. |
| 4. `card --live` | 소유 worker의 실제 incoming agent card를 읽어 연결 계약을 확인합니다. | 원격 metadata 조회. 업무 질문의 성공과 별개입니다. |
| 5. `invoke --live` | coordinator에 합성 요청을 보내 원격 worker 위임과 반환 item을 확인합니다. | 실제 모델·agent 호출 비용 발생. A2A 호출 증거가 없으면 위임 성공으로 표시하지 않습니다. |

</div>

동봉 코드는 새 Contoso 정책 worker와 coordinator를 만들고, incoming A2A agent card 및
`agentic-identity` connection을 연결합니다. `results/a2a.json`의 worker/caller version을 고정합니다.
관리자는 새 caller identity가 해당 worker를 호출할 최소 프로젝트 역할을 부여해야 합니다.
직접 card를 조회할 때 Foundry 1.0 경로는 `agentCard/v1.0`입니다. 일반 `.well-known/agent-card.json`과
혼동하지 않습니다. 반면 Foundry를 가리키는 `A2ATool`은 `agent_card_path`를 생략해 서비스의
기본 해석을 사용합니다. 기존 실습 caller의 연결을 보정해야 한다면 `rebind --live`가 이전 버전을
보존한 채 새 버전을 만듭니다.
실제 반환 item에 A2A 호출이 없으면 “위임했습니다”라는 문장만으로 성공 처리하지 않습니다.
서비스가 숨긴 하위 응답은 추측하지 않으며 response/task ID가 실제로 노출된 범위만 기록합니다.

승인 단계에서는 **“승인합니다”라는 모델 문장** 대신 실제 승인 요청 ID와 사람의 결정을 저장하고, 승인된 내용이 변경되지 않았는지 검증합니다. L06 샘플에는 실제 업무 실행이 없으므로 승인 프로세스를 완료한 것으로 가장하지 않습니다.

## 성공 기준

두 MAF 단계와 A2A 원격 위임은 각각 실행 증거를 확인합니다.
단일 agent 대비 추가 비용이 정당한지 설명할 수 있습니다.
HITL는 설계이며 실제 업무 승인 완료를 수행한 것으로 표시하지 않습니다.

## 막혔을 때

SDK import 오류는 환경 혼용부터 확인합니다. 이 샘플은 core `WorkflowBuilder`를 사용하며 별도의 `agent-framework-orchestrations` 패키지를 요구하지 않습니다. 문서의 다른 `SequentialBuilder` 예제에는 추가 패키지가 필요할 수 있습니다.

## 정리

모델 호출 비용을 기록합니다. 운영에 옮길 때는 L14의 hosted runtime과 L22의 릴리스 게이트를 사용합니다.
