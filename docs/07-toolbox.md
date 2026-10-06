> **완성할 결과:** 목록뿐 아니라 MCP/OpenAPI의 실제 결과, Toolbox/Skill 버전, 인증 주체와 승인 결정을 확인합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 기본은 로컬 1–2단계 · 클라우드 Toolbox/Skill은 선택입니다.

**먼저 할 일:** 같은 실습 폴더에서 터미널 두 개를 열고 서버용·호출용을 구분합니다.

**확인할 결과:** HTTP 재고 응답, MCP 도구 2종의 결과와 승인 없는 호출의 차단을 확인한 뒤 서버를 끕니다.

</div>

## 목표

**MCP는 연결 프로토콜, OpenAPI는 HTTP 계약, Toolbox는 버전 관리되는 도구 묶음,
Skill은 반복 작업의 수행 지침**입니다. Skill은 승인 권한이나 실행 성공 증거가 아닙니다.

## 개념과 실습 지도

**경험할 기능:** 같은 재고 조회를 HTTP와 MCP라는 두 연결 방식으로 호출합니다.

**무엇이며 왜 중요한가요?** OpenAPI는 요청·응답 설명서, MCP는 도구를 찾아 호출하는 공통 통신 방식입니다. Toolbox는 도구 묶음, Skill은 수행 지침입니다. 어느 것도 업무 승인 자체는 아닙니다.

**어떻게 사용하나요?** 로컬 서버의 재고 응답을 읽은 뒤 MCP로 같은 값을 조회합니다. 도구 목록에 있다는 것과 실제 호출됐다는 것을 구분합니다.

**어디서 실행하나요?** 내 PC의 터미널 두 개를 사용합니다. [HTTP 서버](../samples/inventory_api.py)·[OpenAPI](../samples/inventory.openapi.json)·[MCP 서버](../samples/mcp_server.py)·[클라이언트](../samples/toolbox_lab.py)가 동봉되어 있습니다. [Skill](../data/skills/purchase-review/SKILL.md)은 선택 확장입니다.

## 준비

L01의 Python 가상환경에 `requirements-tools.txt`를 설치합니다. 가상환경이 없다면 L01의 **가상환경 생성 단계**를 먼저 진행하되 Azure 로그인은 하지 않아도 됩니다. 설치에는 인터넷과 승인된 패키지 저장소 접근이 필요하지만 **기본 1–2단계에는 Azure 계정이 필요 없습니다.**
클라우드 단계는 L11의 Search와 프로젝트 관리 ID의 Search Index Data Reader 역할이 필요합니다.
**기본 코스의 필수 범위는 아래 1–2단계(로컬 HTTP/OpenAPI·MCP)입니다.**
3–4단계의 클라우드 Toolbox/Skills는 L11 자원 준비 후 선택하는 확장입니다.
기본 코스 학습자가 L11을 먼저 진행할 필요는 없습니다.

```bash
python -m pip install -r requirements-tools.txt
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `pip install -r requirements-tools.txt` | 활성화한 기본 가상환경에 MCP 실습 의존성을 추가합니다. `python -m pip`는 현재 Python과 설치 대상을 일치시킵니다. | 패키지 다운로드·로컬 환경 변경만 수행하며 Azure 도구를 호출하지 않습니다. |

</div>

## 실행

### 1. 로컬 HTTP/OpenAPI 계약

첫 터미널에서 서버를 시작하고 켜 둡니다.

```bash
python samples/inventory_api.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `inventory_api.py` | 합성 재고를 읽는 HTTP 서버를 `127.0.0.1:8766`에 띄웁니다. 프롬프트가 바로 돌아오지 않는 것이 정상입니다. | 내 컴퓨터에서만 대기합니다. Azure 비용 없음. 끝나면 이 터미널에서 Ctrl+C로 중지합니다. |

</div>

두 번째 터미널에서 같은 실습 폴더를 열고 Python 환경을 다시 선택합니다. **Windows PowerShell에서는 아래 `curl` 대신 `curl.exe`를 사용**해 다른 PowerShell 명령과의 이름 충돌을 피합니다.

첫 터미널의 대기 화면은 그대로 두세요. 두 번째 터미널의 준비가 기억나지 않으면 [L01 새 터미널 확인](#l01-new-terminal)으로 돌아갑니다.

```bash
curl --fail http://127.0.0.1:8766/health
curl --fail http://127.0.0.1:8766/inventory/NB-14
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `curl .../health` | `curl`은 HTTP 클라이언트입니다. `--fail`은 HTTP 오류 상태를 정상 응답처럼 넘기지 않고 실패 종료하게 합니다. | 로컬 서버 준비 상태만 확인합니다. 모델·MCP 호출이 아닙니다. |
| 2. `curl .../inventory/NB-14` | URL의 `NB-14`가 조회할 품목입니다. 서버가 CSV에서 읽은 재고 JSON을 반환합니다. | 재고 8개·단가 145만 원을 계약과 대조합니다. 읽기 전용·Azure 비용 없음. |

</div>

`samples/inventory.openapi.json`의 `get_stock` 응답과 비교합니다.
이 서버는 loopback·무인증 연습용입니다. 클라우드에서 접근하지 못하는 것이 정상이며
터널로 외부 공개하지 않습니다.

### 2. 동봉 MCP 서버를 실제 호출

서버가 대기 중인 첫 터미널이 아니라 **두 번째 터미널**에서 이어 실행합니다. 이 단계의 MCP 서버는 명령이 따로 시작하므로 서버 창을 하나 더 열 필요가 없습니다.

**macOS/Linux:** 아래를 한 줄씩 실행합니다. 두 번째 줄의 승인 오류는 의도한 결과이며, 그 뒤 승인된 호출로 비교합니다.

```bash
python samples/toolbox_lab.py inspect --local
python samples/toolbox_lab.py call --local --tool get_stock --arguments '{"sku":"NB-14"}'
python samples/toolbox_lab.py call --local --tool get_stock --arguments '{"sku":"NB-14"}' --approve-tool get_stock
python samples/toolbox_lab.py call --local --tool prepare_purchase_request --arguments '{"sku":"NB-14","quantity":2}' --approve-tool prepare_purchase_request
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `inspect --local` | 별도 stdio MCP 서버를 자식 프로세스로 실행하고 초기화·도구 목록/계약을 조회합니다. 앞의 HTTP 서버를 재사용하는 경로는 아닙니다. | 실제 로컬 MCP 교환과 도구 이름을 확인합니다. Azure 호출 없음. |
| 2. 승인 없는 `call` | 정확한 도구·인수를 주되 `--approve-tool`은 주지 않습니다. | `Approval required` 오류와 실패 종료가 정상입니다. 실제 `tools/call` 전에 차단됩니다. |
| 3. 승인한 `call ... get_stock` | `--tool`은 도구 이름, `--arguments`는 JSON, `--approve-tool`은 이 이름·인수의 1회 호출 허용입니다. | 재고 조회 결과와 로컬 evidence를 확인합니다. |
| 4. `call ... prepare_purchase_request` | JSON의 수량 2로 초안 도구를 호출합니다. 외부 작은따옴표는 셸에서 JSON의 큰따옴표를 보존합니다. | 290만 원·승인 대기·미주문 상태. 도구 호출 승인은 구매 승인이 아닙니다. |

</div>

**Windows PowerShell:** 위 블록 **대신** 다음을 한 줄씩 실행합니다. [`--%`](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_parsing#the-stop-parsing-token)는 Windows 실행기에 JSON의 따옴표를 그대로 전달하기 위한 PowerShell 문법입니다. Python 옵션이나 승인 생략 기능이 아닙니다.

```powershell
.\.venv\Scripts\python.exe samples/toolbox_lab.py inspect --local
.\.venv\Scripts\python.exe --% samples/toolbox_lab.py call --local --tool get_stock --arguments "{\"sku\":\"NB-14\"}"
.\.venv\Scripts\python.exe --% samples/toolbox_lab.py call --local --tool get_stock --arguments "{\"sku\":\"NB-14\"}" --approve-tool get_stock
.\.venv\Scripts\python.exe --% samples/toolbox_lab.py call --local --tool prepare_purchase_request --arguments "{\"sku\":\"NB-14\",\"quantity\":2}" --approve-tool prepare_purchase_request
```

<div class="command-explanation" markdown="1">

**명령 해설 — Windows**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `inspect --local` | 가상환경의 Python으로 로컬 MCP 목록을 읽습니다. | Azure 호출 없음. |
| 2. 승인 없는 `call` | JSON을 보존해 전달하되 도구 승인은 하지 않습니다. | `Approval required` 오류가 정상. 도구 실행 없음. |
| 3. 승인한 `get_stock` | 같은 JSON과 정확한 이름으로 이번 호출만 허용합니다. | 로컬 재고 8개·단가 145만 원. |
| 4. 승인한 초안 함수 | 수량 2의 입력과 도구 이름을 함께 확인합니다. | 290만 원·미주문. 실제 구매 승인 없음. |

</div>

stdio child process가 서버를 실행하고 initialize → tools/list → tools/call을 실제 교환합니다.
재고 8개, 단가 1,450,000원, 초안 총액 2,900,000원과 `order_submitted=false`를 확인합니다.
`--approve-tool`을 빼면 **호출 전에** 멈춥니다. 승인도 실제 주문 승인으로 해석하지 않습니다.

### 3. 선택 확장: 버전 고정 Toolbox와 Skill 생성

기본 코스 참여자는 여기서 **성공 기준 → 정리 → L08**로 이동합니다.

<details class="optional-path" markdown="1">
<summary>L11 준비 후에만: 클라우드 Toolbox·Skill 생성과 호출 (3–4단계)</summary>

```bash
python samples/toolbox_lab.py create
python samples/toolbox_lab.py create --live
python samples/toolbox_lab.py inspect --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — L11 자원과 관리 ID 권한이 준비된 경우에만 선택합니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `create` | 원격 Toolbox/Skill 생성 계획을 표시합니다. `--local` 생성은 필요 없으며 허용되지 않습니다. | Azure 요청 없음. |
| 2. `create --live` | 고유 Toolbox와 script-free Skill을 실제 등록하고 정확한 버전을 연결합니다. | 원격 객체 생성과 로컬 `results/toolbox.json` 기록. 연결 대상 서비스의 비용·권한 조건을 먼저 확인합니다. |
| 3. `inspect --live` | receipt의 원격 endpoint에 현재 Entra 주체로 연결하여 목록·Skill 리소스를 읽습니다. | 원격 읽기 요청이며 업무 도구 실행 성공과는 구분합니다. 빈 목록을 성공으로 표시하지 않습니다. |

</div>

동봉 `data/skills/purchase-review/SKILL.md`를 script-free Skill로 등록하고,
고유 이름 Toolbox version에 **정확한 Skill version**을 연결합니다.
`results/toolbox.json`은 버전별 MCP endpoint를 기록합니다.

| 구성 | 인증/승인 | 호출 목적 |
| --- | --- | --- |
| Toolbox endpoint | 현재 Entra 주체 | tools/list·resources/list·resources/read |
| Microsoft Learn MCP | 공개 문서, 검색 1종만 허용 | 제품 설명 검색, `require_approval=always` |
| Contoso OpenAPI | 프로젝트 관리 ID → Search audience | 합성 정책 index 읽기 |
| Skill | 같은 프로젝트의 고정 version | 초안 검토 지침, 실행 스크립트 없음 |

**중요:** Toolbox MCP endpoint 자체는 `tools/call`을 승인 대기로 막지 않을 수 있습니다.
`require_approval` metadata를 받은 **호출 runtime이 승인 정책을 집행**해야 합니다.
동봉 client는 모든 도구에 정확한 이름·인수의 1회 승인을 요구합니다.

### 4. 선택 확장: 목록의 정확한 이름으로 클라우드 도구 호출

`inspect`에서 반환된 **Contoso OpenAPI 검색 도구**의 정확한 이름을 복사합니다. Microsoft Learn 검색 도구는 다른 입력 형식을 쓰므로 섞지 않습니다.

```bash
python samples/toolbox_lab.py call --tool 실제-OPENAPI-검색도구명 --arguments '{"api-version":"2024-07-01","body":{"search":"노트북 구매 승인","top":3,"select":"id,document_id,title,section,filename,content,content_sha256"}}' --approve-tool 실제-OPENAPI-검색도구명 --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `call --live` | 두 곳의 `실제-OPENAPI-검색도구명`을 같은 실제 이름으로 바꿉니다. `api-version`은 최상위, `search`·`top`·`select`는 `body` 안에 둡니다. `--approve-tool`은 이 이름·인수의 1회 승인입니다. | 프로젝트 관리 ID로 한국어 합성 정책을 최대 3절 읽습니다. 원문·해시를 `data/policies/`와 대조합니다. Search 비용은 남으며 초안·주문은 생성하지 않습니다. |

</div>

OpenAPI 도구의 인수는 `tools/list`의 `inputSchema`를 따릅니다.
`api-version=2024-07-01`을 최상위에, `search`, `top<=5`, 지정 `select`를 **`body` 안에** 전달합니다. `search`를 최상위에 놓거나 Learn 도구의 `query`를 대신 쓰지 않습니다.
`python samples/toolbox_lab.py openapi`로 **이 저장소가 생성하는 전체 계약**을 확인할 수 있습니다. `openapi`는 Search 설정/receipt로 계약 JSON을 구성해 출력하는 로컬 명령입니다. Azure 요청이나 도구 실행은 없지만 L11의 설정이 있어야 올바른 endpoint가 들어갑니다.
API version의 schema default만 적는 것은 실제 query parameter 전송이 아닙니다.

Windows PowerShell에서 위 클라우드 호출을 선택했다면 `python`을 `.\.venv\Scripts\python.exe`로 바꾸고 실행기 뒤에 `--%`를 둡니다. `--arguments`는 바깥 **큰따옴표**로 감싸고 JSON 내부의 큰따옴표를 `\"`로 바꾸는 위 로컬 예제와 같은 문법을 사용합니다. 두 곳의 도구 이름은 직접 실제 값으로 바꿉니다. 승인 옵션이나 `--live`를 빼서 오류를 피하지 않습니다.

실제 output과 tool error를 `results/contoso-toolbox-*.jsonl`에 보존합니다.
Skill은 resources/list에 있어야 하며 resources/read의 본문까지 확인합니다.
이것은 지침 발견/읽기 검증이고, 모델이 매번 지침을 따랐다는 품질 보증은 아닙니다.

</details>

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 로컬 MCP 서버와 Foundry 연결의 차이 — 읽기용</summary>

### 로컬 코드와 Foundry 포털의 경계

동봉 MCP 서버의 원본 코드는 합성 Python 함수를 MCP 도구로 노출합니다.

```python
from mcp.server.fastmcp import FastMCP
from workshop import get_stock as stock, prepare_purchase_request as draft

server = FastMCP("contoso-purchasing-v1")

@server.tool()
def get_stock(sku: str) -> dict:
    return stock(sku)

@server.tool()
def prepare_purchase_request(sku: str, quantity: int) -> dict:
    return draft(sku, quantity)

server.run(transport="stdio")
```

| 실습 표면 | 실제 코드·동작 |
| --- | --- |
| 첫 터미널의 HTTP 서버 | `inventory_api.py`의 `Handler.do_GET()`가 `/inventory/<sku>`를 처리합니다. `127.0.0.1` 전용이라 Foundry 포털에서 직접 호출할 수 없습니다. |
| 두 번째 터미널의 MCP 호출 | `mcp_server.py`가 stdio tool을 제공하고 `toolbox_lab.py --local`이 자식 프로세스로 시작해 `tools/list`·`tools/call`을 보냅니다. |
| Foundry의 Cloud Toolbox 선택 확장 | `toolbox_lab.py create`가 `MCPToolboxTool`/`OpenApiToolboxTool` 설정과 managed identity를 등록합니다. 포털에서는 같은 Toolbox/version을 확인합니다. |
| 한 번의 도구 승인 | `--approve-tool`은 동봉 client가 정확한 도구 이름·인수에만 적용합니다. 로컬 Python 함수의 실제 실행 승인은 별도 업무 승인이나 주문 권한이 아닙니다. |

즉, 로컬 HTTP/MCP 코드는 포털의 버튼이 아니라 내 컴퓨터에서 실행됩니다. 포털 연동은 동봉 서버를 터널링하는 방식이 아니라 승인된 클라우드 Toolbox/OpenAPI 연결을 사용합니다.

</details>

## 성공 기준

기본 코스는 로컬 HTTP 응답과 MCP 2종의 실제 결과, 도구별 승인 차단을 확인하면 이 장을 완료합니다.
클라우드 확장을 수행했다면 tools/list·call·Skill read, version·caller·backend identity·승인 기록까지 별도로 확보합니다.
Tool search Preview나 외부 업무 시스템 연결을 실행한 것으로 합산하지 않습니다.

## 막혔을 때

| 로컬 증상 | 다음 행동 |
| --- | --- |
| `Connection refused` | 첫 터미널의 서버가 켜져 있는지와 현재 포트를 확인. 서버 창에서는 대기하고 두 번째 창에서 호출 |
| `Address already in use` | 먼저 자신이 켠 서버 창 확인. 다른 프로세스를 강제 종료하지 말고 사용 가능한 포트로 `inventory_api.py --port 18766`을 실행했다면 두 `curl` URL도 같은 포트로 변경 |
| `No module named mcp` | L01에서 Python 경로를 확인하고 그 가상환경에 `requirements-tools.txt`가 설치됐는지 확인 |
| JSON 해석 오류 | 자기 OS의 명령 블록 사용. 특히 Windows는 위 `--%`·따옴표 문법을 그대로 사용 |
| `Approval required` | 승인 없는 호출 과제에서는 정상. 승인한 호출을 하려면 확인한 이름·인수의 `--approve-tool` 값 대조 |

403은 호출자와 프로젝트 MI를 구분해 봅니다. 빈 목록은 connection/schema/도구 지원 상태를
확인합니다. 인증을 `anonymous`나 승인을 `never`로 바꾸어 오류를 숨기지 않습니다.

## 정리

로컬 stdio child는 client 종료 시 함께 종료됩니다. HTTP 서버는 Ctrl+C로 정지합니다.
Toolbox/Skill version은 소유 receipt와 함께 보존하며, 삭제는 별도 승인 후 진행합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** HTTP 재고, MCP 목록·두 도구의 결과·승인 없는 호출의 거절 근거. 서버 터미널의 **Ctrl+C 종료**까지 확인합니다.

**다음:** [L08 지침 비교·평가](#l08). 클라우드 Toolbox는 건너뛰어도 기본 코스를 이어갈 수 있습니다.

</div>
