> **완성할 결과:** 내가 작성한 코드를 로컬에서 실행하고, Foundry가 호스팅하는 같은 agent를 호출합니다.

## 목표

Prompt Agent의 instructions와 서버 도구만으로 충분하면 그대로 둡니다. **사용자 정의 코드·복잡한 실행 흐름·프레임워크·의존성이 필요할 때 Hosted Agent**를 선택합니다.

## 준비

별도의 비운영 실습 폴더, Azure Developer CLI와 `microsoft.foundry` 확장, 공식 quickstart에서 요구하는 권한이 필요합니다. 소스 배포와 컨테이너 배포의 권한·비용·빌드 경로가 다릅니다.

**이 모듈의 provision/deploy는 실제 Azure 변경과 비용을 발생시킵니다.** 준비가 안 되면 생성 파일 검토까지만 진행하고 배포 미실행으로 기록합니다.

## 실행

### 1. 공식 최신 샘플로 빈 프로젝트 시작하기

[Hosted Agent quickstart](https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent?pivots=azd)의 **Azure Developer CLI** 탭을 엽니다. 별도 빈 폴더에서 문서의 Step 1 초기화 명령을 사용합니다.

선택값을 다음과 같이 정합니다.

| 항목 | 실습 선택 |
| --- | --- |
| 배포 모드 | 먼저 code deployment |
| 샘플 | Agent Framework basic Responses |
| 프로젝트 | 승인된 비운영 프로젝트 재사용 우선 |
| 모델 | L02의 지원 모델, Batch가 아닌 online 배포 |
| 이름 | 기존 agent와 겹치지 않는 실습 이름 |

현재 문서의 명령을 사용하는 이유는 확장·템플릿·startup 설정이 빠르게 바뀌기 때문입니다. 자동 생성된 파일을 확인하지 않고 바로 배포하지 않습니다.

### 2. 생성된 파일 읽기

`azure.yaml`, agent source, dependency manifest, 생성된 infrastructure가 담당하는 역할을 확인합니다.

| 파일/값 | 확인 |
| --- | --- |
| `azure.yaml` | 올바른 agent service와 프로젝트 경로 |
| startup command | 실제 앱을 시작하는 명령 |
| runtime protocol | 호출 클라이언트와 맞는 Responses/Invocations 등 |
| 모델/프로젝트 설정 | 기존 실습 환경과 일치 |
| dependency versions | 검증 가능한 버전 조합 |
| deployment outputs | endpoint·agent name/version을 실제 출력에서 취득 |

이 가이드의 기본 SDK 프로젝트와 생성된 hosted 프로젝트를 같은 폴더에 겹치지 않습니다.

### 3. 로컬 → 배포 → 같은 질문 순서로 진행하기

공식 quickstart의 **Provision → Run locally → Deploy → Invoke**를 순서대로 수행합니다. 각 단계에서 subscription·resource group·region을 다시 확인합니다. provision은 필요 자원을 만들 수 있으므로 예상 자원 목록을 먼저 검토합니다.

로컬 실행에서 다음 질문을 보내고, 배포 후 같은 질문을 반복합니다.

```text
실습용 구매 안내를 세 문장으로 작성해줘.
실제 주문이나 승인을 수행하지 않았다는 사실을 명시해줘.
```

**프로세스가 시작됨 → endpoint가 응답함 → 올바른 결과를 반환함**은 서로 다른 단계입니다. 로컬 inspector와 배포 endpoint에서 각각 확인합니다.

### 4. 구매 도구를 서버로 옮기기

L06의 검증된 읽기/초안 함수와 schema를 hosted 앱의 도구 등록 지점에 추가합니다. 주문 API는 추가하지 않습니다. 환경별 credential은 코드가 아니라 배포 identity/connection을 사용합니다.

이제 함수 실행은 사용자의 로컬 터미널이 아니라 hosted 앱 안에서 일어납니다. 서버 평가와 Teams 게시가 필요한 경우 이 실행 책임 차이가 중요합니다.

### 5. 개발 표면을 목적에 맞게 고르기

| 도구 | 활용 |
| --- | --- |
| Foundry Toolkit for VS Code | 프로젝트·모델·도구, inspector, 로컬 tracing |
| Foundry Agent Canvas | 구성과 실행을 시각적으로 탐색 |
| Foundry Skill / MCP | coding agent가 scaffold·관리 작업을 보조 |
| SDK / REST | 자동화 가능한 명시적 앱 코드 |
| azd | 환경 설정·프로비저닝·배포의 재현성 |

도구가 만든 코드와 권한 요청도 사람이 검토합니다. Canvas는 종료 예정인 포털 Workflows와 같은 기능이 아닙니다.

## 성공 기준

같은 질문이 로컬과 배포 환경에서 모두 기대대로 동작하고, 정확한 agent version과 trace/log를 확인했습니다. resource provisioning만 성공한 것을 agent 성공으로 표시하지 않습니다.

## 막혔을 때

protocol 불일치, startup command, 누락 dependency, 컨테이너 registry 접근, managed identity 권한을 순서대로 봅니다. code deployment와 container deployment를 서로의 체크리스트로 진단하지 않습니다.

## 정리

실행 중인 hosted 버전·세션·빌드 자원·registry·storage·로그의 비용을 확인합니다. 공유 프로젝트 전체를 삭제하지 않습니다.
