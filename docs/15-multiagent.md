> **완성할 결과:** 초안 작성자와 검토자가 역할을 나누되, 실제 승인은 모델이 대신하지 않는 2단계 흐름.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · 로컬 두 역할과 원격 A2A는 서로 다른 실험입니다.

**먼저 할 일:** `python samples/multi_agent.py`로 작성자 → 검토자 계획만 읽습니다.

**확인할 결과:** 실행했다면 역할별 출력·추가 지연과 A2A 위임 근거를 따로 기록합니다. 검토자의 답은 실제 구매 승인이 아닙니다.

</div>

## 목표

**에이전트 수를 늘리는 것이 목적이 아닙니다.** 역할·도구·평가 기준이 실제로 분리될 때만 orchestration을 추가합니다.

**중요:** Foundry 포털 Workflows는 Preview이며 **2026-12-01 종료 예정**입니다. 이 모듈은 **Microsoft Agent Framework**로 새 구현을 진행합니다.

## 개념과 실습 지도

**경험할 기능:** Microsoft Agent Framework의 순차 orchestration, 원격 A2A 위임, 사람 승인 경계입니다.

**무엇이며 왜 중요한가요?** Orchestration은 여러 작업의 실행 순서와 결과 전달을 정하는 코드입니다. 같은 프로세스의 drafter→reviewer와 다른 서비스에 요청하는 A2A는 실패·인증 경계가 다릅니다. 역할을 나누면 전문성을 분리할 수 있지만 호출 수·지연·권한 관리도 늘어납니다. Reviewer의 문장을 실제 업무 승인이나 독립적인 품질 검증으로 오해하지 않는 것이 중요합니다.

**어떻게 사용하나요?** 로컬 계획을 먼저 읽고 두 단계의 입력·출력을 확인한 뒤 단일 agent와 비교합니다. A2A에서는 agent card의 능력과 실제 위임 결과를 따로 확인합니다. 모델이 “위임했다”고 말하는 것만으로는 네트워크의 하위 호출이 있었는지 알 수 없습니다.

**어디서 실행하나요?** [multi_agent.py](../samples/multi_agent.py)는 별도 MAF 환경, [a2a_lab.py](../samples/a2a_lab.py)는 기본 SDK 환경입니다. 두 명령 묶음 사이에 Python 환경을 반드시 구분합니다. 포털 Workflows를 새 의존성으로 만들지 않습니다.

## 준비

L01의 프로젝트·모델·`.env`, 별도 Python 환경이 필요합니다. 기본 코스의 환경을 그대로 덮어쓰지 마세요.

2026-09-29 확인 기준 `agent-framework-foundry==1.13.1`은 `azure-ai-projects<2.7.0`을 요구합니다. 기본 코스는 2.7.0입니다. **각각 호환되는 환경을 분리**했습니다.

## 실행

### 1. 로컬 계획 확인하기

```bash
python samples/multi_agent.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `multi_agent.py` | 두 역할의 순차 흐름만 출력합니다. `--live`가 없으므로 Foundry 모델을 호출하지 않습니다. | `drafter → reviewer` 구조를 확인합니다. 배포·Azure 비용 없음. |

</div>

`drafter → reviewer` 계획만 출력하며 Azure를 호출하지 않습니다.

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

### 3. 실제 두 agent 실행하기

```bash
.venv-advanced/bin/python samples/multi_agent.py --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `multi_agent.py --live` | MAF 환경에서 drafter와 reviewer를 순차 실행하여 Foundry 모델을 호출합니다. | 모델 추론 비용 발생. orchestration은 로컬이며 Hosted 배포나 실제 승인 완료가 아닙니다. 각 역할의 출력과 추가 지연을 비교합니다. |

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
    max_iterations=4,
).add_edge(drafter, reviewer).build()
```

### 4. 단일 agent와 비교하기

같은 질문의 정확도·토큰·전체 지연을 기록합니다. 두 agent 결과가 더 길기만 하다면 단일 agent로 돌아갑니다. Reviewer라는 이름만으로 독립 검증이나 보안 경계가 생기지 않습니다.

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
