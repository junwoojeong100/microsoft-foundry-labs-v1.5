> **완성할 결과:** 검토를 받은 작성자가 답을 고치는 흐름과, 전문 담당자에게 제어를 넘기는 흐름을 구분합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · L13의 환경을 재사용하고 두 패턴을 하나씩 실행합니다.

**먼저 할 일:** 아래 두 계획을 읽고, 수정이 필요한 일인지 담당자 전환이 필요한 일인지 먼저 예측합니다.

**확인할 결과:** 그룹 채팅의 세 발언과 핸드오프의 실제 도구 호출·전문가 응답을 찾습니다. 종료 메시지와 업무 답변은 구분합니다.

</div>

## 목표

**“같이 대화한다”와 “담당자를 바꾼다”는 다릅니다.** 그룹 채팅은 검토를 받아 같은 작성자가 수정하고, 핸드오프는 다른 전문가가 다음 작업을 맡습니다. 어느 쪽도 사람의 구매 승인을 대신하지 않습니다.

## 개념과 실습 지도

**경험할 기능:** `GroupChatBuilder`와 `HandoffBuilder`의 메시지·제어 전달입니다.

**무엇이며 왜 중요한가요?** Group chat은 같은 팀의 반복 검토, handoff는 담당자 전환입니다. “위임했습니다”라는 말만으로 실제 제어가 넘어간 것은 아닙니다.

**어떻게 사용하나요?** 같은 정책·질문으로 두 패턴을 실행하고, 중간 답과 실제 핸드오프 도구 호출을 읽습니다. 반복 수와 비용 상한은 바꾸지 않습니다.

**어디서 실행하나요?** [multi_agent.py](../samples/multi_agent.py)를 `.venv-advanced`에서 실행합니다. 모델만 Azure에 있으며 Hosted·원격 A2A 서버는 만들지 않습니다.

## 준비

[L13 환경 준비](#l15)의 `.venv-advanced`, `.env`, **내 소유 기록** `results/azure-environment.json`, chat 배포의 **100,000 TPM / 60 RPM** 확인을 재사용합니다. L13의 유료 패턴 실행은 선행 조건이 아닙니다. Windows는 `.venv-advanced\Scripts\python.exe`를 사용합니다.

### 먼저 경로 정하기

| 지금 상태 | 진행할 단계 | 남길 결과 |
| --- | --- | --- |
| Azure 승인 없음 | 1단계의 두 계획만 읽기 | 차이·호출 상한 설명, 실제 실행 미실행 |
| 모델·소유 기록·비용 승인 있음 | 계획 → 그룹 채팅 → 결과 읽기 → 핸드오프 → 비교 | 두 원본 파일과 수정/위임 비교표 |

추가 자원을 배포할 필요는 없습니다. 두 패턴을 모두 선택하면 **최대 7회 모델 호출**입니다. 실행당 **180초·응답당 2,048토큰·재시도 0회**를 유지하며, 다음 패턴은 이전 시작부터 **1분 이상** 지난 뒤 시작합니다.

## 실행

### 1. 실행 전에 두 흐름 예측하기

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode group-chat
.venv-advanced/bin/python samples/multi_agent.py --mode handoff
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode group-chat` | 작성자 → 검토자 → 작성자 수정의 계획을 읽습니다. | SDK 초기화·Azure 호출·실행 증거 생성 없음. 최대 3회 호출 계획. |
| 2. `--mode handoff` | 분류 담당자 → 정책 또는 금액 담당자의 계획을 읽습니다. | 실제 위임 없음. 최대 4회 호출 계획. |

</div>

먼저 “290만 원 구매 안내를 검토받아 고치기”에는 그룹 채팅, “정책/금액 중 담당자를 선택하기”에는 핸드오프라고 적어 봅니다. **예측은 결과가 아닙니다.** 다음 단계에서 실제 전달을 확인합니다.

### 2. 그룹 채팅: 마지막 수정 답까지 읽기

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode group-chat --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode group-chat --live` | 검토 내용을 작성자에게 돌려주는 세 차례 대화입니다. 발언자는 코드의 round-robin으로 정하며 모델 사회자는 추가하지 않습니다. | 실제 모델 호출 최대 3회. 출력과 `Evidence:` 원본 파일을 확인합니다. |

</div>

편집기로 `Evidence:` 파일을 열어 `paths.group-chat.stages`를 찾습니다. 첫 작성자 답 → 검토자 답 → 마지막 작성자 답을 나란히 읽습니다. `model_call_completed` 이벤트의 `payload.input`과 `input_authors`로 검토가 실제 입력에 전달됐는지 대조합니다.

| 확인할 것 | 판단 |
| --- | --- |
| 세 stage의 `role` | 작성자·검토자·작성자 순서인가 |
| 첫 답과 마지막 `answer` | 검토에서 지적한 누락이 보완됐는가. 그대로라면 그대로 기록 |
| `final_messages`, `workflow_state` | 종료 상태인가. “대화가 종료됐다”는 orchestrator 문장은 구매 안내 답이 아님 |

### 3. 핸드오프: 말이 아닌 실제 제어 이전 찾기

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode handoff --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode handoff --live` | 허용된 정책·금액 담당자 중 하나로 제어를 넘깁니다. 전문가는 답한 뒤 종료하며 다시 위임하지 않습니다. | 최대 4회 모델 호출. 실제 위임 도구와 전문가 응답이 없으면 실패. 주문·사람 승인 없음. |

</div>

`paths.handoff.stages`에서 분류 담당자의 `handoff_calls`와 뒤따르는 전문가 응답을 찾습니다. `handoff_to_…` 도구 이름이 기록되고 선택된 전문가가 실제 답했는지 확인합니다. 도구 호출 없이 자연어로 “위임했다”고만 말하면 통과가 아닙니다.

샘플은 `require_per_service_call_history_persistence=True`로 제어 전환 뒤에도 대화 기록을 유지합니다. 이를 제거해 생긴 오류를 추가 재시도로 덮지 않습니다.

### 4. 한 가지 바꿔 비교하기

<div class="practice-block" markdown="1">

**직접 해보기:** 두 파일에서 `역할 순서 / 입력 전달 / 수정된 문장 / 위임 도구 / 종료 상태 / total_tokens / elapsed_seconds`를 기록합니다. 사용량 `null`은 0이 아닙니다.

**한 가지 바꾸기:** 추가 호출을 승인받은 경우, 선택한 한 패턴에 `--case boundary`만 추가합니다. 정확히 200만 원과 200만 1원의 승인 규칙을 비교하고 모델·정책·역할 지침은 그대로 둡니다. 계획만 읽은 경우 실제 비교는 미실행으로 표시합니다.

**결과 설명하기:** “수정이 필요해서 그룹 채팅 / 담당자를 바꿔야 해서 핸드오프” 중 자신의 업무에 맞는 선택을 한 줄로 적고 실제 입력·응답을 근거로 듭니다. 더 많은 호출을 했다는 이유로 품질이 좋아졌다고 결론내리지 않습니다.

</div>

### 5. 이 실습이 하지 않는 일 구분하기

로컬 역할 간 핸드오프는 **원격 Agent2Agent(A2A) 연결이 아닙니다.** 사람 승인(Human-in-the-loop), incoming A2A endpoint, 조직 권한 위임도 구현하지 않습니다. 외부 에이전트 연결이 필요하면 별도의 인증·protocol·사용자 권한 설계부터 진행합니다.

공식 [그룹 채팅](https://learn.microsoft.com/agent-framework/workflows/orchestrations/group-chat?pivots=programming-language-python)과 [핸드오프](https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python) 문서로 Builder의 역할을 비교합니다.

#### 포털 모델 배포와 Group chat/Handoff 코드

L14에는 Foundry Portal에서 설정하는 Group chat/Handoff 편집기가 없습니다. 포털은 모델 배포를 제공하고, 실제 참여자 선택·메시지 전달·종료 조건은 아래 Agent Framework 코드가 정합니다.

```python
from agent_framework.orchestrations import GroupChatBuilder, HandoffBuilder

def select_speaker(state):
    names = list(state.participants)
    return names[state.current_round % len(names)]

group_workflow = GroupChatBuilder(
    participants=[drafter, reviewer],
    selection_func=select_speaker,
    max_rounds=3,
    termination_condition=lambda messages: sum(message.role == "assistant" for message in messages) >= 3,
    intermediate_output_from=[drafter, reviewer],
).build()

handoff_workflow = (
    HandoffBuilder(
        participants=[coordinator, policy_agent, budget_agent],
        termination_condition=lambda messages: any(
            message.role == "assistant"
            and message.author_name in {"policy", "budget"}
            and message.text.strip()
            for message in messages
        ),
    )
    .with_start_agent(coordinator)
    .add_handoff(coordinator, [policy_agent, budget_agent])
    .build()
)
```

| 코드 설정 | Evidence에서 확인할 실제 결과 |
| --- | --- |
| `participants` | 각 stage의 agent author |
| `selection_func`, `max_rounds` | Group chat에서 누가 말했고 어디서 멈췄는지 |
| `with_start_agent`, `add_handoff` | `handoff_calls`에 실제 제어 이전이 기록됐는지 |
| Portal의 model deployment | 각 participant가 호출한 승인된 Foundry model |

참여자 변수는 `build_role()`이 만든 SDK agent입니다. 그룹 채팅은 세 발언, 핸드오프는 전문가 답변을 종료 조건으로 사용합니다. `multi_agent.py`는 선택한 workflow만 실행하며 포털에 이 그래프를 저장하지 않습니다.

## 성공 기준

그룹 채팅의 세 발언과 최종 수정 답, 핸드오프의 실제 도구 호출·전문가 응답·종료 상태를 선택한 실행 범위에서 확인했습니다. 역할의 검토·위임을 사람의 승인이나 원격 A2A 성공으로 표시하지 않습니다.

## 막혔을 때

| 증상 | 먼저 확인할 것 | 다음 행동 |
| --- | --- | --- |
| SDK import 실패 | L13의 Python 환경과 `pip check` | 기본 SDK와 섞지 말고 전용 환경으로 복귀 |
| 그룹 채팅의 끝이 종료 안내뿐 | `final_messages`와 `stages`를 혼동했는가 | 마지막 작성자 stage의 `answer`를 읽기 |
| 위임 도구/전문가 응답 없음 | `handoff_calls`, 실제 입력, 종료 이유 | 실패로 보존. 성공할 때까지 반복하지 않기 |
| 429·잘린 응답·시간 초과 | L02 처리량과 호출 시각·상한 | 새 호출 중지, 원본 오류 확인 후 승인된 재실행만 수행 |

## 정리

두 실행은 소유 모델을 호출할 뿐 Hosted 배포나 반복 예약을 만들지 않습니다. 원본은 `results/`에 보존하고, 전체 학습이 끝나면 [L19 공통 마무리](#l12)로 이동합니다.
