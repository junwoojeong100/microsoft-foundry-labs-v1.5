> **완성할 결과:** 역할과 한계가 명확한 Prompt Agent. 지식·도구를 추가하기 전의 기준 버전입니다.

## 목표

Prompt Agent는 **모델 + instructions + tools**로 선언하는 관리형 agent입니다. 별도의 서버나 컨테이너를 직접 운영하지 않습니다. Hosted Agent와의 차이는 L14에서 다룹니다.

## 개념과 실습 지도

**경험할 기능:** Prompt Agent의 instructions·모델·버전·conversation입니다.

**무엇이며 왜 중요한가요?** Prompt Agent는 역할과 규칙을 서버에 정의해 여러 요청에서 재사용하는 관리형 실행 단위입니다. Instructions는 행동의 방향을 주지만 비공개 회사 지식이나 실행 권한을 자동으로 주지 않습니다. “재고 도우미”라는 이름을 붙여도 재고 도구가 없으면 조회할 수 없습니다. 이 장에서 일부러 지식·도구 없이 시작하는 이유는, 다음 장에서 추가한 기능이 실제로 어떤 차이를 만드는지 비교하기 위해서입니다.

**어떻게 사용하나요?** 포털에서 모델과 instructions를 지정하고, 없는 지식·없는 도구·같은 대화·새 대화를 차례로 시험합니다. Instructions를 수정한 버전과 대화 맥락을 따로 기록하세요. 모델이 그럴듯한 문장을 만들었는지가 아니라 제공한 능력의 한계를 지켰는지가 관찰 대상입니다.

**어디서 실행하나요?** 기본은 포털, SDK는 선택 비교입니다. [지시문 원본](../data/prompts/agent-v4.txt)을 먼저 읽고 [SDK 구현](../samples/workshop.py)과 비교하세요. 두 경로는 별도 agent를 만들므로 같은 객체가 자동 동기화되는 것이 아닙니다.

## 준비

프로젝트 `Foundry User`, 호출 가능한 모델, `data/prompts/agent-v4.txt`가 필요합니다.

## 실행

### 1. 포털에서 만들기

**Build → Agents → New agent → Build an agent**를 선택합니다. 촬영 시점의 **New agent**는 Build/Code/template 등의 경로를 고르는 메뉴입니다. 이름은 `contoso-procurement`, 모드는 **Text**, 모델은 L02의 배포로 지정합니다. 다른 UI 버전에서는 바로 **Build an agent** 버튼이 표시될 수 있습니다.

Instructions에 `data/prompts/agent-v4.txt`의 내용을 붙여 넣습니다. 아직 File search와 함수 도구를 붙이지 않았으므로 **없는 도구를 사용했다고 주장하면 안 됩니다.**

![실제 Contoso Prompt Agent의 Playground. 왼쪽에 Model·Instructions·Tools, 오른쪽에 Chat/YAML과 메시지 입력, 위쪽에 버전·Save·Publish·Traces 탭이 있다.](../assets/portal/04-prompt-playground.png)

**화면 따라 읽기:** 왼쪽 **Model**에서 배포 이름, **Instructions**에서 지시문을 확인하고 오른쪽 **Chat**에 테스트 질문을 넣습니다. 위쪽 **Version**은 설정 버전, **New chat**은 대화 맥락을 구분하는 기능입니다. **Save**와 **Send**는 각각 설정 변경과 유료 요청이므로 목적을 확인한 후 누르세요.

촬영은 **이미 지식·함수가 연결된 기존 실습 agent를 읽기 전용으로 관찰**한 것입니다. L04에서 새로 만든 agent에 화면처럼 File search·함수가 아직 없어도 정상입니다. 촬영 과정에서 메시지를 전송하거나 지시문·버전을 저장하지 않았습니다.

### 2. 기준 질문으로 한계 확인하기

```text
우리 회사 표준 노트북의 가격 상한은 얼마인가요?
```

정책 파일이 없는 상태에서 150만 원을 알고 있는 것처럼 답하면 안 됩니다. 제공된 규정이나 지식 연결이 필요하다고 답하는 것이 이 단계의 정상 동작입니다.

```text
NB-14의 실시간 재고를 확인해줘.
```

도구가 없으므로 조회 성공을 주장하면 실패입니다. **“모른다”는 답도 올바른 행동**입니다.

### 3. 대화 상태 실험하기

같은 대화에서 다음 두 입력을 순서대로 보냅니다.

```text
이번 대화에서는 모니터 구매를 검토하고 있어요.
```

```text
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

instruction을 수정하고 저장한 뒤 새 버전이 생성되는지 확인합니다. “최신 버전”이 곧 “운영에 승인된 버전”은 아닙니다.

### 5. 선택: SDK로 같은 개념 확인하기

```bash
python samples/workshop.py agent
python samples/workshop.py agent --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — 포털 과제를 마친 뒤 선택적으로 비교합니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `agent` | 생성·호출할 Prompt Agent의 실행 계획을 출력합니다. 기본 지시 파일은 `data/prompts/agent-v4.txt`입니다. | Azure 요청 없음. 지시문이 설명한 기능과 실제 연결할 도구를 먼저 구분합니다. |
| 2. `agent --live` | 고유 `contoso-lab-...` agent와 대화를 만들고 실제 모델 응답을 받습니다. 포털에서 만든 agent를 수정하지 않습니다. | 추론·서비스 비용과 새 실습 객체가 생깁니다. 출력된 receipt 경로는 L12 정리용으로 보관합니다. |

</div>

SDK 샘플은 충돌을 피하기 위해 `contoso-lab-...`라는 **새로운 agent**를 만듭니다. 포털에서 만든 `contoso-procurement`를 수정하지 않습니다. 생성 ID는 `results/contoso-lab-....json`에 저장됩니다.

## 성공 기준

역할·근거·없는 정보 처리·도구 실패 처리·금지 행동이 instructions에 있습니다. 같은 대화의 맥락은 유지하고, 없는 지식이나 도구의 성공은 가장하지 않습니다.

## 막혔을 때

이전 대화의 문맥이 instruction 변경을 가릴 수 있습니다. 새 버전을 선택한 뒤 **새 conversation**에서도 확인하세요. SDK 1.x의 Threads/Runs 코드를 2.x 샘플에 섞지 않습니다.

## 정리

포털 agent는 다음 실습에서 재사용합니다. SDK로 만든 별도 agent의 receipt는 L12에서 정리합니다.
