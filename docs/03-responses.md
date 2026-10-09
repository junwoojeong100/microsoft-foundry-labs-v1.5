> **완성할 결과:** 내가 배포한 모델에 질문 한 번을 보내고 실제 답변·상태·response ID를 확인합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 기본은 Python SDK로 1회 실행 · 포털은 설정 확인용이며 대체 실행도 가능합니다.

**먼저 할 일:** L02에서 확인한 `contoso-chat`을 Playground의 Model과 Python의 `model` 인수에서 찾습니다.

**확인할 결과:** 완료된 응답과 ID, 제공하지 않은 회사 규정을 지어내지 않는 답변을 확인합니다.

</div>

## 목표

**가장 작은 모델 호출을 이해합니다.** 아직 agent·문서 검색·함수 도구는 없습니다. 요청하는 코드와 화면 설정의 관계를 먼저 읽고 실행합니다.

## 개념과 실습 지도

**경험할 기능:** Responses API로 질문 한 개를 보내고 답변을 읽습니다.

**무엇이며 왜 중요한가요?** API는 프로그램이 서비스에 요청하는 방법입니다. `response_id`는 한 생성 작업을 찾는 식별자이며 conversation ID와 다릅니다.

**어떻게 사용하나요?** 모델·질문·출력 한도를 확인하고 기본 Python 명령으로 실행합니다. 포털을 대체 경로로 선택했다면 중복 호출하지 않습니다. 회사 정책을 주지 않았다면 모른다고 답하는 것이 정상입니다.

**어디서 실행하나요?** 포털의 모델 Playground와 [first_response.py](../samples/first_response.py)를 사용합니다. 포털이 내 Python 파일을 실행하는 것은 아니며 두 경로가 같은 모델 서비스를 호출합니다.

## 준비

L01의 로그인·가상환경·`.env`, L02의 준비된 배포를 사용합니다. 모델 호출 권한과 1회 요청의 비용 범위를 확인하세요. 이 예제는 Microsoft Azure public cloud를 대상으로 하며 sovereign cloud는 해당 인증·도메인 설정이 별도로 필요합니다.

## 실행

### 1. 포털의 설정과 Python 인수 대조하기

**기본 경로는 여기서 Send를 누르지 않고 2단계의 Python 명령으로 실행합니다.** 포털로 대신 호출할 경우에만 아래 질문을 Chat에 보내며 Python의 `--live`는 생략합니다. 접힌 SDK 코드 발췌는 읽기용 참고입니다.

**Build → Models → Deployments → contoso-chat → Playground**를 엽니다. **Save as agent**는 누르지 않습니다. 추가 instructions·검색 도구가 없는 모델 호출 상태를 확인합니다.

![모델 응답 예시. 질문에 포함된 합성 Contoso 규칙에 따라 정확히 200만 원일 때 팀장 승인이 필요하다고 답한다. Tools에는 추가 도구가 없다.](../assets/portal/16-model-response.png)

사진의 모델·질문은 화면 설명용입니다. 실제로는 자신의 프로젝트·배포를 선택하고 아래 기본 질문을 사용합니다.

```prompt
회사 내부 규정이 제공되지 않았을 때 어떻게 답해야 하나요?
```

![출력 한도 설정 예시. 모델 Playground의 Parameters에서 Max Completion Tokens가 256으로 설정되어 있다.](../assets/portal/17-model-parameters.png)

| 포털에서 조작 | Python 인수·결과 |
| --- | --- |
| Model에서 자신의 배포 선택 | `model=deployment_name` |
| Chat에 질문 입력 | `input=question` |
| Parameters → Max Completion Tokens | `max_output_tokens=512` |
| Send로 서비스 요청 | `client.responses.create(...)` |
| 응답 본문·ID 확인 | `response.output_text`, `response.id` |

사진의 256은 예시입니다. 이 실습의 코드와 같은 예산으로 비교하려면 512로 설정하고 불필요한 **Web search** 등 도구를 끕니다. 모델이 지원하지 않는 Temperature/Top P를 임의로 추가하지 않습니다.

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 실제 SDK 호출 코드 읽기 — 실행은 아래 2단계 명령으로 합니다</summary>

<a id="l03-2-실제-sdk-호출-코드-읽기"></a>

### 실제 SDK 호출 코드 읽기

다음은 연결 → 요청 → 응답 검사를 직접 쓴 코드입니다. 프로젝트·배포 값은 자리표시자이며 `client`·`response`가 어느 줄에서 만들어지는지 따라갑니다. **이 블록은 읽기용**입니다. 실제 실행은 다음 단계의 `--live` 명령으로 한 번만 합니다.

```python
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

project_endpoint = "https://<resource>.services.ai.azure.com/api/projects/<project>"
deployment_name = "contoso-chat"
question = "회사 내부 규정이 제공되지 않았을 때 어떻게 답해야 하나요?"

with (
    AzureCliCredential(process_timeout=30) as credential,
    AIProjectClient(
        endpoint=project_endpoint,
        credential=credential,
        retry_total=0,
    ) as project,
    project.get_openai_client(max_retries=0, timeout=60.0) as client,
):
    response = client.responses.create(
        model=deployment_name,
        input=question,
        max_output_tokens=512,
        store=False,
    )

if response.status != "completed" or not response.output_text or not response.output_text.strip():
    raise RuntimeError(f"Response not complete: {response.status}")

print(response.output_text)
print(f"response_id={response.id}")
```

`AzureCliCredential`은 L01의 CLI 인증을 사용하고, `AIProjectClient`는 Project endpoint에 연결합니다. `get_openai_client()`로 요청 client를 얻고 `responses.create()`가 모델에 질문을 보냅니다. `store=False`는 response 저장 옵션이지 모든 서비스 로그·abuse monitoring·데이터 보존을 끄는 설정이 아닙니다.

실행 파일은 같은 요청에 `.env` 읽기, 입력 길이 검사, `--live` 확인을 추가합니다. `read_config()`와 `ensure_response()`는 공통 설정·상태 검사이며 모델 요청을 숨겨서 추가 실행하지 않습니다.

</details>

<a id="l03-3-계획-확인-후-한-번-실행하기"></a>

### 2. 계획 확인 후 한 번 실행하기

```bash
python samples/first_response.py
```

<div class="command-explanation" markdown="1">

**명령 해설 — 먼저 전송 없이 질문을 확인합니다.**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `first_response.py` | 기본 질문과 `PLAN ONLY`를 출력합니다. | Microsoft Azure 요청·설정 검증·로그인 없음. |

</div>

**여기서 멈춰 확인:** 계획에 나온 질문이 맞고 `.env`의 프로젝트·배포와 1회 호출 비용 범위를 확인했다면 다음을 실행합니다. 포털에서 이미 Send를 눌렀다면 **이 명령은 건너뛰고 그 응답을 읽습니다.**

```bash
python samples/first_response.py --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `first_response.py --live` | `.env`의 프로젝트·배포에 질문 한 개를 보냅니다. | 출력 최대 512토큰·SDK 자동 재시도 0회·요청 timeout 60초. 실제 추론 비용이 발생하며 agent/store를 만들지 않습니다. |

</div>

포털 실행과 Python 실행은 각각 별도 요청이며, 같은 질문도 ID와 답이 달라질 수 있습니다.

답변·완료 상태·`response_id`를 기록합니다. 회사 내부 정책을 제공하지 않았으므로 특정 상한이나 재고를 단정하지 않아야 합니다. 포털에서 ID를 표시하지 않는다면 미확인으로 남기며 임의 ID를 만들지 않습니다.

`first_response.py`는 **터미널에 출력만 하며 결과 파일을 자동 저장하지 않습니다.** 자신의 비공개 진행 기록에 질문·배포·답변·ID를 남기세요. L10에서 쓸 응답 JSONL은 L06의 통합 실행이 따로 만듭니다.

<a id="l03-4-입력-하나-바꿔-보기"></a>

### 3. 입력 하나 바꿔 보기

먼저 전송 없이 질문만 바꿉니다.

```bash
python samples/first_response.py --query "회사 규정이 없는데 노트북 구매 상한을 단정할 수 있나요?"
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--query` | 따옴표 안의 질문을 이 실행의 입력으로 선택합니다. | `--live`가 없어 화면에만 표시됩니다. 추가 추론 없음. |

</div>

실제 답변 비교가 필요하면 비용 범위를 확인한 뒤 선택한 경로로 **추가 1회**만 보냅니다. 문장 일치가 아니라 미확인 정책을 유보했는지를 비교합니다. 사진과 같은 답을 만들려고 반복하지 않습니다.

<details class="optional-path" markdown="1">
<summary>선택 참고: 스트리밍·구조화 출력·이미지 입력</summary>

| 기능 | 비교할 것 |
| --- | --- |
| Streaming | 첫 출력 시간과 최종 완료 시간을 구분 |
| Structured outputs | JSON parse·schema·타입 검사를 모두 확인 |
| Embeddings | 검색용 벡터이지 답변 생성이 아님 |
| Vision | 지원 모델의 합성 영수증 입력을 원본 가격·수량과 비교 |

모델별 API·도구 지원이 다르므로 새 옵션을 추가하기 전에 모델 카드와 공식 SDK 예제를 확인합니다.

</details>

## 성공 기준

- 선택한 포털 또는 Python 요청에서 실제 답변을 받았습니다.
- 질문·배포 이름과 가능한 상태·ID를 기록했습니다.
- Python 경로는 완료 상태와 비어 있지 않은 텍스트 검사를 통과했습니다.
- 계획만 봤다면 모델 호출은 **미실행**입니다.

## 막혔을 때

| 증상 | 먼저 확인할 것 | 다음 행동 |
| --- | --- | --- |
| 미완료·빈 응답 | 출력 한도·거절 여부·배포 이름 | 성공으로 기록하지 않고 원인을 확인합니다. |
| 인증·권한 오류 | 로그인 상태·모델 호출 권한·`.env`의 배포 이름 | L01·L02에서 확인한 값과 대조합니다. |
| 429 | quota와 호출 한도 | 자동으로 반복하지 않고 한도를 확인합니다. |
| 포털과 Python의 답·ID가 서로 다름 | 두 실행은 별도 요청 | 서로의 결과를 다시 보는 명령이 아니므로 각각 기록합니다. |

## 정리

모델 배포는 유지합니다. 이 실습은 별도 agent·vector store를 만들지 않습니다. 다음 L04에서 역할·지시문을 가진 agent를 만듭니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 질문·배포 이름·실제 답변·완료 상태·확인 가능한 `response_id`. 터미널 출력은 비공개 진행 기록에 저장합니다.

**다음:** [L04 역할을 정한 에이전트](#l04). 같은 모델을 사용하되 새 Prompt Agent를 만듭니다.

</div>
