> **완성할 결과:** “도구 정의”, “인증”, “도구 묶음”, “사용 승인”을 구분하고, 읽기 전용 도구 연결을 검증합니다.

## 목표

**MCP는 도구 연결 프로토콜, OpenAPI는 HTTP API 설명, Toolbox는 도구를 관리·재사용하는 Foundry 자원**입니다. 서로 경쟁하는 세 가지 agent 유형이 아닙니다.

## 준비

기본 연습에는 Python과 터미널 두 개가 필요합니다. 클라우드 Toolbox 실습에는 Foundry User, 사용할 도구의 권한, 해당 기능을 지원하는 지역이 필요합니다. Toolkit 경로를 쓰면 Microsoft Foundry Toolkit for VS Code가 필요합니다.

## 실행

### 1. 로컬 OpenAPI 계약 확인하기

첫 번째 터미널:

```bash
python samples/inventory_api.py
```

두 번째 터미널:

```bash
curl --fail http://127.0.0.1:8766/health
curl --fail http://127.0.0.1:8766/inventory/NB-14
```

`samples/inventory.openapi.json`의 `operationId=get_stock`, required parameter, response schema를 실제 응답과 비교합니다.

**이 서버는 loopback 전용이며 인증이 없습니다. Foundry 클라우드에서 접근할 수 없습니다.** 외부에 터널로 노출하지 마세요. cloud OpenAPI 실습은 조직에서 승인한 인증·HTTPS·네트워크를 갖춘 테스트 API로 따로 진행합니다.

### 2. 도구 유형을 고르기

| 이미 가진 것 | 선택 | 주의 |
| --- | --- | --- |
| 애플리케이션 안의 Python 함수 | Function calling | 클라이언트 실행; Toolbox에 넣는 도구가 아님 |
| 승인된 REST API | OpenAPI | 정확한 operationId, 인증, 입력 검증 |
| MCP endpoint | MCP tool | 서버 신뢰, allowed tools, 승인 정책 |
| 여러 agent가 공유할 도구 | Toolbox | 버전·권한·정책을 중앙 관리 |
| 다른 agent의 기능 | A2A | L15의 agent 간 계약 |

### 3. 읽기 전용 MCP 연결 실습

공식 MCP 도구 문서의 **Connect → Discover → Invoke** 순서로 진행합니다. portal의 도구 추가 경험 또는 Toolkit에서 MCP 연결을 만들고, 공개 문서 검색용 endpoint `https://learn.microsoft.com/api/mcp`를 사용합니다. label은 `mslearn`으로 구분합니다.

공개 문서 질문만 전송하고, 검색 도구만 허용합니다. 초기 승인 정책은 **항상 승인 요구**로 둡니다. 조직에서 외부 MCP가 금지되면 연결하지 말고 로컬 OpenAPI 계약 연습으로 대체합니다.

```text
Microsoft Foundry의 Prompt Agent와 Hosted Agent 차이를
Microsoft Learn 공식 문서에서 찾아 간단히 비교해줘.
```

실행 요청의 도구 이름·인수·목적지를 보고 승인합니다. 출처가 `learn.microsoft.com`인지, 실제 MCP tool call이 기록되는지 확인합니다. **승인 대기 상태를 빈 답변 오류로 처리하거나 자동 승인 루프를 만들지 않습니다.**

### 4. Toolbox 버전으로 재사용하기

Foundry Toolkit 또는 공식 Toolbox SDK 절차에서 새 toolbox를 만들고 승인된 도구를 1개만 넣습니다. **Create version → version-specific endpoint 확인 → tools/list → 도구 1회 호출** 순서로 검증합니다.

endpoint는 다음 형태입니다.

```text
https://<resource>.services.ai.azure.com/api/projects/<project>
  /toolboxes/<name>/versions/<version>/mcp?api-version=v1
```

실제로 사용할 때는 줄바꿈 없이 포털/SDK가 반환한 주소를 복사합니다. 일반 MCP endpoint를 Toolbox로 포장했다고 해당 서버의 권한이 생기는 것은 아닙니다.

새 버전에서 description을 명확히 바꾸고 테스트한 뒤 default로 승격하는 과정을 확인합니다. 운영 agent는 기본 버전을 자동으로 따라갈지 특정 버전에 고정할지 릴리스 정책으로 정합니다.

### 5. 도구가 많아질 때만 확장하기

**Tool search와 Skills는 Preview**입니다. Tool search는 필요한 도구만 동적으로 찾게 하고, Skills는 반복 수행 방법을 묶습니다. 도구 2개뿐인 첫 실습에 필수로 넣지 않습니다.

Grounding with Bing, Computer use, Image generation, SharePoint direct tool, Azure Functions 등은 Toolbox 지원 여부가 각각 다릅니다. 최신 공식 지원 표를 확인하고 **모든 도구가 Toolbox 안에 들어간다고 가정하지 않습니다.**

## 성공 기준

로컬 API의 응답과 OpenAPI 계약을 비교했습니다. 클라우드 경로를 진행했다면 실제 tools/list와 호출·승인 기록, 사용한 toolbox version을 확인했습니다. 로컬만 했다면 “클라우드 미실행”으로 기록합니다.

## 막혔을 때

`localhost` 접근 실패는 정상입니다. 인증 audience, project connection, agent identity 권한, MCP transport, 해당 지역의 도구 지원을 확인합니다. “always approve”로 문제를 숨기지 마세요.

## 정리

로컬 서버는 **실행한 터미널에서 Ctrl+C**로 종료합니다. 테스트 연결과 toolbox version의 ID를 기록하고 불필요한 것은 해당 자원만 삭제합니다.
