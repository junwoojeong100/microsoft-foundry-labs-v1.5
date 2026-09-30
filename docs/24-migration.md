> **완성할 결과:** 기존 자원을 유지하면서 새 Foundry로 이동할 항목과 검증 순서를 구분한 마이그레이션 표.

## 목표

**브랜드명 변경, 포털 전환, 리소스 업그레이드, SDK/API 마이그레이션은 서로 다른 작업**입니다.

## 개념과 실습 지도

**경험할 기능:** Classic/신규 Foundry의 리소스·API·상태·운영 차이를 분류하고 이전 계획을 작성합니다.

**무엇이며 왜 중요한가요?** 포털 이름이 바뀌어도 기존 endpoint가 자동으로 새 API가 되는 것은 아닙니다. Threads/Runs 기반 코드를 Conversations/Responses로 옮길 때는 호출 모양뿐 아니라 도구 실행 루프·저장 상태·권한·재시도도 다시 확인해야 합니다. 화면에 agent가 보이는 것만으로 사용자 대화나 삭제·보존 정책까지 이전됐다고 결론내릴 수 없습니다.

**어떻게 사용하나요?** 기존 시스템을 변경하지 않고 정의·사용자 상태·운영 상태를 목록화합니다. 새 비운영 환경에 작은 합성 경로를 구현하고 L03/L05/L06/L08/L10의 같은 검사를 적용합니다. 품질·권한·복구 조건을 통과한 뒤에만 제한된 사용자부터 전환합니다.

**어디서 실행하나요?** 이 장의 기본 결과는 마이그레이션 표이며 자동 변경 CLI는 없습니다. [현재 SDK 의존성](../requirements.txt), [Responses/도구 루프 예제](../samples/workshop.py), [배포 설정](../azure.yaml)을 기존 시스템과 비교하세요. 보존·삭제는 최종 담당자의 별도 승인입니다.

## 준비

기존 시스템을 읽기 전용으로 목록화합니다. 이 가이드는 기존 Azure OpenAI/Classic 자원을 자동 업그레이드하거나 데이터를 옮기지 않습니다.

## 실행

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

### 3. 새 환경에서 회귀 확인하기

동일 합성 데이터로 L03 모델 호출, L05 citation, L06 함수, L08 평가, L10 trace를 다시 수행합니다. endpoint/token audience, response/tool schema, retry, 저장/보존 정책 차이를 기록합니다.

### 4. 종료 예정 기능을 먼저 제거하기

포털 Workflows의 **2026-12-01 종료 예정**을 일정에 반영하고 신규 의존성을 만들지 않습니다. 필요한 orchestration은 Microsoft Agent Framework 등 현재 지원 경로로 이전하고, checkpoint·사람 승인·실패 재개를 다시 검증합니다.

AI Search agentic retrieval은 stable `2026-04-01`와 최신 preview 간 기능·payload 차이가 있습니다. Knowledge source·client 이름·pagination·Work IQ 인증·response 처리 변경을 공식 migration 표와 대조합니다.

### 5. 단계적 전환과 복구 기준 정의하기

기존 endpoint를 성급히 삭제하지 않습니다. 테스트 사용자 → 제한된 traffic → 승인된 확대 순서로 진행하고, 품질·안전·지연·비용 기준을 넘으면 되돌릴 경로를 준비합니다.

## 성공 기준

이전 대상, 유지할 Classic 기능, 사용자 상태의 처리, 종료 일정, 평가 결과, rollback 방법이 있습니다. “새 포털에서 보인다”만으로 마이그레이션 완료를 판정하지 않습니다.

## 막혔을 때

브랜드가 같아도 오래된 문서 URL/SDK 예제의 resource model은 다를 수 있습니다. `foundry-classic`, `azure-ai-projects 1.x`, Threads/Runs 여부를 먼저 확인합니다.

## 정리

새 경로가 실제 사용과 평가에서 통과하고 복구 기간이 끝난 후, 담당자가 기존 자원의 보존·삭제를 승인합니다.
