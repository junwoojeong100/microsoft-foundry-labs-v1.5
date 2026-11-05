## 목표

Microsoft Agent Framework(MAF)의 **SequentialBuilder·ConcurrentBuilder를 실제 실행**하고 전달·분기·종료 기록을 읽습니다. 사람이 답변을 복사하는 실험으로 대체하지 않습니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 터미널의 실제 SDK + 기본 오프라인 fixture. 별도 승인하면 같은 코드에 기존 Microsoft Azure 모델을 연결합니다.

**먼저 할 일:** 전체 실습 ZIP의 저장소 루트에서 MAF 전용 환경을 만듭니다. **Hosted 배포·Search·judge·별도 Prompt Agent 생성은 필요 없습니다.**

**확인할 결과:** 순차 전달 2회, 독립 분기 3회의 실제 SDK 기록. fixture와 유료 모델 결과를 따로 보관합니다.

</div>

## 개념과 실습 지도

**경험할 기능:** 순차 검토와 동시 분기.

**무엇이며 왜 중요한가요?** Sequential은 초안을 다음 역할로 전달합니다. Concurrent는 같은 질문을 독립 분담하고 원문 3개를 남깁니다.

**어떻게 사용하나요?** 실제 builder를 오프라인으로 실행한 뒤 같은 역할·정책·질문을 승인된 모델로 비교합니다.

**어디서 실행하나요?** workflow와 Agent 객체는 **내 Python 프로세스**, 선택한 모델만 Microsoft Foundry입니다. 포털 Chat 두 창은 runtime 동시 실행이 아닙니다.

[![MAF 순차 2단계와 정책·금액·위험 3갈래 동시 실행 흐름도.](../assets/maf-patterns.svg)](../assets/maf-patterns.svg)

흐름도를 선택하면 원본 크기로 볼 수 있습니다. **기존 포털 영상에는 MAF 실행이 없습니다.** 관련 없는 Prompt 생성·복사 화면을 실행 증거로 붙이지 않습니다.

## 준비

Python **3.13**, 전체 ZIP의 `samples/`, `scripts/`, `data/`, `requirements-advanced.txt`가 필요합니다. 인터넷은 패키지 설치에만 필요하고 기본 fixture 실행에는 Microsoft Azure 로그인·`.env`·소유 receipt가 필요 없습니다.

L12의 `.venv-hosted`는 재사용하지 않습니다. Hosted의 `azure-ai-projects==2.7.0`과 이 장의 **2.6.0**은 충돌합니다. 두 requirements를 섞지 않고 `.venv-maf`를 사용합니다.

## 실행

### 1. MAF 환경을 선택하고 실제 builder 코드 읽기

macOS/Linux Bash·zsh:

```bash
python3.13 -m venv .venv-maf
source .venv-maf/bin/activate
python -m pip install -r requirements-advanced.txt
export FOUNDRY_LAB_LANGUAGE=ko
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python3.13 -m venv` | 루트에 MAF 전용 환경을 한 번 만듭니다. | 로컬 폴더. 기존 환경을 재생성하지 않습니다. |
| 2. `source` | 현재 터미널에서 MAF Python을 선택합니다. | Hosted 환경과 분리합니다. |
| 3. `pip install -r` | 고정 MAF 패키지와 SDK를 설치합니다. | 패키지 다운로드만 하며 모델을 호출하지 않습니다. |
| 4. `export` | 한국어 합성 정책·질문을 선택합니다. | 새 터미널에서는 다시 선택합니다. |

</div>

Windows PowerShell은 위 블록 **대신**:

```powershell
py -3.13 -m venv .venv-maf
.\.venv-maf\Scripts\Activate.ps1
python -m pip install -r requirements-advanced.txt
$env:FOUNDRY_LAB_LANGUAGE = "ko"
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `py -3.13 -m venv` | Python 3.13의 별도 환경을 만듭니다. | 로컬 준비만 수행합니다. |
| 2. `Activate.ps1` | MAF 환경을 선택합니다. | 실행 정책이 차단하면 보안을 바꾸지 말고 이후 `python` 대신 `.venv-maf\Scripts\python.exe`를 사용합니다. |
| 3. `pip install -r` | 이 환경에 advanced requirements만 설치합니다. | Hosted requirements를 추가하지 않습니다. |
| 4. `$env:` | 현재 터미널의 합성 자료 언어를 선택합니다. | 두 언어의 live 폴더·receipt는 별개입니다. |

</div>

이후 한 줄 `python` 명령은 두 셸에서 공통입니다. 새 터미널은 환경·언어만 다시 선택하며 설치를 반복하지 않습니다.

[multi_agent.py의 `build_workflow`](../samples/multi_agent.py)를 엽니다. 아래는 이미 정의된 역할을 연결하는 **읽기용 발췌**입니다. 이 블록만 따로 실행하지 않습니다.

```python
from agent_framework.orchestrations import ConcurrentBuilder, SequentialBuilder

sequential = SequentialBuilder(
    participants=[drafter, reviewer], intermediate_output_from=[drafter],
).build()
concurrent = ConcurrentBuilder(
    participants=[policy_agent, budget_agent, risk],
    intermediate_output_from=[policy_agent, budget_agent, risk],
).build()
```

`build_role`이 같은 합성 구매 정책을 각 역할에 넣고, `CallAudit` middleware가 실제 호출 ID·입력 hash·역할·시간·사용량을 남깁니다. 이 역할들은 로컬 SDK 객체이며 포털의 Prompt Agent 두 개를 만드는 과정이 아닙니다.

<div class="practice-block" markdown="1">

### 2. 먼저 순차 전달을 오프라인으로 실행

**직접 해보기:** SDK 검사와 실행 계획을 읽은 뒤 `--offline`으로 실제 workflow를 실행합니다.

```bash
python -m scripts.check_sdk --advanced
python samples/multi_agent.py --mode sequential
python samples/multi_agent.py --mode sequential --offline
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `scripts.check_sdk --advanced` | 실제 설치 SDK의 workflow·전달·비교 계약을 네트워크 차단 상태로 검사합니다. | `sdk_contracts: passed`, `azure_calls: 0`. 실제 모델 사용 아님. |
| 2. `--mode sequential` | 옵션과 호출 상한만 출력합니다. | `PLAN ONLY`이며 SDK workflow를 실행한 결과가 아닙니다. |
| 3. `--mode sequential --offline` | 진짜 `SequentialBuilder`에 고정 응답 client를 연결해 drafter → reviewer를 실행합니다. | 합성 응답 2회, 네트워크·DNS 차단, 비공개 `results/contoso-maf-fixture-....jsonl`. |

</div>

기본 `--case purchase`의 실제 질문은 다음입니다. 코드의 `QUESTIONS`와 비교하되 포털 Chat에 따로 보내지 않습니다.

```text
단가 145만 원인 노트북 2대를 구매하려 한다. 정책과 승인 절차를 안내해줘.
```

출력에서 확인할 필드의 발췌입니다. 응답 문장은 `Synthetic fixture from ...`이며 **정책 답변 품질·실제 토큰 청구의 측정값이 아닙니다.**

```output
"execution": "local_sdk_fixture"
"azure_calls": 0
"fixture_calls": 2
"usage_source": "synthetic_fixture_not_billing"
"quality_release": false
```

실행 로그의 reviewer `model_call_completed` 입력에 **drafter의 실제 fixture 응답**이 있는지 봅니다. 결과만 두 개 있다고 전달이 증명되는 것은 아닙니다.

### 3. 같은 질문을 동시 분기하고 기준선과 비교

```bash
python samples/multi_agent.py --mode concurrent --offline
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode concurrent --offline` | 같은 질문을 policy·budget·risk에 분기하고 각 원문을 보존합니다. | `fixture_calls: 3`, 역할 3개, `maximum_active_fixture_calls`로 로컬 중첩 확인. 요약 모델을 추가 호출하지 않습니다. |

</div>

**한 가지 바꾸기:** 질문·정책은 그대로 두고 단일 agent와 순차 경로의 비교 모드만 바꿉니다.

```bash
python samples/multi_agent.py --mode compare --offline
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode compare --offline` | single 1회와 sequential 2회를 같은 입력으로 실행합니다. | fixture 총 3회와 `sequential_minus_single`. 합성 usage 차이를 비용 절감이나 품질 개선이라고 하지 않습니다. |

</div>

**결과 설명하기:** 순차는 reviewer가 받은 초안, 동시는 독립 입력과 세 원문을 제시합니다. 호출 수·중첩·원문 전달과 답변 품질은 다른 검사입니다. fixture는 질문을 해석하는 모델이 아니므로 정책 정답률을 계산하지 않습니다.

</div>

<a id="maf-live-setup"></a>

### 4. 기존 Microsoft Foundry 모델로 실행 — 별도 승인

오프라인 결과와 분리된 선택 경로입니다. **새 프로젝트·agent·Hosted·Search를 만들지 않습니다.** L01/L02의 기존 chat 배포와 승인된 모델 호출만 필요합니다.

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | Azure portal에서 내 전용 RG의 Overview·Tags를 읽습니다. | L01의 정확한 구독·`validationRun`, `repository=microsoft-foundry-labs-v1.5`입니다. | repository 태그가 없으면 내 그룹의 태그 변경 승인 후에만 추가·저장합니다. 다른 그룹을 내 것으로 표시하지 않습니다. |
| 2 | Microsoft Foundry의 프로젝트 endpoint와 `Models → contoso-chat → Details`를 읽습니다. | 같은 account·project·모델 버전·Succeeded·실제 TPM/RPM입니다. | 이름만 같거나 용량이 부족하면 중단합니다. 자동 증액·다른 모델 대체 없음. |
| 3 | 루트의 `.env.example`을 `.env`로 복사해 아래 값을 바꿉니다. 기존 파일은 덮어쓰지 않습니다. | 프로젝트 endpoint와 실제 chat 배포 이름입니다. | 모델의 `/openai/v1` endpoint나 API key를 넣지 않습니다. |
| 4 | 기존 소유 receipt가 같은 scope·언어이면 재사용합니다. 없다면 아래 읽기 전용 adoption을 실행합니다. | `.env`·receipt·포털이 일치합니다. | 개인 메모를 임의 receipt로 작성하거나 `create`·`foundation`을 다시 실행하지 않습니다. |

```env
FOUNDRY_PROJECT_ENDPOINT=https://YOUR_RESOURCE.services.ai.azure.com/api/projects/YOUR_PROJECT
FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat
FOUNDRY_AUTH_MODE=cli
```

```bash
az login --tenant YOUR_TENANT_ID
python scripts/adopt_portal.py --subscription YOUR_SUBSCRIPTION_ID --resource-group YOUR_RESOURCE_GROUP --run-id YOUR_VALIDATION_RUN --live
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az login --tenant` | 승인 tenant ID로 바꾸고 열리는 브라우저에서 인증합니다. 이미 맞는 CLI 로그인은 재사용합니다. | 인증 화면·코드는 촬영하지 않습니다. |
| 2. `adopt_portal.py ... --live` | 모든 자리표시자를 내 값으로 바꿉니다. 기존 구독·RG 태그·account·project·chat을 5개 읽기 명령으로 확인합니다. | 로컬 소유 receipt만 생성. 자원 변경·모델 호출 없음, 기존 파일 덮어쓰기 없음. |

</div>

기본 두 경로는 최대 **2+3=5회**, 선택 `compare`까지 하면 추가 3회입니다. 한 실행은 180초·모델 호출당 출력 2048토큰·시작 최대 6회/분·재시도 0입니다. 별도 사전 용량 읽기는 최대 24요청/180초이며 용량을 변경하지 않습니다. 이 횟수는 금액 상한이 아니고 동시 사용자는 합산 예산이 필요합니다.

```bash
python samples/multi_agent.py --mode sequential --live
python samples/multi_agent.py --mode concurrent --live
```
<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode sequential --live` | receipt·실제 TPM/RPM 확인 후 기존 모델로 drafter → reviewer를 실행합니다. | 유료 모델 최대 2회. 실제 ID·usage·전달 입력을 보존합니다. |
| 2. `--mode concurrent --live` | 같은 모델·정책·질문을 policy·budget·risk에 분기합니다. | 유료 모델 최대 3회. 시작 간격 제한 때문에 모든 호출이 같은 순간 시작한다고 가정하지 않습니다. |

</div>

live의 `execution`은 `local_maf_with_azure_model`입니다. **workflow는 로컬, 모델 호출은 Microsoft Azure**이며 Foundry-hosted orchestration은 아닙니다. 로그의 `started_after_seconds`·`elapsed_seconds`로 실제 겹친 구간을 확인합니다. 누락된 usage의 `null`을 0으로 바꾸지 않습니다. 포털 Workflows·in-portal execution은 **2026-12-01 종료 예정**이므로 그 디자이너에 의존하지 않습니다.

## 성공 기준

실제 SDK의 순차 전달·동시 분기를 실행하고 역할별 원문을 찾았습니다. 오프라인은 `local_sdk_fixture`, live는 `local_maf_with_azure_model`로 구분했습니다. `PLAN ONLY`, fixture 사용량, 화면 예시를 Microsoft Azure 모델·품질 검증으로 세지 않았습니다. `quality_release`는 여전히 false입니다.

## 막혔을 때

SDK가 없으면 `.venv-maf`와 `requirements-advanced.txt`를 확인합니다. 출력이 `PLAN ONLY`이면 아직 실행하지 않은 것입니다. receipt·태그·TPM/RPM이 부족하면 live는 차단으로 남기고 offline으로 돌아옵니다. 429·부분 결과·중복 ID·시간 초과는 실패 원문을 보존하며 호출·토큰 상한을 늘려 통과시키지 않습니다.

## 정리

이 코드는 영구 agent·서버·원격 A2A를 만들지 않습니다. 실행 프로세스가 끝나도 기존 모델 배포·로그 자원은 남습니다. fixture와 live의 개인 `.jsonl`을 구분해 보관하고 커밋하지 않습니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 실행 종류, mode·case·정책 hash, 원문 전달·역할·호출 수·시간·usage의 근거와 미검증 한계.

**다음:** [L14 실제 MAF 그룹 채팅·핸드오프](#l15-collaboration). 같은 MAF 환경을 재사용합니다.

</div>
