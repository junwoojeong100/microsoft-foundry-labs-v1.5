> **완성할 결과:** 목록뿐 아니라 MCP/OpenAPI의 실제 결과, Toolbox/Skill 버전, 인증 주체와 승인 결정을 확인합니다.

## 목표

**MCP는 연결 프로토콜, OpenAPI는 HTTP 계약, Toolbox는 버전 관리되는 도구 묶음,
Skill은 반복 작업의 수행 지침**입니다. Skill은 승인 권한이나 실행 성공 증거가 아닙니다.

## 준비

Python 기본 환경에 `requirements-tools.txt`를 설치합니다.
클라우드 단계는 L13의 Search와 프로젝트 관리 ID의 Search Index Data Reader 역할이 필요합니다.
**기본 코스의 필수 범위는 아래 1–2단계(로컬 HTTP/OpenAPI·MCP)입니다.**
3–4단계의 클라우드 Toolbox/Skills는 L13 자원 준비 후 선택하는 확장입니다.
기본 코스 학습자가 L13을 먼저 진행할 필요는 없습니다.

```bash
python -m pip install -r requirements-tools.txt
```

## 실행

### 1. 로컬 HTTP/OpenAPI 계약

첫 터미널에서 `python samples/inventory_api.py`, 다른 터미널에서:

```bash
curl --fail http://127.0.0.1:8766/health
curl --fail http://127.0.0.1:8766/inventory/NB-14
```

`samples/inventory.openapi.json`의 `get_stock` 응답과 비교합니다.
이 서버는 loopback·무인증 연습용입니다. 클라우드에서 접근하지 못하는 것이 정상이며
터널로 외부 공개하지 않습니다.

### 2. 동봉 MCP 서버를 실제 호출

```bash
python samples/toolbox_lab.py inspect --local
python samples/toolbox_lab.py call --local --tool get_stock --arguments '{"sku":"NB-14"}' --approve-tool get_stock
python samples/toolbox_lab.py call --local --tool prepare_purchase_request --arguments '{"sku":"NB-14","quantity":2}' --approve-tool prepare_purchase_request
```

stdio child process가 서버를 실행하고 initialize → tools/list → tools/call을 실제 교환합니다.
재고 8개, 단가 1,450,000원, 초안 총액 2,900,000원과 `order_submitted=false`를 확인합니다.
`--approve-tool`을 빼면 **호출 전에** 멈춥니다. 승인도 실제 주문 승인으로 해석하지 않습니다.

### 3. 선택 확장: 버전 고정 Toolbox와 Skill 생성

```bash
python samples/toolbox_lab.py create
python samples/toolbox_lab.py create --live
python samples/toolbox_lab.py inspect --live
```

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

OpenAPI 도구의 인수는 `tools/list`의 `inputSchema`를 따릅니다.
`api-version=2024-07-01`, `search`, `top<=5`, 지정 `select`를 전달합니다.
`python samples/toolbox_lab.py openapi`로 **A가 생성한 전체 계약**을 확인할 수 있습니다.
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
