> **완성할 결과:** 역할과 한계가 명확한 Prompt Agent. 지식·도구를 추가하기 전의 기준 버전입니다.

## 목표

Prompt Agent는 **모델 + instructions + tools**로 선언하는 관리형 agent입니다. 별도의 서버나 컨테이너를 직접 운영하지 않습니다. Hosted Agent와의 차이는 L14에서 다룹니다.

## 준비

프로젝트 `Foundry User`, 호출 가능한 모델, `data/prompts/agent-v4.txt`가 필요합니다.

## 실행

### 1. 포털에서 만들기

**Build → Agents → Build an agent** 또는 현재 포털의 동등한 생성 동작을 선택합니다. 이름은 `contoso-procurement`, 모드는 **Text**, 모델은 L02의 배포로 지정합니다.

Instructions에 `data/prompts/agent-v4.txt`의 내용을 붙여 넣습니다. 아직 File search와 함수 도구를 붙이지 않았으므로 **없는 도구를 사용했다고 주장하면 안 됩니다.**

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

SDK 샘플은 충돌을 피하기 위해 `contoso-lab-...`라는 **새로운 agent**를 만듭니다. 포털에서 만든 `contoso-procurement`를 수정하지 않습니다. 생성 ID는 `results/contoso-lab-....json`에 저장됩니다.

## 성공 기준

역할·근거·없는 정보 처리·도구 실패 처리·금지 행동이 instructions에 있습니다. 같은 대화의 맥락은 유지하고, 없는 지식이나 도구의 성공은 가장하지 않습니다.

## 막혔을 때

이전 대화의 문맥이 instruction 변경을 가릴 수 있습니다. 새 버전을 선택한 뒤 **새 conversation**에서도 확인하세요. SDK 1.x의 Threads/Runs 코드를 2.x 샘플에 섞지 않습니다.

## 정리

포털 agent는 다음 실습에서 재사용합니다. SDK로 만든 별도 agent의 receipt는 L12에서 정리합니다.
