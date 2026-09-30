> **완성할 결과:** A에 들어 있는 같은 구매 도우미 코드를 패키징하고 로컬·Azure에서 호출합니다.

## 목표

Prompt Agent는 instructions와 서비스 도구, **Hosted Agent는 직접 관리하는 실행 코드**입니다.
동봉 구현은 구조화된 요청·증거를 그대로 주고받기 위해 **Invocations protocol**을 사용합니다.
Responses·Voice·Teams protocol을 검증한 것으로 표시하지 않습니다.

## 준비

L13의 Search/index와 모델, Python **3.13**, azd **1.34.0**,
`azure.ai.agents` **1.0.0-beta.10** 조합을 기준으로 합니다.
지원 범위·지역은 공식 Hosted 문서를 확인하세요. 특정 구독 Owner를 학습자에게 요구하지 않습니다.
배포 담당자와 이미 준비된 프로젝트를 사용하는 학습자를 구분합니다.

```bash
python3.13 -m venv .venv-live
source .venv-live/bin/activate
python -m pip install -r requirements-hosted.txt
python -m pip check
python scripts/check_sdk.py
```

MAF 실습용 `.venv-advanced`는 별도입니다. 서로 다른 `azure-ai-projects` 제약을 단순 병합하지 않습니다.

## 실행

### 1. Azure 호출 없이 패키지부터 만들기

```bash
python scripts/build_hosted.py
```

`.build/contoso/`와 `.build/contoso-code.zip`을 만듭니다.
Optimizer용 Responses 프로필은 `.build/contoso-responses/`에 별도로 생성합니다.
이 분리 덕분에 Optimizer의 설정 로딩을 고쳐도 이미 검증한 기본 Invocations 런타임을 바꾸지 않습니다.
구매 정책·재고·instructions·실행 코드·고정 의존성만 포함하고,
`.env`, 인증, 평가 정답, 기존 결과, 개인 환경은 포함하지 않습니다.
`package-manifest.json`의 파일별 hash와 runtime contract를 확인합니다.
외부 샘플 저장소나 B를 clone할 필요가 없습니다.

### 2. 로컬 실행과 호출

서버 터미널에서 다음 동봉 helper를 실행합니다. L01/L13의 `.env`와 `results/search.json`에서
허용된 비밀 없는 값만 자식 프로세스로 전달합니다.

```bash
python scripts/run_hosted_local.py
```

다른 터미널에서:

```bash
curl --fail http://127.0.0.1:8088/readiness
python samples/hosted_client.py invoke --local
python samples/hosted_client.py invoke --local --live
```

**로컬 서버도 실제 Azure 모델·검색을 사용하므로 호출에는 비용이 발생합니다.**
기본 bind는 loopback이며 인증 없는 개발 서버를 외부에 노출하지 않습니다.
한 요청은 도구 계획 → 근거 답변 → 출처 대응 확인으로 나눕니다.
앞의 두 모델 출력은 각각 2048토큰, 출처 확인은 512토큰으로 제한합니다.
도구 최대 8회, SDK 재시도 0을 유지합니다.

현재 엔진은 모델 실행 **전에** 서버가 질문별 검색과 작은 합성 정책 13절의 실제 조회를 수행합니다.
모델의 검색 함수 선택을 기다리지 않습니다. 응답은 내부적으로 `answer`·`citation_ids` JSON이며,
인용은 실제 반환된 절 중 모델이 선택한 것만 렌더링합니다. 검색/인용 누락은 성공이 아니라 오류입니다.
`tool_calls`의 `execution=server_required`는 실제 서버 검색이며 모델이 호출했다고 가장한 기록이 아닙니다.
명시된 SKU의 `get_stock`도 읽기 전용 서버 선행 작업으로 기록합니다. 초안 생성은 여전히 별도 함수이며
실제 주문·결제를 수행하지 않습니다. 수량 제한의 근거는 실행에 사용한 `tool_definitions`로 대조합니다.

도구 실행 단계에는 답변 JSON 형식을 강제하지 않고 필요한 함수를 실행하게 합니다.
그 다음 답변 전용 단계에서 실제 결과와 문서에 근거한 엄격한 JSON을 생성합니다.
도구를 호출하겠다는 계획 문장은 답변이나 실행 증거로 게시하지 않습니다.

초안 도구 인수는 사용자가 명시한 SKU와 하나의 명확한 정수 수량에 연결돼야 합니다.
모델이 빠진 수량을 1로 채우거나 11개를 10개로 줄여 제안해도 코드가 실행 전에 거절합니다.
답변 단계에도 실제 함수 정의를 전달하여 도구의 1~10 입력 제약을 회사 정책으로 혼동하지 않게 합니다.
마지막 출처 확인 단계는 실제 검색 자료와 작성된 답변만 보고 근거를 선택하며,
두 모델의 실제 선택을 합쳐 표시합니다. 원문 답변과 출처 선택 응답 ID는 각각 보존합니다.

### 3. 준비된 프로젝트에만 배포하기

관리자가 L01의 동봉 IaC로 만든 환경이라면:

```bash
python scripts/configure_hosted.py
azd deploy contoso-purchasing --no-prompt
azd ai agent show contoso-purchasing --output json
python scripts/runtime_roles.py --agent contoso-purchasing --live
```

학습자에게 별도로 provision된 프로젝트를 제공했다면 `azd env new`와 `azd env set`으로
`AZURE_AI_PROJECT_ID`, `AZURE_AI_PROJECT_ENDPOINT`, `AZURE_SUBSCRIPTION_ID`,
`AZURE_TENANT_ID`, `AZURE_RESOURCE_GROUP`, **`AZURE_LOCATION`** 및 모델/Search 값을 설정합니다.
이는 자격 증명이 아니라 환경 바인딩입니다. `azd env get-values` 전체를 공개 로그에 출력하지 마세요.

`AZURE_LOCATION`은 프로젝트의 실제 리전 이름입니다. 코드 배포에서 이 값이 없으면 실패합니다.
`scripts/configure_hosted.py` 경로는 동봉 관리 스크립트가 만든 소유 receipt를 사용하며,
강사가 제공한 별도 프로젝트를 사용할 때는 그 프로젝트의 실제 값으로 azd 환경을 구성해야 합니다.

동봉 `azure.yaml`은 **code deployment**이며 Docker/ACR가 필수는 아닙니다.
이 파일로 무심코 `azd provision`을 실행하지 않습니다. 리소스 생성은 L01 관리 경로입니다.
배포마다 새 immutable version이 생깁니다. agent runtime identity에는 해당 Search 읽기 역할만 부여합니다.

L20의 native optimizer는 현재 **Responses protocol만 지원**합니다.
같은 업무 엔진을 사용하는 선택형 `contoso-purchasing-responses` adapter를 함께 동봉했습니다.
필요할 때만 해당 service를 지정해 배포하고, 별도 agent/version/identity로 기록합니다.
기본 Invocations 실습의 성공을 이 adapter의 실행 증거로 대신 사용하지 않습니다.

```bash
python scripts/run_hosted_local.py --protocol responses --port 8089
azd deploy contoso-purchasing-responses --no-prompt
python scripts/runtime_roles.py --agent contoso-purchasing-responses --live
azd ai agent invoke contoso-purchasing-responses "표준 노트북 상한은?" --protocol responses --version 실제숫자
```

Responses CLI에는 질문을 직접 전달합니다. JSON request 파일을 그대로 질문으로 감싸 보내지 않습니다.
raw 응답이 SSE이면 `response.completed` terminal event를 확인하며, 출력 delta만으로 성공 처리하지 않습니다.

### 4. 정확한 버전 원격 호출

```bash
python samples/hosted_client.py invoke --version 실제숫자 --live
```

`show`의 실제 version을 넣습니다. 새 version-bound session에서 호출하고 `finally`에서
**compute만 stop**합니다. 응답·내부 model response ID·tool call ID·citation·trace ID가 반환되며,
로컬 package contract와 원격 contract가 다르면 실패합니다.
trace ID가 없으면 추측하지 않고 미수집으로 남깁니다.

배포·session 관리는 azd, 동봉 Invocations client의 본문 수집은 **서비스가 반환한 endpoint에
Entra-authenticated HTTP JSON 요청**을 사용합니다. CI의 azd stdout에 추가 출력이 섞인 실제 사례를
수정한 것으로, CLI 화면 출력을 안정적인 API JSON 계약으로 가정하지 않습니다.

### 5. 기본 도구를 실제로 확인하기

질문은 “NB-14 2대의 정책과 재고를 확인하고 구매 요청 초안만 만들어줘”입니다.
결과에서 `search_policies`, `get_stock`, `prepare_purchase_request`의 인수와 결과를 확인합니다.
총액은 **2,900,000원**, 두 승인 역할, `order_submitted=false`여야 합니다.
Toolbox를 별도 연결할 때는 L07의 인증 주체와 1회 승인 정책을 그대로 유지합니다.

## 성공 기준

패키징·서버 시작·로컬 업무 결과·배포·같은 버전 원격 업무 결과를 각각 확인했습니다.
hash·도구·citation이 연결되고, 배포만 성공한 상태를 품질 통과로 표시하지 않습니다.

## 막혔을 때

health 실패는 entry point/의존성, 502는 보존된 upstream 오류, 403은 runtime ID의
모델/Search 역할부터 확인합니다. 424 cold start는 로그를 확인하고 제한된 횟수만 재시도합니다.
오류 문장을 HTTP 200의 정상 답변으로 바꾸지 않습니다.

## 정리

로컬 서버는 시작한 터미널의 Ctrl+C로 종료합니다. 중단된 실행은
`python scripts/stop_sessions.py`로 **기록된 세션만** 정지합니다.
agent/version/session 파일·Azure 자원은 남습니다. 남은 storage·로그·Search 비용을 L12에 기록합니다.

Hosted의 `/app`은 읽기 전용입니다. 원격 원시 증거는 세션의 `$HOME/.contoso/evidence`에만
기록하고 코드 폴더에 쓰지 않습니다. 이를 패키지에 포함하지 않습니다.
