> **완성할 결과:** 같은 Contoso 구매 질문을 순차·동시 실행으로 처리하고, 앞사람의 답을 전달하는 방식과 독립 분담의 차이를 설명합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 로컬에서 Agent Framework orchestration을 실행하고 승인된 Foundry 모델을 호출합니다. Hosted 배포는 하지 않습니다.

**먼저 할 일:** 별도 심화 환경을 준비하고 L02의 TPM/RPM 확인을 마친 뒤 실행할 패턴 하나의 계획을 읽습니다.

**확인할 결과:** 실제 참여 역할·전달 순서·모델 호출 수·답변·토큰·시간을 비교합니다. 에이전트의 답변은 업무 승인이 아닙니다.

</div>

## 목표

**같은 역할도 연결 방식에 따라 다르게 동작함을 경험합니다.** 여러 에이전트를 쓰는 것이 항상 더 빠르거나 정확하다는 뜻은 아닙니다.
이 모듈은 `agent_framework.orchestrations`의 공식 Builder를 사용합니다. Foundry 포털 Workflows와는 다른 코드 기반 실행이며, 포털 Workflows는 **2026-12-01 종료 예정**입니다.

## 개념과 실습 지도

**경험할 기능:** `SequentialBuilder`와 `ConcurrentBuilder`로 순차·동시 실행을 비교합니다.

**무엇이며 왜 중요한가요?** 오케스트레이션은 누가 다음에 작업할지와 어떤 대화·결과를 전달할지 정합니다. 순차는 연결, 병렬은 분담, 그룹 채팅은 반복 검토, 핸드오프는 담당자 전환에 적합합니다.

**어떻게 사용하나요?** 같은 정책·질문에서 `--mode`만 바꾸고 역할 순서와 실제 출력을 비교합니다. 검토 후 수정·담당자 전환은 [L14](#l15-collaboration)에서 별도로 진행합니다.

**어디서 실행하나요?** [multi_agent.py](../samples/multi_agent.py)를 별도 Python 환경에서 실행합니다. 모델만 Azure에 있으며, 원격 A2A나 실제 업무 승인 실습은 아닙니다.

## 준비

L01에서 내가 만든 프로젝트·모델·`.env`·`results/azure-environment.json`을 사용합니다. 프로젝트·언어·배포 이름이 다르면 진행하지 않습니다.
L13·L14는 **chat 배포만** 사용합니다. 한 명 기준 최소 권장값은 **100,000 TPM / 60 RPM**이며, 산정 가정과 설정 방법은 [L02](#l02-capacity)에 있습니다.

심화 SDK는 `requirements-advanced.txt`로 분리합니다. `agent-framework-foundry==1.13.1`은 `azure-ai-projects<2.7.0`을 요구하므로 기본 코스의 SDK 환경과 섞지 않습니다. `agent-framework-orchestrations==1.2.0`도 함께 설치합니다.

### 먼저 경로 정하기

| 지금 상태 | 진행할 단계 | 남길 결과 |
| --- | --- | --- |
| Azure 승인 없음 | 1단계 환경 준비 → 3단계 계획 읽기 | 역할·최대 호출 수 설명. 실제 응답은 미실행 |
| 모델·소유 기록·비용 승인 있음 | 1 → 2 → 3 → 4 → 5 | 같은 질문의 순차·동시 응답과 비교표 |

L01·L02의 `.env`와 자신의 소유 기록을 재사용하며 Hosted·Search는 필요하지 않습니다. **L06과 달리 실제 재고 함수는 호출하지 않고, 정책과 질문을 SDK agent 역할별로 검토하는 실습**입니다.

## 실행

### 1. 별도 SDK 환경 준비하기

```bash
python3.13 -m venv .venv-advanced
.venv-advanced/bin/python -m pip install -r requirements-advanced.txt
.venv-advanced/bin/python -m pip check
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python3.13 -m venv` | 기본 SDK와 별도의 심화 환경을 만듭니다. | 로컬 환경 생성. 기존 환경을 덮어쓰지 않습니다. |
| 2. `pip install -r requirements-advanced.txt` | Foundry 연동과 네 가지 orchestration Builder의 호환 조합을 설치합니다. | 패키지 다운로드만 수행하며 Azure를 호출하지 않습니다. |
| 3. `pip check` | 같은 심화 환경의 의존성을 확인합니다. | 충돌하면 실행 전에 해결합니다. |

</div>

Windows에서는 `.venv-advanced\Scripts\python.exe`를 사용합니다. 기존 심화 환경이 다른 Python 버전이면 새 폴더에 환경을 만듭니다.

### 2. 모델 처리량 확인하기

```bash
.venv-advanced/bin/python samples/model_capacity.py plan --roles chat
.venv-advanced/bin/python samples/model_capacity.py check --roles chat --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `model_capacity.py plan --roles chat` | 한 명이 한 실습을 진행하는 조건의 chat TPM/RPM 계획을 봅니다. | 로컬 계산이며 Azure 호출은 없습니다. |
| 2. `check --roles chat --live` | 소유 RG와 실제 배포의 `rateLimits`를 조회합니다. | 읽기 전용입니다. 최소치 미달이면 실패하며 모델 호출은 하지 않습니다. |

</div>

미달이면 자신의 변경 권한·quota·비용 범위를 확인하고 L02의 `apply`로 보정합니다. 이미 충분한 배포는 줄이지 않습니다. live 명령도 실제 한도를 재확인하므로 오래된 결과만 믿고 호출하지 않습니다.

### 3. 순차와 동시 실행의 계획 읽기

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode concurrent
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `multi_agent.py --mode concurrent` | 선택한 패턴의 역할과 호출 상한을 읽습니다. 아래 다른 mode도 같은 방식으로 계획을 볼 수 있습니다. | `--live`가 없으면 SDK 초기화·Azure 요청·실행 기록 생성이 없습니다. |

</div>

| mode | 실제 Builder | 흐름 | 모델 호출 상한 |
| --- | --- | --- | ---: |
| `sequential` | `SequentialBuilder` | 작성자 → 검토자 | 2 |
| `concurrent` | `ConcurrentBuilder` | 정책·금액·위험 검토를 병렬 수행 → 결과 모음 | 3 |

이 장은 위 두 패턴만 진행합니다. **GroupChatBuilder·HandoffBuilder는 L14**에서 같은 환경을 이어 사용하므로 지금 실행할 필요가 없습니다.

모든 패턴은 **180초, 응답당 최대 2,048토큰, 재시도 0회**입니다. 같은 배포에 여러 터미널을 동시에 실행하지 않습니다.
한 실행 안에서는 요청 시작을 최소 1초 간격·분당 최대 6회로 제한합니다. 다음 패턴은 **이전 실행을 시작한 뒤 1분 이상 지난 후** 진행하세요. 다른 학습자와 배포를 공유하면 L02에서 동시 학습자 수를 반영합니다.

### 4. 패턴을 하나씩 실행하고 결과 읽기

각 명령은 새 모델 호출입니다. 하나를 실행하고 결과를 읽은 뒤 다음 패턴으로 넘어갑니다. 이 장의 두 패턴은 합계 **최대 5회**, L14의 두 패턴까지 선택하면 합계 **최대 12회** 호출입니다.

**순차:** 검토자의 입력에 작성자의 실제 초안이 전달되는지 확인합니다.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode sequential --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode sequential --live` | 같은 정책·대화를 작성자와 검토자에게 순서대로 전달합니다. | 최대 2회 모델 호출. 실제 중간·최종 답을 보존합니다. |

</div>

**병렬:** 세 역할은 서로의 답을 먼저 읽지 않습니다. 합쳐진 결과가 자동 합의나 하나의 검증된 정답은 아닙니다.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode concurrent --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode concurrent --live` | 정책·금액·위험 담당자가 같은 질문을 독립적으로 처리합니다. | 최대 3회 호출. 시작 간격은 지키되 진행 중인 작업은 겹칠 수 있습니다. |

</div>

두 명령이 출력한 **`Evidence:` 파일을 편집기로 각각 엽니다.** 순차 결과에서는 `paths.sequential.stages`의 작성자 답과 검토자 입력을 연결합니다. 동시 결과에서는 `paths.concurrent.stages`의 세 역할이 서로의 답을 기다리지 않았는지 `input_authors`와 입력 원문으로 확인합니다. 구현은 `samples/multi_agent.py`의 `build_workflow`에 있습니다.

### 5. 전달·종료·비용을 비교하기

<div class="practice-block" markdown="1">

**직접 해보기:** 반환된 `paths`와 `Evidence:` 파일에서 다음 항목을 찾습니다. 예시값이 아니라 자신의 결과를 적습니다.

| 항목 | 확인할 내용 |
| --- | --- |
| `paths.<mode>.stages` | 실제 호출별 역할·답·응답 ID·토큰 |
| `input_authors`, `input_sha256` | 어떤 대화가 전달됐는지 확인할 단서 |
| `model_call_completed` 이벤트의 `payload.input` | 실제 입력 메시지와 지침. 순차에서는 작성자의 답이 검토자에게 전달됨 |
| `elapsed_seconds`, `total_tokens` | 실행 시간·호출 합계. 사용량 `null`은 0이 아닙니다. |
| `final_messages`, `workflow_state` | 동시 실행의 최종 결과 모음과 종료 상태 |

**한 가지 바꾸기:** 추가 호출을 승인받았다면 같은 mode에서 `--case boundary`만 추가합니다. 정확히 200만 원과 200만 1원의 승인 경계를 비교합니다. 모델·정책·역할 지침은 함께 바꾸지 않습니다.

**결과 설명하기:** `선택한 패턴 / 전달 순서 / 빠진 내용 / 종료 조건 / 추가 토큰·시간 / 이 패턴을 사용할 이유`를 적습니다. 금액·승인·미실행 주장을 정책과 대조하며, 에이전트 수가 많다는 이유로 품질 향상을 가정하지 않습니다.

</div>

<details class="optional-path" markdown="1">
<summary>선택: 단일 작성자와 순차 흐름 비교</summary>

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode compare --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode compare --live` | 같은 작성 지침·정책·질문으로 단일 답 1회와 순차 흐름 2회를 실행합니다. | 추가 최대 3회 호출. `sequential_minus_single`은 시간·토큰 차이지 품질 점수가 아닙니다. |

</div>

단일 경로가 먼저 실행되므로 인증·캐시·초기 지연이 다를 수 있습니다. 한 번의 차이를 일반적인 속도 우위로 해석하지 않습니다.

</details>

#### 포털 배포와 Python 오케스트레이션의 경계

포털은 **모델 배포**를 제공하지만 L13의 순차·동시 workflow 그래프를 설정하지 않습니다. 그 순서는 Python Agent Framework 코드가 만듭니다.

```python
from agent_framework.orchestrations import SequentialBuilder, ConcurrentBuilder

sequential = SequentialBuilder(
    participants=[drafter, reviewer],
    intermediate_output_from=[drafter],
).build()

concurrent = ConcurrentBuilder(
    participants=[policy_agent, budget_agent, risk],
    intermediate_output_from=[policy_agent, budget_agent, risk],
).build()
```

| Foundry/코드 위치 | 무엇을 조작하나요? |
| --- | --- |
| Portal → Models → Deployments | Python client가 호출할 모델 배포를 선택 |
| `build_role(...)` | 각 SDK agent의 instructions·모델 호출 역할을 정의 |
| `SequentialBuilder` | 작성자 출력을 검토자 입력으로 전달 |
| `ConcurrentBuilder` | 독립 역할을 동시에 실행하고 stage별 결과 수집 |
| `.venv-advanced`의 `multi_agent.py` | orchestration을 로컬에서 만들고, 승인 시 모델 요청만 Foundry에 전송 |

위 `drafter`·`reviewer`·`policy_agent`·`budget_agent`·`risk`는 `build_role()`로 instructions와 모델 client를 지정한 SDK agent입니다. `multi_agent.py`는 선택한 mode의 Builder 하나만 실행합니다. 이 설정은 포털에서 만든 workflow가 아니라 로컬 코드이며 `Evidence:`의 실제 입력·stage·출력으로 확인합니다.

## 성공 기준

순차의 실제 초안 전달과 동시 실행의 세 독립 결과를 구분하고, 선택해 실행한 패턴의 응답·시간·토큰을 설명할 수 있습니다.
검토자가 동의한 것을 사람 승인이나 자동 품질 합격으로 기록하지 않습니다. 계획만 읽었다면 모델 실행은 미실행입니다.

## 막혔을 때

`agent_framework_orchestrations` import 오류는 심화 환경의 설치 경로부터 확인합니다. TPM/RPM 미달이면 L02로 돌아가며, 429가 나오면 새 호출을 반복하지 않고 기존 오류·한도·다른 사용자의 동시 사용을 확인합니다.
입력 예산 초과나 응답 잘림은 실패입니다. 결과를 꾸미거나 상한을 무작정 늘리지 말고 대화 길이와 실제 응답을 확인합니다.

## 정리

이 모듈은 로컬 오케스트레이션과 모델 호출만 수행합니다. 다른 장에서 만든 Hosted 세션·예약은 별도이며 L19에서 정리합니다. 자신의 실행 결과는 `results/`에 보관하고 사용자·인증 정보를 공유하지 않습니다.
