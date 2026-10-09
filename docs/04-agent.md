> **완성할 결과:** 역할과 한계가 명확한 Prompt Agent. 지식·도구를 추가하기 전의 기준 버전입니다.

<div class="lab-brief" markdown="1">

**진행 방식:** Microsoft Foundry 포털에서 직접 만들고, 같은 설정을 원본 SDK 코드와 대조합니다.

**먼저 할 일:** L02의 모델을 선택해 Text 에이전트를 만들고 동봉 지시문을 넣습니다.

**확인할 결과:** 없는 규정·재고를 지어내지 않고, 같은 대화와 새 대화의 차이를 확인합니다. 이 에이전트는 L05에서 이어 씁니다.

</div>

## 목표

Prompt Agent는 **모델 + instructions + tools**로 선언하는 관리형 agent입니다. 별도의 서버나 컨테이너를 직접 운영하지 않습니다. Hosted Agent와의 차이는 L12에서 다룹니다.

## 개념과 실습 지도

**경험할 기능:** 역할을 정한 Prompt Agent를 만들고 대화를 이어갑니다.

**무엇이며 왜 중요한가요?** Instructions는 에이전트가 따라야 할 지시문입니다. “재고 에이전트”라고 지시해도 재고 조회 기능이 생기지는 않습니다. 문서·도구 없이 시작해야 L05·L06에서 무엇이 달라지는지 보입니다.

**어떻게 사용하나요?** 모델과 지시문을 저장한 뒤 질문합니다. 같은 대화는 앞선 내용을 이어받고, 새 대화는 별도로 시작하는지 확인합니다.

**어디서 실행하나요?** 포털에 [지시문 원본](../data/prompts/agent-v2.txt)을 붙여넣고 아래 Python 코드에서 같은 Model·Instructions·Tools 값을 찾습니다. `workshop.py`는 이 SDK 동작을 receipt·호출 제한과 함께 감싼 별도 실행기입니다.

## 준비

프로젝트 `Foundry User`, 호출 가능한 모델, `data/prompts/agent-v2.txt`가 필요합니다.

## 실행

### 1. 포털에서 만들기

1. **Build → Agents → New agent → Build an agent**를 선택합니다. UI에 따라 **Build an agent**가 바로 표시될 수 있습니다.
2. `contoso-procurement-자신의고유번호`처럼 직접 고른 이름과 **Text** 모드를 지정합니다. 목표가 필요하면 “합성 Contoso 구매 규정을 안내하며 실제 주문은 하지 않는다”를 입력합니다. 같은 이름이 있다면 자신의 기존 실습인지 확인하고, 다른 사람의 agent는 수정하지 않습니다.
3. 열린 편집 화면의 **Model**을 L02의 배포로 선택합니다. VS Code에서 `data/prompts/agent-v2.txt`를 열고 **파일 내용 전체**를 Instructions에 붙여넣습니다. 파일 경로만 입력하는 것이 아닙니다.
4. **Save**하고 에이전트 이름·표시된 버전을 기록합니다. **Model이 맞고, Instructions가 저장되어 있으며, 지식·함수 도구가 아직 없는지** 확인한 뒤 오른쪽 Chat으로 갑니다.

이 에이전트는 L05에서 그대로 사용합니다. 아직 File search와 함수 도구를 붙이지 않았으므로 **없는 도구를 사용했다고 주장하면 안 됩니다.** 아래 실험은 질문 5회(한계 2회·같은 대화 2회·새 대화 1회)이며 승인된 범위에서 각각 한 번씩만 전송합니다.

![Prompt Agent 구성 예시. 왼쪽에 Model·Instructions·Tools, 오른쪽에 Chat/YAML과 메시지 입력, 위쪽에 버전·Save·Publish·Traces 탭이 있다.](../assets/portal/04-prompt-playground.png)

**화면 따라 읽기:** 왼쪽 **Model**에서 배포 이름, **Instructions**에서 지시문을 확인하고 오른쪽 **Chat**에 테스트 질문을 넣습니다. 위쪽 **Version**은 설정 버전, **New chat**은 대화 맥락을 구분하는 기능입니다. **Save**와 **Send**는 각각 설정 변경과 유료 요청이므로 목적을 확인한 후 누르세요.

사진은 지식·함수까지 연결한 구성 예시입니다. **L04에서는 지시문만 저장합니다.** File search는 L05에서, 함수 도구는 L06에서 다루므로 지금 화면과 똑같이 연결할 필요는 없습니다.

| 포털에서 하는 일 | SDK 코드에서 같은 값·동작 |
| --- | --- |
| **Model**에서 L02 배포 선택 | `model=deployment_name` |
| Instructions에 지시문 전체 붙여넣기 | `Path("data/prompts/agent-v2.txt").read_text(...)` |
| **Tools**를 비워 둠 | `tools=[]` |
| **Save**로 설정 버전 저장 | `project.agents.create_version(...)` |
| **New chat**로 새 맥락 시작 | `client.conversations.create()` |
| Chat에서 **Send** | `client.responses.create(..., extra_body={"agent_reference": ...})` |

같은 구성을 화면에서는 필드로, SDK에서는 인수로 표현합니다. L04에서는 포털에서 직접 한 번 만들고 질문합니다. 아래 코드는 그 조작이 실제 API에 어떻게 대응하는지 보여줍니다.

### 2. 기준 질문으로 한계 확인하기

```prompt
우리 회사 표준 노트북의 가격 상한은 얼마인가요?
```

정책 파일이 없는 상태에서 150만 원을 알고 있는 것처럼 답하면 안 됩니다. 제공된 규정이나 지식 연결이 필요하다고 답하는 것이 이 단계의 정상 동작입니다.

```prompt
NB-14의 실시간 재고를 확인해줘.
```

도구가 없으므로 조회 성공을 주장하면 실패입니다. **“모른다”는 답도 올바른 행동**입니다.

### 3. 대화 상태 실험하기

같은 대화에서 다음 두 입력을 순서대로 보냅니다.

```prompt
이번 대화에서는 모니터 구매를 검토하고 있어요.
```

```prompt
내가 검토하는 품목을 한 단어로 말해줘.
```

대답이 “모니터”인지 확인합니다. 새 대화를 시작해 두 번째 질문만 보내 봅니다. 이전 대화의 품목이 자동으로 전달되지 않아야 합니다. **Conversation 유지와 장기 Memory는 별개**입니다.

### 4. 이름·버전·대화·응답 구분하기

| 단위 | 언제 달라지나요? |
| --- | --- |
| Agent name | 하나의 논리적 agent를 식별 |
| Agent version | instructions·model·tools 구성 변경을 버전으로 저장 |
| Conversation | 독립적인 대화 맥락을 시작할 때 |
| Response | 대화 중 모델/agent가 한 번 실행될 때 |

지금 저장된 이름·버전과 각 질문의 응답 ID를 구분해 기록합니다. 버전을 늘리기 위해 지시문을 임의로 바꿀 필요는 없습니다. 나중에 설정을 바꿨다면 새 버전을 확인하되, “최신 버전”이 곧 “운영에 승인된 버전”은 아닙니다.

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 포털의 Model·Instructions·Save를 SDK와 대조하기 — 읽기용</summary>

### 5. 같은 구성을 원본 Python SDK 코드로 읽기

아래는 `workshop.py`의 `create_lab_agent()`와 `run_turn()`에서 사용하는 SDK 호출을 학습용으로 연결한 발췌입니다. `project_endpoint`는 자신의 주소, `deployment_name`은 `contoso-chat`입니다. **읽기용 코드**이며 실제 생성은 포털 또는 아래 소유 기록을 남기는 실행 경로 중 하나로 합니다.

```python
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import AzureCliCredential

project_endpoint = "<Project endpoint from L01>"
deployment_name = "<deployment name from L02>"
agent_name = "<unique-sdk-agent-name>"
instructions = Path("data/prompts/agent-v2.txt").read_text(encoding="utf-8")

with (
    AzureCliCredential(process_timeout=30) as credential,
    AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
        retry_total=0,
    ) as project,
    project.get_openai_client(max_retries=0, timeout=60.0) as client,
):
    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=deployment_name,
            instructions=instructions,
            tools=[],
        ),
        description="Synthetic workshop agent; never submit real orders.",
    )
    conversation = client.conversations.create()
    response = client.responses.create(
        conversation=conversation.id,
        input="우리 회사 표준 노트북의 가격 상한은 얼마인가요?",
        extra_body={
            "agent_reference": {
                "name": agent.name,
                "type": "agent_reference",
                "version": agent.version,
            }
        },
        max_output_tokens=2048,
    )
    if response.status != "completed" or not response.output_text or not response.output_text.strip():
        raise RuntimeError(f"Response not complete: {response.status}")
    print(response.output_text)
    print(f"response_id={response.id}")
```

`conversation.id`가 새 채팅의 맥락이고, `agent_reference`가 위에서 만든 버전을 가리킵니다. 포털에서는 New chat과 Send로 같은 개념을 조작합니다. 아직 정책 파일을 붙이지 않았으므로 규정 질문에 모른다고 답하는 것이 정상입니다.

실제로 실행하면 별도 agent·conversation을 만들고 모델 비용이 발생합니다. SDK 호출이 필요하면 소유 범위 receipt·호출 제한·`--live` opt-in을 추가한 아래 실행기를 사용하며, 포털 실습과 둘 다 실행하지 마세요.

</details>

<details class="optional-path" markdown="1">
<summary>선택: receipt·호출 제한이 포함된 완성형 SDK 실행기</summary>

```bash
python samples/workshop.py agent
python samples/workshop.py agent --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — SDK를 실행 경로로 선택한 경우만 사용합니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `agent` | 생성·호출할 Prompt Agent의 실행 계획을 출력합니다. 기본 지시 파일은 `data/prompts/agent-v2.txt`입니다. | Microsoft Azure 요청 없음. 지시문이 설명한 기능과 실제 연결할 도구를 먼저 구분합니다. |
| 2. `agent --live` | 고유 `contoso-lab-...` agent와 대화를 만들고 실제 모델 응답을 받습니다. 포털에서 만든 agent를 수정하지 않습니다. | 추론·서비스 비용과 새 실습 객체가 생깁니다. 출력된 receipt 경로는 L19 정리용으로 보관합니다. |

</div>

`workshop.py`는 위 원본 API 호출에 plan-only 기본값, 고유 receipt, 오류·호출 제한을 더한 실행기입니다. 충돌을 피하려고 `contoso-lab-...`라는 **새 agent**를 만들며 앞서 포털에서 만든 agent는 수정하지 않습니다. 생성 ID는 `results/contoso-lab-....json`에 저장됩니다.

이 명령의 기본 입력은 **상한 질문 1건**입니다. 위의 다섯 질문이나 같은 대화/새 대화 비교를 자동 수행하지 않습니다. 그 비교를 이어 하려면 receipt의 agent 이름을 포털에서 열어 해당 질문을 수행하고, 하지 않았다면 **대화 비교 미실행**으로 남깁니다. L05 SDK 경로는 이 agent에 파일을 추가하는 명령이 아니라 또 다른 agent를 만듭니다.

</details>

## 성공 기준

- 저장한 지침에 역할·근거·없는 정보 처리·도구 실패 처리·금지 행동이 있습니다.
- 한계 질문 2개에서 없는 규정이나 재고 조회 성공을 가장하지 않았습니다.
- 같은 대화에서는 앞선 맥락(예: 모니터)을 유지하고, 새 대화에서는 이어받지 않았습니다.

## 막혔을 때

| 증상 | 먼저 확인할 것 | 다음 행동 |
| --- | --- | --- |
| instruction을 바꿨는데 답이 그대로임 | 이전 대화의 문맥이 변경을 가릴 수 있음 | 새 버전을 선택한 뒤 **새 conversation**에서도 확인합니다. |
| 샘플 코드가 맞지 않음 | SDK 1.x의 Threads/Runs 코드를 섞었는지 | 2.x 샘플 기준을 유지하고 1.x 코드를 섞지 않습니다. |

## 정리

포털 agent는 L05에서 이어 사용합니다. SDK 경로를 선택했다면 L05의 SDK File search 경로가 새 agent를 만든다는 점과 각각의 소유 기록을 구분합니다. 자원 삭제는 L19에서 정확한 대상을 별도로 승인한 뒤 수행합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 내 agent 이름·버전과 다섯 질문의 답·대화 구분. 포털에서 만든 대상에는 SDK receipt가 자동 생성되지 않으므로 이름을 직접 기록합니다.

**다음:** [L05 회사 문서 연결](#l05). 기본 경로는 **지금 만든 포털 agent 그대로** 사용합니다.

</div>
