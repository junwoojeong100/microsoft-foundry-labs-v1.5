> **완성할 결과:** 기존 자원을 유지하면서 새 Foundry로 이동할 항목과 검증 순서를 구분한 마이그레이션 표.

<div class="lab-brief" markdown="1">

**진행 방식:** 로컬 계약 변환 + 선택 설계 · 기존 Classic 환경이 없어도 됩니다.

**먼저 할 일:** 합성 요청 변환의 세 오류를 수정하고, 정의·사용자 상태·운영 상태의 차이를 설명합니다.

**확인할 결과:** 이전 대상·검사·복구·보존 담당자 표를 만듭니다. 실제 자원 이전이나 삭제는 이 설계에 포함되지 않습니다.

</div>

## 목표

**브랜드명 변경, 포털 전환, 리소스 업그레이드, SDK/API 마이그레이션은 서로 다른 작업**입니다.

## 개념과 실습 지도

**경험할 기능:** 새 API의 입력 변환을 고치고 기존 서비스의 이전 계획을 작성합니다.

**무엇이며 왜 중요한가요?** Classic은 이전 Foundry 환경입니다. Threads/Runs에서 Conversations/Responses로 옮길 때는 이름뿐 아니라 대화·함수 결과·권한·보존 방식도 바뀔 수 있습니다.

**어떻게 사용하나요?** 합성 요청의 세 오류를 고칩니다. 이후 옮길 설정·사용자 데이터·운영 상태와 검증·복구 방법을 표로 정리합니다.

**어디서 실행하나요?** 내 PC에서 진행하며 Classic 계정이 필요 없습니다. [SDK 의존성](../requirements.txt)·[Responses 예제](../samples/workshop.py)·[배포 설정](../azure.yaml)은 비교용입니다. 실제 이관·삭제는 수행하지 않습니다.

## 준비

기존 시스템이 있으면 승인된 범위에서 읽기 전용으로 목록화합니다. 없으면 아래 **가상 Contoso Classic 사례**로 계획을 작성합니다. 실습을 위해 Classic 자원을 새로 만들 필요가 없습니다. 이 장은 기존 자원을 자동 업그레이드하거나 데이터를 옮기지 않습니다.

## 실행

### 0. 직접 고치기: 새 API의 ID와 출력 계약

<div class="practice-block" markdown="1">

**직접 해보기:** Classic 환경을 만들지 않고 새 Responses 요청의 작은 조각을 변환합니다. 기존 Threads/Runs의 `tool_call_id`와 달리, Responses의 출력 item `id`와 함수 결과에 붙일 `call_id`는 별개입니다. 모든 ID는 합성입니다.

```bash
python samples/prepare_practice.py migration --output practice/migration
python -m unittest discover -s practice/migration -p "test_exercise.py" -v
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `prepare_practice.py migration` | 변환 함수와 고정 계약 테스트를 새 폴더에 복사합니다. | 로컬 파일 생성만 수행. 구 SDK 설치·Azure 호출·실제 이관 없음. |
| 2. `unittest discover` | 대화 ID, 함수 상관 ID, JSON 문자열, 출력 항목 개수를 확인합니다. | 처음에는 **4개 중 3개 실패**합니다. 나쁜 변환을 발견한 정상적인 검사 결과입니다. |

</div>

| 입력·출력 | 합성 값 | 유지해야 할 의미 |
| --- | --- | --- |
| 새 대화 | `conv_new_demo` | 이후 함수 결과를 돌려줄 같은 conversation |
| 함수 요청 item의 `id` | `fc_item_demo` | 응답 안의 item 식별자 |
| 함수 요청의 `call_id` | `call_demo_1` | 함수 결과와 요청을 연결할 식별자 |
| 실제 함수 결과 | `{"sku":"NB-14","stock":8}` | `output`에는 이 객체의 JSON **문자열**을 전달 |

**한 가지 바꾸기:** `practice/migration/exercise.py`의 변환 계약을 고칩니다. 대화에는 입력받은 `conversation_id`, 함수 상관관계에는 `function_call["call_id"]`, 결과에는 `json.dumps`를 사용합니다. 하나씩 고친 뒤 같은 테스트를 실행하여 어떤 실패가 사라지는지 확인합니다.

<details markdown="1">
<summary>완성된 변환 조각 — 새 API 요청의 일부이며 전체 이관기가 아님</summary>

<!-- solution:migration -->
```python
import json

def continuation(conversation_id: str, function_call: dict, result: dict) -> dict:
    return {
        "conversation": conversation_id,
        "input": [{
            "type": "function_call_output",
            "call_id": function_call["call_id"],
            "output": json.dumps(result, ensure_ascii=False),
        }],
    }
```

</details>

**결과 설명하기:** 네 테스트가 모두 통과하면 각 필드가 왜 필요한지 설명하고 아래 마이그레이션 표의 **정의 / 사용자 상태 / 운영 상태** 중 어디에 속하는지 적습니다. 실제 호출에서는 새 서비스가 반환한 ID와 같은 agent/version 바인딩을 사용합니다. 이 과제는 과거 Thread/Run ID를 재사용하거나 사용자 이력을 실제로 옮기지 않습니다. 전체 호출·도구 루프는 동봉 `samples/workshop.py`의 `run_turn`과 비교합니다.

</div>

### 1. 현재 사용 중인 것을 찾기

| 과거/기존 | 새 경로 | 주의 |
| --- | --- | --- |
| Azure AI Studio / Azure AI Foundry | Microsoft Foundry | 이름 변경만으로 API가 바뀌지 않음 |
| hub 기반 프로젝트 | Foundry resource 아래 project | 일부 Classic 경험은 별도 유지 |
| Assistants / Threads / Runs | Agent Versions / Conversations / Responses | 호출·상태·tool loop 변경 |
| `azure-ai-projects` 1.x | 2.x project client | import만 바꾸는 작업이 아님 |
| 여러 추론 endpoint | 프로젝트/OpenAI-compatible surface | 공급자·API별 지원 확인 |
| Azure AI User 등 역할명 | Foundry User 등 | 역할 ID·scope·실제 permissions 확인 |

standalone Azure OpenAI 자원과 Classic hub 기반 프로젝트는 새 포털의 모든 경로에 바로 들어가는 것이 아닙니다. 공식 upgrade/migration 절차를 따릅니다.

Azure Government 등 sovereign cloud는 endpoint·인증 audience·서비스/모델 지원 범위가 별도입니다. public cloud용 이 가이드의 환경 파일을 주소만 일부 바꿔 재사용하지 말고 해당 클라우드의 공식 지원 문서를 기준으로 이전 계획을 세웁니다.

### 2. 세 상태를 분리해서 이전 계획 만들기

**정의:** instructions, model, tools, connections.  
**사용자 상태:** conversations, memory, 파일, vector stores.  
**운영 상태:** endpoint, identity, 권한, monitoring, 평가 결과, 게시 채널.

API migration 도구가 정의를 옮겼다고 사용자 대화나 업무 승인 상태까지 모두 이전됐다고 가정하지 않습니다.

**완성 예 — 가상의 기존 구매 도우미이며 실제 이관 결과가 아닙니다.**

| 구분·기존 항목 | 새 경로의 결정 | 확인할 것 / 실패하면 |
| --- | --- | --- |
| 정의: instructions·함수 schema | 현재 v2와 L06 계약에 각각 대응. 이름만 치환하지 않음 | 수량 1~10·미주문 경계 비교. 다르면 함수/계약 수정 후 재검토 |
| 지식: 정책 파일 3개·vector store | 승인 후 새 환경에 원문을 올리고 새 file/store ID 기록 | L05의 실제 citation이 새 파일·같은 절을 가리키는지. 실패 시 파일→store→agent 연결 확인 |
| 사용자 상태: Thread/Run | 새 conversation으로 시험. 기존 ID를 그대로 사용하지 않음 | 새 대화에서 필요한 맥락만 전달되는지. 사용자 이력 이관은 별도 범위/보존 계획 |
| 운영: identity·endpoint·모델 | 새 환경별 바인딩과 최소 권한을 명시 | L03 응답과 L10 trace 연결. 403/404는 권한·주소·버전부터 분리 |
| 게시·복구 | 기존 endpoint는 유지하고 테스트 사용자만 새 경로 사용 | L22 이전 설정 묶음으로 돌아갈 수 있는지. 기존 자원 삭제는 전환과 분리 |

자신의 표에는 **원본 위치·담당자·보존 결정·검증 파일/ID·미해결 항목**을 덧붙입니다. 예시 결정을 실제 환경에 적용하기 전에 현재 제품의 migration 지원 범위를 확인합니다.

### 3. 새 환경에서 회귀 확인하기

실제 이관을 승인받은 경우에만 새 비운영 환경에서 같은 합성 입력을 비교합니다. 기본 설계 과제는 아래 표에 사용할 입력과 근거 위치를 적는 것으로 진행합니다.

| 확인할 것 | 어떻게 판단하나요? | 실패하면 다음 행동 |
| --- | --- | --- |
| L03 모델 호출 | 완료된 응답, 실제 배포 이름·response ID | endpoint/token audience·모델 지원 확인 |
| L05 정책 질문 | 상한 150만 원·부가세 포함·36개월과 실제 새 citation | 원문/인덱싱/store 바인딩부터 확인 |
| L06 정상·실패 입력 | NB-14 2대는 총액 290만 원·미주문; 품절/음수 수량은 오류 | schema·dispatcher·도구 결과 전달 순서 확인 |
| L08 지침 비교 | 동일 언어·문맥·모델·질문·기준의 실제 차이 | 기존 비교와 조건이 다르면 직접 우열 주장 금지. 기존 결과 덮어쓰기·봉인 holdout 재사용 금지 |
| L10 추적 | 새 응답과 새 환경의 trace 연결 | 이전 환경 로그를 대신 붙이지 않고 연결·시각·권한 확인 |

L08의 도구 없는 비교는 위의 통합 함수·검색 시험을 대체하지 않습니다. endpoint·schema·재시도·저장/보존 정책 차이는 각각 기록하며, 실행하지 않은 검사는 빈 성공 표시 대신 미실행으로 남깁니다.

### 4. 종료 예정 기능을 먼저 제거하기

포털 Workflows의 **2026-12-01 종료 예정**을 일정에 반영하고 신규 의존성을 만들지 않습니다. 필요한 orchestration은 Microsoft Agent Framework 등 현재 지원 경로로 이전하고, checkpoint·사람 승인·실패 재개를 다시 검증합니다.

AI Search agentic retrieval은 stable `2026-04-01`와 최신 preview 간 기능·payload 차이가 있습니다. Knowledge source·client 이름·pagination·Work IQ 인증·response 처리 변경을 공식 migration 표와 대조합니다.

### 5. 단계적 전환과 복구 기준 정의하기

테스트 사용자 → 제한된 traffic → 승인된 확대 순서로 진행합니다. **후보가 citation 없이 정답만 말하거나 주문 완료를 가장한다면 확대를 보류**하는 것이 이 사례의 결정입니다. 먼저 새 경로의 실패 원본을 보존하고, 담당자가 승인된 이전 endpoint/버전·설정을 선택합니다. 상태가 호환되는지 확인한 뒤 실제 복구 호출을 별도 검증합니다.

표의 품질·권한·복구 항목 중 하나라도 미확인이면 “이관 완료”가 아니라 **전환 보류 / 필요한 다음 확인**을 적습니다. 기존 endpoint나 사용자 상태를 성급히 삭제하지 않습니다.

## 성공 기준

합성 변환 과제의 세 오류를 설명하고, 테스트를 바꾸지 않은 수정으로 4개 테스트가 통과합니다. 이는 로컬 계약 변환 확인이지 실제 서비스 이관 완료가 아닙니다.
이전 대상, 유지할 Classic 기능, 사용자 상태의 처리, 종료 일정, 평가 결과, rollback 방법이 있습니다. “새 포털에서 보인다”만으로 마이그레이션 완료를 판정하지 않습니다.

## 막혔을 때

브랜드가 같아도 오래된 문서 URL/SDK 예제의 resource model은 다를 수 있습니다. `foundry-classic`, `azure-ai-projects 1.x`, Threads/Runs 여부를 먼저 확인합니다.

## 정리

새 경로가 실제 사용과 평가에서 통과하고 복구 기간이 끝난 후, 담당자가 기존 자원의 보존·삭제를 승인합니다.
