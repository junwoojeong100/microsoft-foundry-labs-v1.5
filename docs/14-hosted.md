## 목표

포털에서 Hosted가 필요한 경계를 확인한 뒤 **소스 → 로컬 패키지 → 승인된 단일 서비스 배포 → 정확한 버전 1회 호출**을 따라갑니다. 포털로 할 수 없는 코드 작업을 수동 Chat으로 대신하지 않습니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 포털 + 터미널. 기본은 오프라인 빌드·SDK 검사이며 유료 배포·권한 변경·호출은 각각 승인된 선택 단계입니다.

**먼저 할 일:** 전체 실습 ZIP을 풀고 `azure.yaml`, `hosted/`, `samples/`, `scripts/`가 함께 있는 **저장소 루트**에서 터미널을 엽니다. 가벼운 포털 입력 ZIP에는 코드가 없습니다.

**확인할 결과:** 패키지 manifest와 검사 결과. 실제 실행을 선택했다면 원격 version·응답·세션 중지 기록까지 확인합니다.

</div>

## 개념과 실습 지도

**경험할 기능:** Hosted 코드 배포와 Invocations 요청.

**무엇이며 왜 중요한가요?** Prompt는 지시문·모델 설정, Hosted는 내 서버 코드입니다. 포털의 Save는 코드 배포가 아닙니다.

**어떻게 사용하나요?** 먼저 로컬 패키지를 확인하고, 승인된 기존 자원에만 한 서비스를 배포합니다.

**어디서 실행하나요?** 종류·자원은 포털, Python 코드·패키징·azd 배포는 터미널입니다. SDK 설치는 이 선택 심화에서만 필요합니다.

[![Hosted 소스·오프라인 패키지·승인된 배포·호출 흐름도. 로컬 서버도 Microsoft Azure를 호출합니다.](../assets/hosted-lifecycle.svg)](../assets/hosted-lifecycle.svg)

흐름도를 선택하면 원본 크기로 볼 수 있습니다. **기존 영상에는 Hosted 배포·호출이 없습니다.** 아래 포털 사진은 개발 경계만 보여 주며 터미널 절차를 촬영한 화면이 아닙니다.

## 준비

Python **3.13**이 필요합니다. 실제 연결에는 Azure CLI, Azure Developer CLI(azd)와 `azure.ai.agents` extension, 기존 L01 프로젝트·L02 모델, 승인된 전용 Search 서비스와 **1536차원으로 호출 가능한 embedding 배포**가 추가로 필요합니다. 개발 skill·Docker·ACR 설치는 이 코드 배포의 학습자 전제 조건이 아닙니다.

Hosted는 `requirements-hosted.txt`의 `azure-ai-projects==2.7.0`, MAF는 `requirements-advanced.txt`의 **2.6.0**을 씁니다. **두 requirements를 한 환경에 설치하지 않습니다.** 이 장은 `.venv-hosted`, L13은 별도 `.venv-maf`입니다.

## 실행

### 1. 포털에서 코드가 필요한 지점 확인

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | 내 프로젝트의 `Build → Agents`에서 `Type`을 읽습니다. | 현재 `contoso-policy`는 Prompt입니다. | Running을 Hosted 배포로 해석하지 않습니다. |
| 2 | `New agent → Code an agent`를 열어 framework·hosting 안내를 읽고 `Cancel`로 돌아옵니다. | 여기서부터 개발 코드가 필요합니다. 아래 2절로 이동합니다. | 새 Prompt Agent를 만들어 Hosted를 실행했다고 하지 않습니다. |

<div class="screen-step" markdown="1">

**목록: 이름보다 Type부터**

![실제 목록의 Version, Prompt Type, New agent 버튼.](../assets/portal/steps/agents-type-list.png)

**1 Version / 2 Type:** 사진의 세 대상은 모두 Prompt입니다. **3 New agent:** Code an agent 경로를 찾는 위치이며 Hosted 실행 결과는 아닙니다.

[자막 영상 05 · 02:23](../downloads/portal/index.html?clip=05-inspection-retention&t=143&lang=ko#05-inspection-retention)

</div>

<div class="screen-step" markdown="1">

**Code agent: 이다음은 터미널**

![Code agent의 framework·hosting 안내와 Cancel.](../assets/portal/steps/hosted-dialog.png)

**1 개발 경로:** 이번에는 관찰에서 끝내지 않고 체크인 소스로 이어갑니다. **2 Cancel:** 포털 창만 닫고 2절로 이동합니다. 이 녹화 자체의 배포·호출은 여전히 0회입니다.

[자막 영상 05 · 02:19](../downloads/portal/index.html?clip=05-inspection-retention&t=139&lang=ko#05-inspection-retention)

</div>

### 2. 터미널에서 전용 환경과 패키지 확인 — 오프라인

macOS/Linux의 Bash·zsh에서는:

```bash
python3.13 -m venv .venv-hosted
source .venv-hosted/bin/activate
python -m pip install -r requirements-hosted.txt
export FOUNDRY_LAB_LANGUAGE=ko
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python3.13 -m venv` | 루트에 Hosted 전용 환경을 한 번 만듭니다. | 로컬 폴더만 생성. 기존 환경이 있으면 재생성하지 않습니다. |
| 2. `source` | 현재 터미널의 Python을 해당 환경으로 선택합니다. | Microsoft Azure 로그인 아님. |
| 3. `pip install -r` | 체크인한 Hosted SDK 버전을 설치합니다. | 패키지 다운로드이며 자원 배포·모델 호출 없음. |
| 4. `export` | 이번 터미널의 합성 자료 언어를 선택합니다. | 한국어·영어 실습 폴더와 receipt를 섞지 않습니다. |

</div>

Windows PowerShell에서는 **위 블록 대신**:

```powershell
py -3.13 -m venv .venv-hosted
.\.venv-hosted\Scripts\Activate.ps1
python -m pip install -r requirements-hosted.txt
$env:FOUNDRY_LAB_LANGUAGE = "ko"
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `py -3.13 -m venv` | Python 3.13으로 전용 환경을 만듭니다. | 한 번만 실행하는 로컬 준비. |
| 2. `Activate.ps1` | 현재 터미널에서 환경을 선택합니다. | 실행 정책이 차단하면 보안을 바꾸지 말고 이후 `python` 대신 `.venv-hosted\Scripts\python.exe`를 사용합니다. |
| 3. `pip install -r` | Hosted 의존성만 설치합니다. | MAF requirements는 추가하지 않습니다. |
| 4. `$env:` | 현재 터미널의 자료 언어를 선택합니다. | 다른 터미널에는 자동 적용되지 않습니다. |

</div>

이후 `python`·`az`·`azd` 한 줄 명령은 두 셸에서 공통입니다. 새 터미널에서는 해당 환경·언어만 다시 선택하며 설치를 반복하지 않습니다.

| 먼저 열어 볼 원본 | 무엇을 확인하나요? |
| --- | --- |
| [hosted/main.py](../hosted/main.py) | `InvocationAgentServerHost`, `/invocations`, 입력 검사·동시 1건 처리·실패 HTTP 응답 |
| [samples/hosted_runtime.py](../samples/hosted_runtime.py) | 실제 Search 근거, 합성 재고·초안 함수, 요청별 도구 권한 검사. 주문·결제·승인 없음 |
| [azure.yaml](../azure.yaml) | 아래 서비스의 코드 entrypoint·protocol·0.5 CPU/1Gi. Responses 서비스는 별도 |

원본에서 읽을 핵심 설정입니다. 새 YAML로 덮어쓰거나 이 발췌만 배포하지 않습니다.

```yaml
codeConfiguration:
  runtime: python_3_13
  entryPoint: main.py
  dependencyResolution: remote_build
protocols:
  - protocol: invocations
    version: 1.0.0
```

```bash
python scripts/build_hosted.py
python -m scripts.check_sdk
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `build_hosted.py` | 합성 원본·허용 파일·고정 의존성을 두 protocol 패키지로 묶습니다. | `.build/contoso/package-manifest.json`과 Responses 패키지. **둘 다 로컬 파일이며 배포 아님.** |
| 2. `scripts.check_sdk` | credential·네트워크를 사용하지 않고 설치된 SDK 계약을 검사합니다. | `sdk_contracts: passed`, `azure_calls: 0`. 실제 Microsoft Azure 성공이나 품질 통과 아님. |

</div>

`.env`가 아직 없으면 패키지의 모델 설정은 `CONFIGURE-MODEL-BEFORE-DEPLOY`입니다. 오프라인 빌드는 가능하지만 **그대로 배포·호출하지 않습니다.** 여기까지만 선택했다면 5절과 성공 기준으로 갑니다.

<a id="l12-azd"></a>

### 3. 기존 포털 환경 연결 — 승인된 선택 경로

**새 그룹·프로젝트를 만들지 않습니다.** 포털의 개인 메모는 CLI receipt가 아닙니다. 기존 `results/azure-environment.json`이 같은 범위·언어와 일치하면 재사용하고 아래 adoption을 반복하지 않습니다.

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | Azure portal에서 내 전용 RG의 Overview·Tags를 엽니다. | L01의 `validationRun`과 `repository=microsoft-foundry-labs-v1.5`입니다. | repository 태그가 없으면 **내 그룹의 태그 변경이 승인된 경우만** 추가·저장합니다. 다른 그룹에 소유 태그를 붙이지 않습니다. |
| 2 | Microsoft Foundry의 프로젝트 endpoint와 Models의 실제 배포 이름을 대조합니다. | `contoso-chat`, 승인된 embedding, 같은 account·구독입니다. | 자동으로 관찰된 ada-002를 호환 embedding이라고 가정하지 않습니다. |
| 3 | 파일 탐색기/편집기에서 `.env.example`을 `.env`로 복사하고 아래 자리표시자를 내 값으로 바꿉니다. 기존 `.env`는 덮어쓰지 않습니다. | 비밀 없이 endpoint·이름만 있습니다. | API key·토큰·비밀번호를 넣지 않습니다. |

```env
FOUNDRY_PROJECT_ENDPOINT=https://YOUR_RESOURCE.services.ai.azure.com/api/projects/YOUR_PROJECT
FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat
FOUNDRY_SEARCH_ENDPOINT=https://YOUR_SEARCH_SERVICE.search.windows.net
FOUNDRY_SEARCH_INDEX=
FOUNDRY_KNOWLEDGE_BASE=
FOUNDRY_EMBEDDING_DEPLOYMENT_NAME=YOUR_EMBEDDING_DEPLOYMENT
FOUNDRY_EMBEDDING_ENDPOINT=https://YOUR_RESOURCE.openai.azure.com
FOUNDRY_AUTH_MODE=cli
```

Search는 L11에서 승인한 **기존 전용 서비스**입니다. 이 Hosted 구현은 임의의 포털 index가 아니라 체크인 정책 절·hash·1536차원 schema를 요구합니다. 처음 초기화할 때 index·knowledge base 값은 비워 두며, 이미 같은 코드로 만든 `results/search.json`이 있으면 재사용합니다. 내 사용자에게 해당 서비스의 Search Service Contributor·Search Index Data Contributor와 모델 호출 권한이 있어야 합니다. 부족하면 최소 scope의 별도 권한 승인을 받고, 키나 공유 서비스로 우회하지 않습니다.

로그인이 없으면 아래 명령이 브라우저 창을 엽니다. 로그인·인증 코드는 녹화하지 않습니다.

```bash
az login --tenant YOUR_TENANT_ID
python scripts/adopt_portal.py --subscription YOUR_SUBSCRIPTION_ID --resource-group YOUR_RESOURCE_GROUP --run-id YOUR_VALIDATION_RUN --search-service YOUR_SEARCH_SERVICE --embedding-deployment YOUR_EMBEDDING_DEPLOYMENT --live
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az login --tenant` | 자리표시자를 승인 조직 ID로 바꾸고 브라우저에서 인증합니다. 이미 맞는 계정이면 생략합니다. | CLI 인증 캐시. 다른 조직·구독 기본값을 임의 변경하지 않습니다. |
| 2. `adopt_portal.py ... --live` | 모든 `YOUR_...`를 내 값으로 바꿉니다. 기존 RG 태그·account·project·chat·Search·embedding을 최대 7개 읽기 명령으로 확인합니다. | 비공개 소유 receipt 생성. 자원 생성·권한 부여·모델 호출 **0**. 기존 receipt는 덮어쓰지 않습니다. |

</div>

**다음은 읽기 전용이 아닙니다.** 정책 index·knowledge source·knowledge base 생성과 embedding 1배치 비용을 승인한 경우에만 첫 줄을 한 번 실행합니다. 이미 이 코드의 정상 `search.json`이 있으면 첫 줄은 생략합니다.

```bash
python samples/search_lab.py initialize --live
python scripts/build_hosted.py
python scripts/configure_hosted.py
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `search_lab.py initialize --live` | 기존 Search에 합성 3정책의 절·벡터·knowledge source/base를 만듭니다. 요청 상한 15, 300초입니다. | Microsoft Azure 데이터 쓰기·embedding 과금. 별도 Search 서비스를 만들지는 않습니다. |
| 2. `build_hosted.py` | 수정한 `.env`의 실제 모델 이름으로 **다시** 패키징합니다. | `.agent_configs/baseline/metadata.yaml`의 실제 모델과 manifest의 파일 hash를 확인합니다. |
| 3. `configure_hosted.py` | 검증된 receipt와 `.env`·Search 설정을 일치시켜 로컬 azd 환경을 연결합니다. | `.azure/`만 구성. provision·배포·권한 변경 아님. |

</div>

### 4. 한 서비스만 배포하고 정확한 버전 호출 — 별도 승인

배포·runtime 최소 권한·invocation **각 범위가 승인되어야** 진행합니다. 대상은 `contoso-purchasing` 하나입니다. 서비스 이름 없는 `azd deploy`·`azd up`은 두 서비스를 함께 배포할 수 있으므로 사용하지 않습니다.

```bash
azd deploy contoso-purchasing --timeout 1200
azd ai agent show contoso-purchasing --output json
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `azd deploy contoso-purchasing` | `azure.yaml`의 Invocations 코드 서비스 하나만 배포합니다. 최대 대기 1200초입니다. | 유료 Hosted compute 생성/변경. timeout은 Microsoft Azure 작업 취소가 아니므로 재배포하지 말고 상태를 확인합니다. |
| 2. `azd ai agent show` | 같은 서비스의 실제 version·endpoint·상태를 읽습니다. | 정확한 숫자 version을 개인 기록에 보관. Prompt 저장 버전이나 `latest`를 쓰지 않습니다. |

</div>

runtime identity의 프로젝트 역할·Search Index Data Reader·account의 Cognitive Services OpenAI User가 **각 최소 scope에서 별도로 승인된 경우만** 다음을 실행합니다. 이미 같은 할당이 있으면 반복하지 않습니다.

```bash
python scripts/runtime_roles.py --agent contoso-purchasing --live
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `runtime_roles.py ... --live` | 소유 receipt의 agent identity에 프로젝트·Search·모델 scope의 최소 역할 3개를 설정합니다. | **접근 권한 변경**입니다. 승인·roleAssignments/write가 없으면 중단하며 구독 전체 역할을 주지 않습니다. |

</div>

`YOUR_DEPLOYED_VERSION`을 위에서 확인한 **숫자**로 바꾸고 한 번만 호출합니다.

```bash
python samples/hosted_client.py invoke --version YOUR_DEPLOYED_VERSION --live
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `hosted_client.py invoke` | 고정 version의 내 세션에서 NB-14 2개를 조회하고 합성 구매 초안만 요청합니다. | 유료 호출 **1건**이며 내부 모델·검색 요청도 과금됩니다. runtime 예산은 요청 12·토큰 60,000·300초, 도구 최대 8개입니다. 원문·오류를 보존하고 자신의 세션만 중지·확인합니다. |

</div>

`results/contoso-hosted-client-...-responses.jsonl`의 `status`, `response_id`, `citations`, `tool_calls`, `contract.sha256`를 읽고 `...jsonl` 실행 로그의 `stopped_session`을 확인합니다. 초안은 `draft_requires_human_approval`, 실제 주문은 `order_submitted=false`여야 합니다. `evaluate`나 holdout 수집은 이 실습에서 실행하지 않습니다.

### 5. 로컬 서버를 시험한다면 — 오프라인 아님

원격 invocation **대신** 선택할 수 있습니다. 3절의 실제 Search·모델·권한과 `.env`가 필요합니다. **터미널 A**에서 Hosted 환경·언어를 선택한 뒤:

```bash
python scripts/run_hosted_local.py --protocol invocations --port 8088
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `run_hosted_local.py` | 생성 패키지의 실제 서버를 `127.0.0.1:8088`에 실행합니다. | 서버를 계속 켜 둡니다. 터널·공개 바인딩을 만들지 않습니다. |

</div>

**터미널 B**에서도 같은 Hosted 환경·언어를 선택하고, 유료 호출 1건을 승인한 뒤:

```bash
python samples/hosted_client.py invoke --local --live
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `invoke --local --live` | 로컬 `/invocations`에 1건을 보냅니다. 서버 내부는 Azure AI Search와 Microsoft Azure 모델을 호출합니다. | **로컬 실행 + Microsoft Azure backend**이며 원격 Hosted 배포 성공은 아닙니다. 완료 후 터미널 A에서 Ctrl+C로 서버를 멈춥니다. |

</div>

Invocations 성공은 별도 `contoso-purchasing-responses`의 **Responses 2.0.0**, Voice, Teams `activity` 성공을 뜻하지 않습니다. 이 장의 코드 배포와 포털 Chat 화면을 같은 실행면으로 취급하지 않습니다.

## 성공 기준

| 실제로 마친 경로 | 남겨야 할 결과 | 주장하지 않을 것 |
| --- | --- | --- |
| 오프라인 빌드·SDK 검사 | manifest·설치 버전·`azure_calls: 0` | Microsoft Azure 배포·도구 실행·품질 통과 |
| 선택 로컬 서버 호출 | 실제 응답·계약·검색/도구 원문, 로컬 실행 표시 | 원격 Hosted 배포 성공 |
| 선택 원격 배포·호출 | 정확한 서비스/version·응답 원문·세션 중지 확인 | 주문·결제·업무 승인·다른 protocol 성공 |

## 막혔을 때

의존성 충돌은 Hosted와 MAF 환경을 분리했는지 확인합니다. receipt가 없으면 기존 포털 scope를 검증하며 `create`·`foundation`으로 중복 생성하지 않습니다. 검색 hash/schema 불일치는 임의 포털 index를 재사용했는지 확인합니다. 403은 사용자와 runtime의 권한을 나누어 확인하고 키·public access로 우회하지 않습니다. 실패·429·timeout에는 원문을 남기고 자동 재시도하지 않습니다.

## 정리

로컬 서버는 Ctrl+C, 원격 세션은 호출기가 **자기 세션만** 중지하며 삭제하지 않습니다. 중지 확인 실패는 종료 성공이 아닙니다. 중지되지 않은 자신의 세션은 [stop_sessions.py](../scripts/stop_sessions.py)의 소유 기록 검증 절차로 담당자와 처리합니다. 세션 중지와 agent/compute·Search·파일·로그의 전체 과금 종료는 다르므로 L19에 인계합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 소스·패키지 contract와 실행 경로 구분. 선택 live는 scope·버전·원문·권한·세션 종료 상태까지 비공개 보관합니다.

**다음:** [L13 실제 MAF 순차·동시 실행](#l15). Hosted 배포 없이 별도 MAF 환경에서 시작할 수 있습니다.

</div>
