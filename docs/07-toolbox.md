> **완성할 결과:** 목록뿐 아니라 MCP/OpenAPI의 실제 결과, Toolbox/Skill 버전, 인증 주체와 승인 결정을 확인합니다.

## 목표

**MCP는 연결 프로토콜, OpenAPI는 HTTP 계약, Toolbox는 버전 관리되는 도구 묶음,
Skill은 반복 작업의 수행 지침**입니다. Skill은 승인 권한이나 실행 성공 증거가 아닙니다.

## 개념과 실습 지도

**경험할 기능:** 로컬 HTTP API, OpenAPI 계약, MCP 도구 발견·호출, 선택형 Toolbox/Skill 연결입니다.

**무엇이며 왜 중요한가요?** OpenAPI는 HTTP 요청·응답의 모양을 설명하고, MCP는 클라이언트가 어떤 도구가 있는지 알아보고 호출하는 절차를 표준화합니다. Toolbox는 여러 연결을 버전 있는 묶음으로 재사용하게 하고, Skill은 작업 지침을 제공합니다. 서로 대체하는 이름이 아닙니다. 연결이 늘수록 “누가 어떤 이름의 도구를 어떤 인수로 실행했는가”를 분명히 해야 재현과 권한 통제가 가능합니다.

**어떻게 사용하나요?** 먼저 HTTP 응답을 원본 계약과 비교하고, 다음으로 MCP의 목록 조회와 실제 호출을 구분합니다. 도구 이름·인수를 검토한 후 그 한 호출만 승인하세요. 클라우드 확장은 같은 개념에 원격 인증·버전 고정을 추가하는 단계입니다.

**어디서 실행하나요?** 기본은 터미널 두 개를 쓰는 로컬 실습입니다. [HTTP 서버](../samples/inventory_api.py), [OpenAPI](../samples/inventory.openapi.json), [MCP 서버](../samples/mcp_server.py), [클라이언트](../samples/toolbox_lab.py), [Skill 원문](../data/skills/purchase-review/SKILL.md)을 비교하면 프로토콜과 업무 코드의 경계가 보입니다.

## 준비

Python 기본 환경에 `requirements-tools.txt`를 설치합니다.
클라우드 단계는 L13의 Search와 프로젝트 관리 ID의 Search Index Data Reader 역할이 필요합니다.
**기본 코스의 필수 범위는 아래 1–2단계(로컬 HTTP/OpenAPI·MCP)입니다.**
3–4단계의 클라우드 Toolbox/Skills는 L13 자원 준비 후 선택하는 확장입니다.
기본 코스 학습자가 L13을 먼저 진행할 필요는 없습니다.

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

두 번째 터미널에서 같은 리포 폴더로 이동한 뒤:

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

```bash
python samples/toolbox_lab.py inspect --local
python samples/toolbox_lab.py call --local --tool get_stock --arguments '{"sku":"NB-14"}' --approve-tool get_stock
python samples/toolbox_lab.py call --local --tool prepare_purchase_request --arguments '{"sku":"NB-14","quantity":2}' --approve-tool prepare_purchase_request
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `inspect --local` | 별도 stdio MCP 서버를 자식 프로세스로 실행하고 초기화·도구 목록/계약을 조회합니다. 앞의 HTTP 서버를 재사용하는 경로는 아닙니다. | 실제 로컬 MCP 교환과 도구 이름을 확인합니다. Azure 호출 없음. |
| 2. `call ... get_stock` | `--tool`은 정확한 도구 이름, `--arguments`는 JSON 객체, `--approve-tool`은 그 이름·인수의 이번 호출을 허용합니다. | 재고 조회 결과와 로컬 evidence를 확인합니다. 승인 옵션을 빼면 호출 전에 차단됩니다. |
| 3. `call ... prepare_purchase_request` | JSON의 수량 2로 초안 도구를 호출합니다. 외부 작은따옴표는 셸에서 JSON의 큰따옴표를 보존하기 위한 것입니다. | 290만 원·승인 대기·미주문 상태를 확인합니다. 이 도구 호출 승인은 실제 구매 승인이 아닙니다. |

</div>

stdio child process가 서버를 실행하고 initialize → tools/list → tools/call을 실제 교환합니다.
재고 8개, 단가 1,450,000원, 초안 총액 2,900,000원과 `order_submitted=false`를 확인합니다.
`--approve-tool`을 빼면 **호출 전에** 멈춥니다. 승인도 실제 주문 승인으로 해석하지 않습니다.

### 3. 선택 확장: 버전 고정 Toolbox와 Skill 생성

```bash
python samples/toolbox_lab.py create
python samples/toolbox_lab.py create --live
python samples/toolbox_lab.py inspect --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — L13 자원과 관리 ID 권한이 준비된 경우에만 선택합니다.**

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

`inspect`에서 반환된 이름을 복사합니다. 예시는 실제 이름을 추측해서 사용하지 마세요.

```bash
python samples/toolbox_lab.py call --tool 실제-검색도구명 --arguments '{"query":"Microsoft Foundry hosted agents"}' --approve-tool 실제-검색도구명 --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `call --live` | 두 곳의 `실제-검색도구명`을 `inspect`에서 받은 같은 이름으로 바꿉니다. `--arguments`는 해당 도구 schema에 맞는 입력이며 `--approve-tool`은 한 번의 승인을 표시합니다. | 원격 도구에 질문이 전송됩니다. 이 예는 제품 공개 문서 검색이며 회사 데이터는 넣지 않습니다. 도구의 실제 결과·오류와 서비스별 비용을 확인합니다. |

</div>

OpenAPI 도구의 인수는 `tools/list`의 `inputSchema`를 따릅니다.
`api-version=2024-07-01`, `search`, `top<=5`, 지정 `select`를 전달합니다.
`python samples/toolbox_lab.py openapi`로 **A가 생성한 전체 계약**을 확인할 수 있습니다. `openapi`는 Search 설정/receipt로 계약 JSON을 구성해 출력하는 로컬 명령입니다. Azure 요청이나 도구 실행은 없지만 L13의 설정이 있어야 올바른 endpoint가 들어갑니다.
API version의 schema default만 적는 것은 실제 query parameter 전송이 아닙니다.

실제 output과 tool error를 `results/contoso-toolbox-*.jsonl`에 보존합니다.
Skill은 resources/list에 있어야 하며 resources/read의 본문까지 확인합니다.
이것은 지침 발견/읽기 검증이고, 모델이 매번 지침을 따랐다는 품질 보증은 아닙니다.

## 성공 기준

기본 코스는 로컬 HTTP 응답과 MCP 2종의 실제 결과, 도구별 승인 차단을 확인하면 이 장을 완료합니다.
클라우드 확장을 수행했다면 tools/list·call·Skill read, version·caller·backend identity·승인 기록까지 별도로 확보합니다.
Tool search Preview나 외부 업무 시스템 연결을 실행한 것으로 합산하지 않습니다.

## 막혔을 때

403은 호출자와 프로젝트 MI를 구분해 봅니다. 빈 목록은 connection/schema/도구 지원 상태를
확인합니다. 인증을 `anonymous`나 승인을 `never`로 바꾸어 오류를 숨기지 않습니다.

## 정리

로컬 stdio child는 client 종료 시 함께 종료됩니다. HTTP 서버는 Ctrl+C로 정지합니다.
Toolbox/Skill version은 소유 receipt와 함께 보존하며, 삭제는 별도 승인 후 진행합니다.
