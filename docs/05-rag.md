> **완성할 결과:** “노트북 상한 150만 원, 부가세 포함”을 실제 업로드 문서의 근거와 함께 답합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** L04의 포털 에이전트 재사용 · 업로드·검색 비용을 먼저 확인합니다.

**먼저 할 일:** 합성 정책 3개를 읽고 노트북 상한과 승인 규칙이 있는 절을 찾습니다.

**확인할 결과:** 답할 수 있는 질문 2개의 실제 인용과, 없는 규정에 대한 유보를 확인합니다. SDK 경로는 선택입니다.

</div>

## 목표

모델의 사전 지식 대신 **검색된 문서**로 답하게 합니다. Retrieval-Augmented Generation, 즉 RAG의 가장 짧은 경로입니다.

## 개념과 실습 지도

**경험할 기능:** File search로 회사 규정을 찾아 근거와 함께 답합니다.

**무엇이며 왜 중요한가요?** RAG는 **문서 검색 후 답변하기**입니다. 모델을 다시 학습시키지 않습니다. Vector store는 검색용 문서 보관소, citation은 답의 근거로 연결되는 인용입니다.

**어떻게 사용하나요?** 정책 3개를 읽고 업로드한 뒤 검색 준비 완료를 기다립니다. 세 질문의 답과 실제 인용을 원문에 대조합니다. 파일 이름만 적힌 답은 인용 확인이 아닙니다.

**어디서 실행하나요?** L04의 포털 에이전트에 [구매](../data/policies/procurement-policy.md)·[경비](../data/policies/expense-policy.md)·[보안 정책](../data/policies/security-policy.md)을 연결합니다. [SDK](../samples/workshop.py)는 선택 경로입니다.

## 준비

기본 경로는 L04의 **포털 agent**와 `data/policies/`의 Markdown 파일 3개를 사용합니다. 저장소 업로드 권한과 File search 추가 비용을 확인하세요. 회사 문서를 가져오지 않아도 실습할 수 있습니다. L04를 SDK로만 진행했거나 File search 편집이 지원되지 않으면 아래 선택 SDK 경로를 읽고, 새로 생성한 대상과 완료한 질문 범위를 따로 기록합니다.

## 실행

### 1. 세 문서를 먼저 읽기

| 파일 | 들어 있는 정보 | 들어 있지 않은 정보 |
| --- | --- | --- |
| `procurement-policy.md` | 품목별 상한, 36개월 교체, 승인 경계 | 현재 재고 |
| `expense-policy.md` | 사전 승인, 증빙, 환율 확인, 중복 금지 | 오늘 환율 |
| `security-policy.md` | 권한·데이터·실행 경계 | 개인별 인사 데이터 |

정답의 위치를 모르면 RAG 품질을 평가할 수 없습니다.

### 2. File search 연결하기

1. **Build → Agents**에서 L04에 기록한 **자기 에이전트 이름**을 엽니다. 새 에이전트를 만들지 않습니다.
2. Agent builder의 **Tools/Knowledge → File search**에서 기본 파일 검색 연결을 엽니다. 이 경로가 보이지 않으면 프로젝트의 지원 상태를 확인하고 아래 SDK 경로를 선택합니다. L07의 Cloud Toolbox 확장은 이 단계의 선행 조건이 아닙니다.
3. 자기 실습용 vector store를 만들고 `data/policies/`의 위 **Markdown 파일 3개만** 업로드합니다. ZIP 전체나 `data/` 폴더 전체를 올리지 않습니다.
4. 파일 3개의 인덱싱이 **Completed**인지 확인합니다. 업로드 완료와 검색 준비 완료는 다릅니다. 연결을 **Save**하고 에이전트 버전과 store 이름을 기록합니다.
5. **New chat**으로 새 대화를 열어 아래 세 질문을 각각 한 번씩 보냅니다. 지식 추가 전 L04 대화와 구분합니다.

![도구 연결 설정 예시. File search 카드와 별도의 get_stock·prepare_purchase_request 함수가 구분되어 있다.](../assets/portal/05-agent-tools.png)

**화면 따라 읽기:** **Tools**의 **File search** 카드에서 자신의 store와 검색 설정을 확인합니다. 그 아래 `get_stock`·`prepare_purchase_request`는 L06에서 설명할 함수이며 파일 검색 자체의 기능이 아닙니다. 인덱싱이 완료되면 아래 질문을 보내고 실제 인용을 원문과 대조합니다.

### 3. 정답·교차 문서·모름을 차례로 실험하기

```prompt
노트북 가격 상한과 정기 교체 주기를 알려줘. 문서명과 절을 제시해줘.
```

기대: **150만 원, 부가세 포함, 36개월, procurement-policy.md 2절**.

```prompt
노트북 2대를 총액 290만 원에 사려 합니다.
누구의 승인이 필요하고, 사전 승인 없이 구매하면 비용 처리할 수 있나요?
```

기대: **팀장 + 구매 담당자** 승인과, 사전 승인 없는 구매의 **원칙적 비용 처리 불가/서면 예외 검토**. 두 문서 근거를 구분합니다.

```prompt
독일 지사의 구매 규정도 알려줘.
```

기대: 제공 문서에서 확인할 수 없다고 답합니다. 출처를 만들어내면 실패입니다.

### 4. citation을 실제로 열어보기

대답에 파일 이름이 적혀 있는 것만으로 성공이 아닙니다. portal의 인용이나 SDK의 `annotations`가 **실제 업로드 파일/검색 결과**를 가리키는지 확인합니다. 근거에 없는 숫자를 섞지 않았는지도 점검합니다.

**포털에서 세 답을 확인했다면 아래 SDK는 건너뜁니다.** L06의 통합 명령은 필요한 파일을 스스로 준비하므로 `rag --live`가 선행 조건이 아닙니다.

<details class="optional-path" markdown="1">
<summary>선택: 파일·보관소·에이전트를 새로 만드는 SDK 경로</summary>

```bash
python samples/workshop.py rag
python samples/workshop.py rag --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `rag` | 사용할 합성 정책과 RAG 실행 계획을 표시합니다. `--live`가 없어 업로드하지 않습니다. | 로컬 계획 확인만 수행합니다. |
| 2. `rag --live` | 파일 업로드 → vector store 연결 → 최대 180초 인덱싱 대기 → 새 agent 생성 → 질문을 실제 수행합니다. | 모델·File search·파일 보관 비용 가능. 답변의 citation과 receipt의 파일/store ID를 대조합니다. 포털 객체를 재사용하는 명령은 아닙니다. |

</div>

실행 파일은 업로드 → vector store 파일 연결 → 최대 180초 인덱싱 대기 → agent 생성 → **기본 상한 질문 1건**을 진행합니다. 위 세 질문을 자동 수행하지 않습니다. 180초 안에 끝나지 않으면 완료로 가장하지 않고 중단합니다. receipt로 남은 파일과 상태를 확인하세요.

세 질문을 마저 확인하려면 새 agent 이름·버전을 receipt에서 찾고 포털 **Build → Agents**에서 그 대상을 엽니다. 질문별 추가 비용 범위를 확인해 3단계 질문을 수행합니다. Chat을 사용할 수 없다면 **기본 질문의 검색·인용 확인 / 세 질문 비교 미실행**으로 기록하고, `rag --live`를 질문마다 반복해 자원을 재생성하지 않습니다.

</details>

### 5. 검색 실패를 분해하기

![질문, 검색, 근거, 답변, 평가, 개선으로 이어지는 학습 루프](../assets/learning-loop.svg)

| 현상 | 먼저 볼 계층 |
| --- | --- |
| 관련 문서가 검색되지 않음 | 인덱싱·chunk·검색 설정 |
| 문서는 맞는데 답이 틀림 | instructions·질문·모델 |
| 답은 맞지만 출처가 없음 | citation 처리·화면 렌더링 |
| 다른 사용자의 자료가 보임 | 데이터 권한·검색 필터·호출자 ID |

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 업로드·인덱싱·검색이 SDK에서 이어지는 방식 — 읽기용</summary>

### 포털 동작과 실제 File search 코드

포털에서는 **store 생성·파일 업로드 → 인덱싱 완료 → File search 연결 → 질문** 순서입니다. 아래는 `create_lab_agent()`와 `run_turn()`의 호출을 연결한 학습용 발췌입니다. `project`·`client`는 L03의 연결 객체, `receipt`는 SDK 실행이 먼저 만드는 소유 기록입니다. 블록을 따로 실행해 자원을 중복 생성하지 않습니다.

```python
from pathlib import Path
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
from lab_profile import DATA

instructions = Path("data/prompts/agent-v2.txt").read_text(encoding="utf-8")
store = client.vector_stores.create(
    name=receipt.data["run_id"],
    expires_after={"anchor": "last_active_at", "days": 1},
)
receipt.add("vector_store", store.id)
for path in sorted((DATA / "policies").glob("*.md")):
    with path.open("rb") as handle:
        uploaded = client.files.create(file=handle, purpose="assistants")
    receipt.add("file", uploaded.id)
    index_file(client, uploaded.id, store.id)

file_search = FileSearchTool(vector_store_ids=[store.id], max_num_results=4)
agent = project.agents.create_version(
    agent_name=receipt.data["run_id"],
    definition=PromptAgentDefinition(
        model=deployment_name,
        instructions=instructions,
        tools=[file_search],
    ),
    description="Synthetic workshop agent; never submit real orders.",
)
receipt.add("agent", agent.name, version=agent.version)
conversation = client.conversations.create()
receipt.add("conversation", conversation.id)
response = client.responses.create(
    conversation=conversation.id,
    input=question,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference", "version": agent.version}},
    include=["file_search_call.results"],
    max_output_tokens=2048,
)
```

| 포털 조작 | 코드에서 실제로 일어나는 일 |
| --- | --- |
| 정책 파일 업로드·인덱싱 상태 확인 | `client.files.create(...)` 후 `index_file(...)` 완료 확인 |
| File search와 store 연결 | `FileSearchTool(vector_store_ids=[store.id], ...)` |
| agent 설정 저장 | `project.agents.create_version(...PromptAgentDefinition(...))` |
| Chat에 질문 전송·citation 확인 | `responses.create(...)`와 `include=["file_search_call.results"]` |

이 코드는 SDK 경로의 원본 흐름을 읽기 위한 것입니다. 실제 SDK 실행은 별도 store·agent·파일을 만들므로 receipt가 있는 `workshop.py rag --live` 경로를 선택하고 포털과 중복 실행하지 마세요.

</details>

## 성공 기준

정답 질문 2개에 실제 근거가 있고, 문서에 없는 질문은 유보합니다. 응답의 사실을 원문과 대조했으며 인덱싱 완료 상태를 확인했습니다.

## 막혔을 때

“문서를 다시 올려보자”부터 시작하지 않습니다. 연결한 vector store ID, 인덱싱 실패 사유, 지원 파일 형식, 모델/tool 지원, 올바른 agent 버전을 확인합니다. 실제 파일에 이미지로만 들어 있는 표라면 검색 가능한 텍스트가 있는지 먼저 확인하고, File search만으로 읽었다고 가정하지 않습니다.

## 정리

다음 실습을 위해 지식 연결을 유지합니다. SDK store의 **마지막 활동 후 1일** 만료는 업로드 파일까지 삭제하지 않습니다. L19에서 남은 자원을 확인하고 승인된 대상만 삭제하거나 보존 기한을 기록합니다.

<details markdown="1">
<summary>File search와 Microsoft Foundry IQ는 언제 나누나요?</summary>

파일 몇 개로 빠르게 검증하려면 File search. 직접 인덱스·hybrid 검색·필터를 제어하려면 Microsoft Azure AI Search. 여러 지식 소스와 agentic retrieval을 공유하려면 Microsoft Foundry IQ를 검토합니다. 어느 경로도 연결만으로 사용자별 문서 권한이 자동 완성되지는 않습니다.

</details>

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 정책 agent 이름·저장한 버전·store와 세 질문의 답/실제 인용. 이 **정책 agent는 L09에서 다시** 사용합니다.

**다음:** [L06 재고와 초안](#l06). L06 통합 명령은 별도 agent를 만들므로 지금 agent에 함수를 추가하거나 SDK 업로드를 반복하지 않습니다.

</div>
