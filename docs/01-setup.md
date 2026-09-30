> **완성할 결과:** 올바른 테넌트의 Foundry 프로젝트, 호출 가능한 모델 1개, 개발 환경, 비용 중단 계획.

## 목표

실습 실패의 대부분을 차지하는 **권한 / 잘못된 엔드포인트 / 지원 지역 / quota** 문제를 시작 전에 분리합니다.

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
python3.13 scripts/azure_environment.py foundation --chat-model 지원-chat모델 --chat-version 실제버전 --judge-model 지원-judge모델 --judge-version 실제버전 --embedding-model 지원-embedding모델 --embedding-version 실제버전 --model-sku GlobalStandard --capacity 10 --live
python3.13 scripts/azure_environment.py roles --live
```

명령의 설명값은 실제 값으로 바꿉니다. 모델 catalog·SKU·quota를 먼저 조회하고
Global/Data Zone/Standard 처리 범위를 승인받습니다. capacity의 단위는 모델별로 다르며 비용 상한이 아닙니다.
`infra/main.bicep`은 Foundry account/project와 명시한 모델만 배포합니다.
L13이 필요할 때만 `python scripts/azure_environment.py search --live`로 Search를 추가합니다.
소유 기록은 `results/azure-environment.json`입니다. RequestConflict 등의 부분 실패는
원본 deployment operation을 확인하고 **같은 소유 자원에 한해서만** `foundation --resume`로 재개합니다.

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
L08의 native 자동 평가를 진행할 때는 별도 judge 배포도 필요합니다. 관리자가 이미 제공했다면 다시 만들지 않습니다. **PTU, 유료 Search tier, GPU managed compute, 대규모 Batch, fine-tuning은 기본 코스에 불필요**합니다.

프로젝트 지역, 모델 지원 지역, 배포 유형, quota는 서로 다른 조건입니다. “Korea Central 프로젝트”라는 사실만으로 모든 추론이 한국에서 처리된다고 가정하지 마세요. Global / Data Zone / geography 처리 범위는 L02에서 다룹니다.

Agent playground의 **Metrics**에서 자동 평가 항목을 확인합니다. 필요하지 않은 평가는 선택 해제합니다. Playground 평가도 과금될 수 있습니다. 비용에는 추론뿐 아니라 File search, Search, Code Interpreter, 로그, hosted runtime 등이 추가될 수 있습니다.

### 4. 로컬 연습 환경 만들기

가이드 폴더에서 실행합니다.

```bash
python3 samples/workshop.py doctor
python3 samples/workshop.py validate-data
```

기대 결과는 `dev=10, holdout=10`, 중복 시나리오 0개입니다. 이 단계는 **Azure 계정·네트워크·외부 패키지가 필요 없습니다.**

코드로 Azure를 호출할 때만 패키지를 설치합니다.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

Windows PowerShell 대안:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

이후 `python` 명령은 해당 환경의 Python을 뜻합니다. PowerShell에서 활성화가 제한되면 `.venv\Scripts\python.exe`를 직접 사용하세요.

### 5. 엔드포인트와 인증 설정하기

포털의 **Manage → Project details** 또는 프로젝트 시작 화면에서 project endpoint를 복사합니다. `.env`의 값 두 개를 수정하세요.

```text
FOUNDRY_PROJECT_ENDPOINT=https://리소스명.services.ai.azure.com/api/projects/프로젝트명
FOUNDRY_MODEL_DEPLOYMENT_NAME=실제-모델-배포이름
```

위 예시의 한글 설명을 그대로 사용하지 않습니다. **프로젝트 endpoint에 `/openai/v1`을 추가하지 않습니다.** SDK가 올바른 경로를 구성합니다. API key는 넣지 않습니다.

L08 전에 `.env`의 `FOUNDRY_JUDGE_DEPLOYMENT_NAME`도 관리자가 제공한 실제 judge 배포 이름으로 설정합니다. **프로젝트 endpoint에 `/openai/v1`을 추가하지 않습니다.** SDK가 올바른 경로를 구성합니다. API key는 넣지 않습니다.

```bash
az login
az account show --query "{subscription:name,tenant:tenantId}" -o table
```

다른 구독이면 명시적으로 선택합니다.

```bash
az account set --subscription "실습용-구독-ID"
```

샘플은 로컬에서 **AzureCliCredential**을 사용합니다. 운영 환경에서는 적절한 managed identity 등 배포 환경에 맞는 자격 증명을 선택해야 합니다.

## 성공 기준

프로젝트·모델·역할·지역·비용 담당자를 기록했고, 로컬 데이터 검사에 성공했습니다. Azure 연결 성공은 **다음 L03의 실제 응답**으로 별도 확인합니다.

## 막혔을 때

**403이면 먼저 역할, 404면 endpoint와 배포 이름, 429면 quota**를 확인합니다. private endpoint 환경이라면 승인된 VPN·VNet 내 개발 환경이 필요합니다. 문제 해결을 위해 public access를 임의로 켜지 마세요.

SDK 설치가 사내 미러에서 실패하면 허용된 미러의 동기화를 요청합니다. 최신 패키지가 공개 PyPI에 있다는 사실이 조직 정책을 무시하고 설치해도 된다는 뜻은 아닙니다.

## 정리

리소스 그룹과 담당자를 기록하고 L12의 종료 체크리스트를 미리 읽습니다. `.env`를 공유·커밋하지 않습니다. 이 실습의 `.env`에는 비밀이 없어야 합니다.
