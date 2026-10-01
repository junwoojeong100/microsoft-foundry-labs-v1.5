> **완성할 결과:** 올바른 테넌트의 Foundry 프로젝트, 호출 가능한 모델 1개, 개발 환경, 비용 중단 계획.

## 목표

실습 실패의 대부분을 차지하는 **권한 / 잘못된 엔드포인트 / 지원 지역 / quota** 문제를 시작 전에 분리합니다.

## 개념과 실습 지도

**경험할 기능:** Foundry 프로젝트의 작업 범위, 모델 배포, Entra 로그인, Python 가상환경을 연결합니다.

**무엇이며 왜 중요한가요?** 구독은 비용·관리의 범위, 리소스 그룹은 자원 묶음, Foundry 리소스는 서비스의 상위 경계, 프로젝트는 에이전트·연결을 다루는 작업 공간입니다. 프로젝트 주소를 안다고 호출 권한이 생기지는 않습니다. 로그인은 “누구인가”, 역할은 “무엇을 할 수 있는가”, quota는 “얼마나 사용할 수 있는가”에 답합니다. 이들을 분리하면 인증 오류 때문에 불필요하게 자원을 다시 만들거나 권한을 넓히는 일을 피할 수 있습니다.

**어떻게 사용하나요?** 포털에서 강사가 준 프로젝트와 모델을 확인하고, 로컬 환경을 준비한 뒤 주소와 배포 이름을 설정합니다. 이미 제공된 프로젝트가 있으면 관리자용 생성 명령은 건너뜁니다. L03에서 실제 응답을 받기 전까지는 “환경 준비”이지 “모델 호출 성공”이 아닙니다.

**어디서 실행하나요?** 포털은 프로젝트·엔드포인트 확인, 터미널은 Python 설치 확인·패키지 준비·CLI 로그인에 사용합니다. [.env.example](../.env.example), [관리 스크립트](../scripts/azure_environment.py), [인프라 정의](../infra/main.bicep)를 함께 열어 어떤 설정이 어느 자원을 만드는지 확인하세요.

## 준비

| 항목 | 기본 코스 | 추가 조건 |
| --- | --- | --- |
| Azure | 사용이 승인된 구독과 비운영 리소스 그룹 | 조직 정책을 우회하지 않음 |
| Foundry | **새 포털의 Foundry 프로젝트** | hub 기반 Classic 프로젝트와 다름 |
| 모델 | Responses·도구 사용을 지원하는 채팅 모델 | L02에서 지원 여부 확인 |
| 개발 환경 | Python 3.13, Azure CLI 2.86.0 | 로컬 표준 라이브러리 연습은 3.11+ 가능 |
| 데이터 | 이 가이드의 합성 데이터 | 실제 고객·직원 자료 업로드 금지 |
| 예산 | 개인/팀별 한도와 중단 담당자 | 예산 알림은 강제 과금 차단이 아님 |

## 실행

### 1. 프로젝트를 준비하기

`https://ai.azure.com`에서 새 Foundry 경험을 사용합니다. 기존 승인된 프로젝트가 있으면 학습자가 사용하고,
없으면 담당자가 새 환경을 준비합니다. 이번 제작 검증은 기존 A/B 자원이 아닌 **새 전용 RG**에서 진행하며,
제작 실행 결과는 `validation/current/report.json`에서 별도로 확인합니다.

비운영 리소스 그룹, 프로젝트 이름, 지역을 기록하세요. 기본 예시는 `contoso-workshop`입니다.
**학습자 경로:** 관리자가 제공한 프로젝트/모델과 최소 데이터 역할을 사용합니다.
**관리자 경로:** 아래 스크립트가 고유 새 RG만 만들고 기존 자원을 재사용/삭제하지 않습니다.

```bash
python3.13 scripts/azure_environment.py create --subscription 실제-구독-ID --location 허용-리전 --cost-authorization "승인 금액과 보존 정책" --live
python3.13 scripts/azure_environment.py foundation --chat-model gpt-6-sol --chat-version 2026-09-22 --judge-model 지원-judge모델 --judge-version 실제버전 --embedding-model 지원-embedding모델 --embedding-version 실제버전 --model-sku GlobalStandard --capacity 10 --live
python3.13 scripts/azure_environment.py roles --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — 관리자 전용이며, 제공된 환경을 쓰는 학습자는 실행하지 않습니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `create` | `--subscription`은 승인된 구독, `--location`은 실제 리전입니다. `--cost-authorization`의 따옴표 안에는 승인된 금액·보존 조건을 기록합니다. `--live`가 새 전용 RG 생성을 허용합니다. | 소유 receipt를 `results/azure-environment.json`에 기록합니다. 기존 RG 재사용 명령이 아닙니다. 이후 자원 비용의 범위가 됩니다. |
| 2. `foundation` | chat·judge·embedding 각각의 모델 ID와 버전을 지정합니다. `--model-sku`는 처리 범위/배포 유형, `--capacity 10`은 해당 모델의 용량 단위이며 10달러 한도가 아닙니다. | Foundry 리소스·프로젝트·모델을 실제 배포합니다. 정책·quota 확인과 비용 승인이 선행되어야 합니다. |
| 3. `roles` | 소유 receipt에 기록된 새 환경에 실습용 역할을 설정합니다. `--live`는 권한 변경까지 포함하는 실제 실행입니다. | 관리자 권한이 필요합니다. 역할 전파 후 데이터 접근을 확인하며, 다른 환경에 대한 권한 확대 용도로 쓰지 않습니다. |

</div>

명령의 설명값은 실제 값으로 바꿉니다. 모델 catalog·SKU·quota를 먼저 조회하고
Global/Data Zone/Standard 처리 범위를 승인받습니다. capacity의 단위는 모델별로 다르며 비용 상한이 아닙니다.
`infra/main.bicep`은 Foundry account/project와 명시한 모델만 배포합니다.
L13이 필요할 때만 `python scripts/azure_environment.py search --live`로 Search를 추가합니다. `search`는 소유 RG에 검색 서비스를 생성하는 관리자 작업이며, 요청하지 않아도 고정 비용이 생길 수 있습니다. 이 명령은 “검색을 한 번 해 보기”가 아닙니다.
소유 기록은 `results/azure-environment.json`입니다. RequestConflict 등의 부분 실패는
원본 deployment operation을 확인하고 **같은 소유 자원에 한해서만** `foundation --resume`로 재개합니다. `--resume`은 기록된 부분 배포를 이어가는 옵션이며 새 환경을 고르거나 원래 오류 기록을 지우는 옵션이 아닙니다.

### 2. 역할을 “누가 무엇을 하는지”로 확인하기

| 주체 | 필요한 범위의 출발점 | 확인할 동작 |
| --- | --- | --- |
| 실습 개발자 | 프로젝트 `Foundry User`, 부모 리소스 읽기 | agent 생성·호출 |
| 리소스/모델 관리자 | 리소스 `Foundry Account Owner` 등 해당 관리 권한 | 프로젝트·모델 배포 |
| 단순 사용자 | `Foundry Agent Consumer` | 허용된 agent endpoint 호출만 |
| 프로젝트 관리 ID | 연결 대상에 필요한 최소 역할 | Search/Storage/모델 접근 |
| 에이전트 ID | 실제 runtime 도구 권한 | Toolbox와 업무 API 사용 |
| 평가/추적 사용자 | 프로젝트 역할 + 로그 리소스의 읽기 역할 | 평가·App Insights 조회 |
| quota 조회자 | 구독의 `Cognitive Services Usages Reader` | 사용량/배포 적격성 확인 |

역할 이름은 최근 **Azure AI User → Foundry User** 등으로 변경되었습니다. 화면에 이전 이름이 남아 있을 수 있습니다. 역할 ID와 핵심 권한은 이름 변경만으로 바뀌지 않았습니다. Azure `Owner`/`Contributor`가 있다고 Foundry 데이터 평면 호출이 자동 허용되는 것도 아닙니다.

**역할 부여는 담당 관리자에게 요청합니다.** 학습자 모두에게 구독 Owner를 주지 않습니다. 도구별 추가 권한은 해당 모듈에서 확인합니다.

### 3. 지역·배포·비용 확인하기

L02의 모델을 1개만 준비합니다. 합성 데이터이고 조직 정책이 허용하면 사용량 기반 배포부터 시작합니다. **PTU, 유료 Search tier, GPU managed compute, 대규모 Batch, fine-tuning은 기본 코스에 불필요**합니다.
L08의 native 자동 평가를 진행할 때는 별도 judge 배포도 필요합니다. 관리자가 이미 제공했다면 다시 만들지 않습니다.

프로젝트 지역, 모델 지원 지역, 배포 유형, quota는 서로 다른 조건입니다. “Korea Central 프로젝트”라는 사실만으로 모든 추론이 한국에서 처리된다고 가정하지 마세요. Global / Data Zone / geography 처리 범위는 L02에서 다룹니다.

Agent playground의 **Metrics**에서 자동 평가 항목을 확인합니다. 필요하지 않은 평가는 선택 해제합니다. Playground 평가도 과금될 수 있습니다. 비용에는 추론뿐 아니라 File search, Search, Code Interpreter, 로그, hosted runtime 등이 추가될 수 있습니다.

### 4. 로컬 연습 환경 만들기

가이드 폴더에서 실행합니다.

```bash
python3 samples/workshop.py doctor
python3 samples/workshop.py validate-data
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `doctor` | 현재 Python과 필요한 도구의 설치 상태를 확인합니다. 문제를 자동 설치·수정하는 명령은 아닙니다. | 터미널의 진단 항목을 읽습니다. Azure 로그인·모델 호출 없음. |
| 2. `validate-data` | 동봉 합성 데이터의 형식·시나리오 ID·dev/holdout 분리를 로컬에서 검사합니다. | 오류 없이 검사 결과가 나와야 합니다. 데이터 구조 검사이지 모델 품질 평가가 아닙니다. |

</div>

기대 결과는 `dev=10, holdout=10`, 중복 시나리오 0개입니다. 이 단계는 **Azure 계정·네트워크·외부 패키지가 필요 없습니다.**

코드로 Azure를 호출할 때만 패키지를 설치합니다.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

<div class="command-explanation" markdown="1">

**명령 해설 — macOS/Linux**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python3.13 -m venv .venv` | Python 3.13의 `venv` 모듈로 이 폴더 전용 환경을 만듭니다. 전역 Python 패키지와 분리합니다. | 로컬 `.venv/` 생성. Azure 호출 없음. |
| 2. `source .venv/bin/activate` | 현재 터미널의 `python`·`pip`가 가상환경을 가리키게 합니다. 새 터미널에서는 다시 선택해야 합니다. | 현재 셸만 변경. 프로젝트나 리소스를 활성화하는 명령이 아닙니다. |
| 3. `python -m pip install -r requirements.txt` | 선택한 Python의 pip로 파일에 지정된 의존성을 설치합니다. `-r`은 요구사항 파일을 읽는 옵션입니다. | 허용된 패키지 저장소에 접속하고 로컬 환경을 변경합니다. Azure 추론은 하지 않습니다. |
| 4. `cp -n .env.example .env` | 설정 템플릿을 복사합니다. `-n`은 기존 `.env`를 덮어쓰지 않게 합니다. | 없는 경우 로컬 `.env` 생성. 다음 단계에서 실제 엔드포인트·배포 이름을 입력합니다. |

</div>

Windows PowerShell 대안:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

<div class="command-explanation" markdown="1">

**명령 해설 — Windows에서는 위 macOS/Linux 블록 대신 사용합니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `py -3.13 -m venv .venv` | Windows Python Launcher에서 3.13을 선택하여 가상환경을 만듭니다. | 로컬 `.venv`만 생성합니다. |
| 2. `.venv\Scripts\python.exe -m pip install` | 활성화 없이 가상환경 Python을 직접 지정합니다. `-r requirements.txt`의 패키지를 설치합니다. | 패키지 다운로드·설치. PowerShell 실행 정책을 낮출 필요가 없습니다. |
| 3. `if ... Copy-Item` | `Test-Path`로 `.env` 존재 여부를 검사하고 없을 때만 템플릿을 복사합니다. | 기존 개인 설정은 보존합니다. Azure 호출 없음. |

</div>

이후 `python` 명령은 해당 환경의 Python을 뜻합니다. PowerShell에서 활성화가 제한되면 `.venv\Scripts\python.exe`를 직접 사용하세요.

### 5. 엔드포인트와 인증 설정하기

![실제 Manage → Project details 화면. 프로젝트·상위 리소스·리전과 Connected resources가 보이고 구독·테넌트·엔드포인트·연결 키·계정 값은 가려져 있다.](../assets/portal/13-project-settings.png)

**화면 따라 읽기:** **Manage → Project details**에서 **Name / Parent resource / Location**을 먼저 대조합니다. **Project endpoint**의 자신의 값을 로컬 설정에 넣고, **Connected resources**에서는 연결 대상·Category·Auth method를 읽습니다. 회색 부분은 개인정보/연결 정보를 가린 것이며 복사할 예시 값이 아닙니다. 연결 키를 표시·복사할 필요는 없습니다. 이 화면 관찰에서는 **Add connection / Users의 권한 변경을 수행하지 않았습니다.**

포털의 **Manage → Project details** 또는 프로젝트 시작 화면에서 project endpoint를 복사합니다. `.env`의 값 두 개를 수정하세요.

```text
FOUNDRY_PROJECT_ENDPOINT=https://리소스명.services.ai.azure.com/api/projects/프로젝트명
FOUNDRY_MODEL_DEPLOYMENT_NAME=실제-모델-배포이름
```

위 예시의 한글 설명을 그대로 사용하지 않습니다. **프로젝트 endpoint에 `/openai/v1`을 추가하지 않습니다.** SDK가 올바른 경로를 구성합니다. API key는 넣지 않습니다.

L08 전에 `.env`의 `FOUNDRY_JUDGE_DEPLOYMENT_NAME`도 관리자가 제공한 실제 judge 배포 이름으로 설정합니다. 환경 변수의 뜻과 기본 예시는 `.env.example`에서 확인합니다.

```bash
az login
az account show --query "{subscription:name,tenant:tenantId}" -o table
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az login` | Azure CLI의 사용자 로그인을 시작합니다. 브라우저 포털에 로그인했더라도 CLI 인증은 별도로 필요합니다. | 로컬 CLI 인증 상태가 생깁니다. 비밀번호·MFA는 인증 화면에서 직접 입력하고 채팅·문서에 적지 않습니다. |
| 2. `az account show` | `--query`로 현재 구독 이름과 테넌트 ID만 선택하고 `-o table`로 읽기 쉽게 출력합니다. | 대상 확인용이며 모델 요청이나 자원 생성은 하지 않습니다. 자신의 승인 범위인지 대조합니다. |

</div>

다른 구독이면 명시적으로 선택합니다.

```bash
az account set --subscription "실습용-구독-ID"
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az account set` | `--subscription`의 자리표시자를 승인된 구독 ID로 바꿔 CLI의 기본 대상을 선택합니다. | 로컬 CLI 기본 구독 변경. 권한을 새로 얻거나 기존 Azure 자원을 이동시키지는 않습니다. |

</div>

샘플은 로컬에서 **AzureCliCredential**을 사용합니다. 운영 환경에서는 적절한 managed identity 등 배포 환경에 맞는 자격 증명을 선택해야 합니다.

## 성공 기준

프로젝트·모델·역할·지역·비용 담당자를 기록했고, 로컬 데이터 검사에 성공했습니다. Azure 연결 성공은 **다음 L03의 실제 응답**으로 별도 확인합니다.

## 막혔을 때

**403이면 먼저 역할, 404면 endpoint와 배포 이름, 429면 quota**를 확인합니다. private endpoint 환경이라면 승인된 VPN·VNet 내 개발 환경이 필요합니다. 문제 해결을 위해 public access를 임의로 켜지 마세요.

SDK 설치가 사내 미러에서 실패하면 허용된 미러의 동기화를 요청합니다. 최신 패키지가 공개 PyPI에 있다는 사실이 조직 정책을 무시하고 설치해도 된다는 뜻은 아닙니다.

## 정리

리소스 그룹과 담당자를 기록하고 L12의 종료 체크리스트를 미리 읽습니다. `.env`를 공유·커밋하지 않습니다. 이 실습의 `.env`에는 비밀이 없어야 합니다.
