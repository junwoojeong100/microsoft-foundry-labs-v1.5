> **완성할 결과:** 같은 Contoso 구매 질문을 순차·병렬·그룹 채팅·핸드오프로 처리하고 역할 간 전달 방식의 차이를 설명합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 로컬에서 Agent Framework orchestration을 실행하고 승인된 Foundry 모델을 호출합니다. Hosted 배포는 하지 않습니다.

**먼저 할 일:** 별도 심화 환경을 준비하고 L02의 TPM/RPM 확인을 마친 뒤 실행할 패턴 하나의 계획을 읽습니다.

**확인할 결과:** 실제 참여 역할·전달 순서·모델 호출 수·답변·토큰·시간을 비교합니다. 에이전트의 답변은 업무 승인이 아닙니다.

</div>

## 목표

**같은 역할도 연결 방식에 따라 다르게 동작함을 경험합니다.** 여러 에이전트를 쓰는 것이 항상 더 빠르거나 정확하다는 뜻은 아닙니다.
이 모듈은 `agent_framework.orchestrations`의 공식 Builder를 사용합니다. Foundry 포털 Workflows와는 다른 코드 기반 실행이며, 포털 Workflows는 **2026-12-01 종료 예정**입니다.

## 개념과 실습 지도

**경험할 기능:** 순차, 병렬, 그룹 채팅, 핸드오프 네 가지 오케스트레이션을 실행합니다.

**무엇이며 왜 중요한가요?** 오케스트레이션은 누가 다음에 작업할지와 어떤 대화·결과를 전달할지 정합니다. 순차는 연결, 병렬은 분담, 그룹 채팅은 반복 검토, 핸드오프는 담당자 전환에 적합합니다.

**어떻게 사용하나요?** 같은 정책·질문에서 `--mode`만 바꾸고 역할 순서와 실제 출력을 비교합니다. 승인된 요청 수와 종료 조건을 유지합니다.

**어디서 실행하나요?** [multi_agent.py](../samples/multi_agent.py)를 별도 Python 환경에서 실행합니다. 모델만 Azure에 있으며, 원격 A2A나 실제 업무 승인 실습은 아닙니다.

## 준비

L01의 프로젝트·모델·`.env`와 관리자가 제공한 `results/azure-environment.json`이 필요합니다. 프로젝트·언어·배포 이름이 다르면 진행하지 않습니다.
L15 자체는 **chat 배포만** 사용합니다. 한 명 기준 최소 권장값은 **100,000 TPM / 60 RPM**이며, 산정 가정과 설정 방법은 [L02](#l02-capacity)에 있습니다.

심화 SDK는 `requirements-advanced.txt`로 분리합니다. `agent-framework-foundry==1.13.1`은 `azure-ai-projects<2.7.0`을 요구하므로 기본 코스의 SDK 환경과 섞지 않습니다. `agent-framework-orchestrations==1.2.0`도 함께 설치합니다.

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

미달이면 관리자가 L02의 `apply` 경로로 먼저 용량을 맞춥니다. 이미 충분한 배포는 줄이지 않습니다. 실제 실행 명령도 다시 확인하므로 오래된 확인 파일만 믿고 호출하지 않습니다.

### 3. 네 가지 흐름의 계획 읽기

```bash
python samples/multi_agent.py --mode concurrent
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
| `group-chat` | `GroupChatBuilder` | 작성자 → 검토자 → 작성자 수정 | 3 |
| `handoff` | `HandoffBuilder` | 분류 담당자 → 정책 또는 금액 담당자로 제어 이전 | 4 |

모든 패턴은 **180초, 응답당 최대 2,048토큰, 재시도 0회**입니다. 같은 배포에 여러 터미널을 동시에 실행하지 않습니다.
한 실행 안에서는 요청 시작을 최소 1초 간격·분당 최대 6회로 제한합니다. 다음 패턴은 **이전 실행을 시작한 뒤 1분 이상 지난 후** 진행하세요. 다른 학습자와 배포를 공유하면 L02에서 동시 학습자 수를 반영합니다.

### 4. 패턴을 하나씩 실행하고 결과 읽기

각 명령은 새 모델 호출입니다. 하나를 실행하고 결과를 읽은 뒤 다음 패턴으로 넘어갑니다. 네 패턴을 모두 실행하면 합계 **최대 12회** 호출입니다.

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

**그룹 채팅:** 발언자를 정하는 코드는 round-robin입니다. 별도의 모델 기반 사회자 호출 없이 세 번의 발언 후 종료합니다.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode group-chat --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode group-chat --live` | 검토 내용을 받은 작성자가 다시 답하는 세 차례 대화를 실행합니다. | 최대 3회 호출. 종료 조건·호출 상한을 늘리지 않습니다. |

</div>

**핸드오프:** 분류 담당자가 실제 `handoff_to_…` 도구로 담당자를 바꿉니다. 말로만 “위임했다”고 답한 것은 성공이 아닙니다. 전문가는 답한 뒤 종료하는 역할이며 다시 위임하지 않습니다.

```bash
.venv-advanced/bin/python samples/multi_agent.py --mode handoff --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--mode handoff --live` | 허용된 정책·금액 담당자 중 하나로 대화 제어를 넘깁니다. | 최대 4회 호출. 실제 도구 호출과 전문가 응답이 없으면 실패합니다. 업무 승인·A2A 서버 호출은 없습니다. |

</div>

핸드오프 Agent에는 `require_per_service_call_history_persistence=True`가 필요합니다. 샘플이 이를 설정해 도구 호출로 제어가 바뀌어도 로컬 대화 기록을 유지합니다.
전체 구현은 `samples/multi_agent.py`의 `build_workflow`에서 네 Builder를 비교해 읽습니다. [그룹 채팅](https://learn.microsoft.com/agent-framework/workflows/orchestrations/group-chat?pivots=programming-language-python)과 [핸드오프](https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff?pivots=programming-language-python)의 공식 문서도 참고합니다.

### 5. 전달·종료·비용을 비교하기

<div class="practice-block" markdown="1">

**직접 해보기:** 반환된 `paths`와 `Evidence:` 파일에서 다음 항목을 찾습니다. 예시값이 아니라 자신의 결과를 적습니다.

| 항목 | 확인할 내용 |
| --- | --- |
| `paths.<mode>.stages` | 실제 호출별 역할·답·응답 ID·토큰 |
| `input_authors`, `input_sha256` | 어떤 대화가 전달됐는지 확인할 단서 |
| `model_call_completed` 이벤트의 `payload.input` | 실제 입력 메시지와 지침. 순차·그룹 채팅의 이전 답 전달 확인 |
| `handoff_calls` | 실제로 요청한 핸드오프 도구 이름 |
| `elapsed_seconds`, `total_tokens` | 실행 시간·호출 합계. 사용량 `null`은 0이 아닙니다. |
| `final_messages`, `workflow_state` | 병렬·그룹 채팅·핸드오프의 최종 메시지와 종료 상태 |

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

## 성공 기준

네 패턴의 역할 전달과 종료 조건을 구분하고, 선택해 실행한 패턴의 실제 응답을 설명할 수 있습니다.
핸드오프는 실제 제어 이전, 그룹 채팅은 세 발언, 병렬은 세 역할의 독립 결과를 확인합니다. 실제 업무 승인이나 원격 A2A를 완료한 것으로 기록하지 않습니다.

## 막혔을 때

`agent_framework_orchestrations` import 오류는 심화 환경의 설치 경로부터 확인합니다. TPM/RPM 미달이면 L02로 돌아가며, 429가 나오면 새 호출을 반복하지 않고 기존 오류·한도·다른 사용자의 동시 사용을 확인합니다.
입력 예산 초과나 응답 잘림은 실패입니다. 결과를 꾸미거나 상한을 무작정 늘리지 말고 대화 길이와 실제 응답을 확인합니다.

## 정리

이 모듈은 로컬 오케스트레이션과 모델 호출만 수행합니다. 다른 장에서 만든 Hosted 세션·예약은 별도이며 L12에서 정리합니다. 자신의 실행 결과는 `results/`에 보관하고 사용자·인증 정보를 공유하지 않습니다.
