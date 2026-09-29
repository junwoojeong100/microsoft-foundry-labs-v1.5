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
한 요청당 모델 최대 5회·도구 최대 8회·출력 2048토큰, SDK 재시도 0으로 제한합니다.

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
`AZURE_TENANT_ID`, `AZURE_RESOURCE_GROUP` 및 위의 모델/Search 값을 설정합니다.
이는 자격 증명이 아니라 환경 바인딩입니다. `azd env get-values` 전체를 공개 로그에 출력하지 마세요.

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
