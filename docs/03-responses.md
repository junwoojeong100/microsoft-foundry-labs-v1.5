> **완성할 결과:** API key 없이 Foundry 모델을 호출하고, 응답과 response ID를 확인합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 터미널 · 계획 확인 후 승인된 모델 호출 1회가 기본입니다.

**먼저 할 일:** L01의 환경을 선택하고 `python samples/workshop.py model`로 계획을 확인합니다.

**확인할 결과:** 실제 호출의 답변과 `response_id`를 기록합니다. 사진과 똑같은 응답을 만들려고 반복 전송하지 않습니다.

</div>

## 목표

모델을 호출하는 가장 작은 단위를 이해합니다. **아직 agent도, RAG도 아닙니다.**

## 개념과 실습 지도

**경험할 기능:** 코드에서 모델에 질문 한 번을 보내는 Responses API입니다.

**무엇이며 왜 중요한가요?** API는 프로그램이 서비스에 요청하는 방법입니다. 결과에는 답변과 요청 식별자 `response_id`가 있습니다. 식별자는 나중에 같은 실행을 찾는 데 사용합니다.

**어떻게 사용하나요?** 계획을 읽고 승인된 호출을 한 번 실행합니다. 답변·완료 상태·ID를 확인합니다. 회사 문서를 주지 않았으므로 규정을 모른다고 답하는 것이 정상입니다.

**어디서 실행하나요?** 터미널에서 [samples/workshop.py](../samples/workshop.py)를 실행합니다. 아래 Python 발췌는 **읽을 코드**이며 터미널에 별도로 붙여넣지 않습니다.

## 준비

L01의 `.env`, 로그인, `requirements.txt` 설치와 L02의 준비된 배포가 필요합니다. 이 경로는 Azure public cloud 프로젝트를 대상으로 합니다. Government 등 sovereign cloud endpoint는 별도 공식 인증·도메인 설정을 적용해야 합니다.

## 실행

### 선택: 포털 화면으로 입력과 응답 이해하기

**기본 경로는 바로 아래 1–3단계의 터미널 실습입니다.** 포털과 SDK를 모두 호출할 필요는 없습니다. 화면을 참고할 때만 펼치세요.

<details class="optional-path" markdown="1">
<summary>선택: 모델 Playground의 입력·설정·응답 읽기</summary>

**Build → Models → Deployments → 자신의 배포 → Playground**를 엽니다. 사진의 `contoso-chat`은 `gpt-4.1-mini` 배포 예시이며, 실제 실행에는 L02에서 확인한 자신의 승인된 배포를 선택합니다. 이 단계는 **Save as agent**를 누르지 않는 모델 실습입니다.

![모델 응답 예시. 질문에 포함된 합성 Contoso 규칙에 따라 정확히 200만 원일 때 팀장 승인이 필요하다고 답한다. Tools에는 추가 도구가 없다.](../assets/portal/16-model-response.png)

**화면 따라 읽기:** 왼쪽 **Model / Instructions / Tools**가 요청의 조건이고, 오른쪽이 사용자 입력과 모델 응답입니다. 질문 안에 합성 규칙을 넣은 모델 응답 예시이며, 회사 문서를 검색하는 RAG와는 다릅니다.

![출력 한도 설정 예시. 모델 Playground의 Parameters에서 Max Completion Tokens가 256으로 설정되어 있다.](../assets/portal/17-model-parameters.png)

**실행 전 확인:** **Parameters → Max Completion Tokens**에서 자신의 모델이 지원하는 승인된 출력 한도를 정합니다. 화면의 256은 예시 값입니다. 모델 호출만 연습하므로 추가 과금·외부 전송이 가능한 **Web search** 등 불필요한 도구는 끕니다. Temperature/Top P는 생성의 변동성 관련 옵션이지 비용 금액 상한이 아니며, 지원 모델마다 허용 옵션이 다릅니다.

입력에 적힌 규칙에 따르면 **정확히 200만 원인 경우 팀장 승인**이 필요합니다. 자신의 응답과 response ID를 확인하며, 표시된 토큰 수는 해당 요청의 사용량이지 전체 실습 비용이 아닙니다.

응답 대기가 길어져도 바로 재전송하지 말고 기존 응답을 먼저 확인합니다. 아래 CLI 경로는 response 객체·ID를 코드로 읽는 별도 실행입니다. 기본 터미널 실습을 진행한다면 포털에서 추가 호출할 필요는 없습니다.

</details>

### 1. 아무 비용 없이 계획 먼저 확인하기

```bash
python samples/workshop.py model
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `model` | `workshop.py`의 모델 호출 경로를 선택하지만 `--live`가 없으므로 실행 계획만 보여 줍니다. | `PLAN ONLY`를 읽습니다. Azure 호출·모델 비용 없음. |

</div>

`PLAN ONLY`가 나오고 Azure 요청은 발생하지 않습니다. `--live` 없는 성공 메시지는 모델 호출 성공이 아닙니다.

이 계획은 **예상 동작 안내**이며 `.env`의 값·로그인·권한을 검증한 결과가 아닙니다. 실행 전 L01의 설정과 L02의 배포 이름을 직접 대조합니다.

### 2. 실제 모델 호출하기

```bash
python samples/workshop.py model --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `model --live` | 설정의 프로젝트·배포와 CLI 인증으로 기본 합성 질문을 실제 전송합니다. 출력 토큰은 최대 2048, SDK 자동 재시도는 비활성화되어 있습니다. | 추론 비용이 발생합니다. 응답 텍스트와 `response_id`를 확인하며 agent나 vector store는 만들지 않습니다. |

</div>

응답 텍스트와 `response_id=...`가 나와야 합니다. 질문은 “회사 규정이 제공되지 않았을 때 어떻게 답해야 하는지”입니다. **회사 규정을 만들어내지 않는지** 확인합니다.

**선택 추가 요청:** 자기 질문을 보내고 싶을 때만 아래 명령을 실행합니다. 이미 응답을 받았다면 기본 과제에는 필요 없습니다.

```bash
python samples/workshop.py model --live --query "회사 규정이 없는데 노트북 구매 상한을 단정할 수 있나요?"
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `model --query` | `--query` 뒤 따옴표 전체가 모델에 보낼 한 입력입니다. 기본 질문을 이 문장으로 대체하며 `--live`가 실제 전송을 허용합니다. | 추가 추론 요청입니다. 앞 명령의 결과를 다시 보는 것이 아니므로 비용이 더 발생하고 새 response ID가 생깁니다. |

</div>

`--query`의 내용은 Azure로 전송됩니다. 실습 합성 입력만 사용합니다.

### 3. 핵심 코드 읽기

다음은 핵심 API 흐름입니다. 환경 검사·오류 처리까지 포함한 전체 실행 파일은 `samples/workshop.py`입니다.

```python
with (
    AzureCliCredential() as credential,
    AIProjectClient(endpoint=project_endpoint, credential=credential) as project,
    project.get_openai_client() as client,
):
    response = client.responses.create(
        model=deployment_name,
        input="회사 규정이 없으면 어떻게 답해야 하나요?",
        max_output_tokens=2048,
        store=False,
    )
```

`store=False`는 이 모델 호출의 response 저장 옵션입니다. 모든 서비스 로그·abuse monitoring·데이터 보존이 사라진다는 의미가 아닙니다.

| 값 | 의미 | 흔한 실수 |
| --- | --- | --- |
| project endpoint | 프로젝트 API의 주소 | 모델의 `/openai/v1/` 주소를 대신 입력 |
| deployment name | 내가 배포한 모델의 이름 | 모델 ID와 항상 같다고 생각 |
| response ID | 한 번의 생성 작업 식별자 | conversation ID와 혼동 |
| output text | 모델의 사용자용 응답 | tool call만 있는 응답도 완성으로 처리 |

### 4. 확장 기능의 위치 확인하기

<details class="optional-path" markdown="1">
<summary>선택 참고: 스트리밍·구조화 출력·이미지 입력</summary>

| 기능 | 실습 방법 | 성공 판정 |
| --- | --- | --- |
| Streaming | 포털의 View code/공식 SDK 예제로 stream 이벤트를 수신 | 첫 출력 지연과 최종 완료를 따로 기록 |
| Structured outputs | 지원 모델의 JSON schema 출력 예제로 `sku`, `quantity` 필드 정의 | JSON parse와 필드·타입 검사에 모두 통과 |
| Embeddings | 지원 embedding 배포에서 문서를 벡터화 | 검색용 표현이지 사람이 읽을 정답이 아님 |
| Vision | 지원 모델에 합성 영수증 이미지를 입력 | 가격·수량·총액을 원본과 대조 |

이 확장들은 같은 API가 모든 모델에서 동일하게 지원한다는 뜻이 아닙니다. 새 parameter를 추가할 때 모델 카드의 지원 여부를 확인합니다. 특히 reasoning 모델에 기존 `temperature` 설정을 그대로 복사하지 않습니다.

</details>

## 성공 기준

실제 `--live` 응답이 완료 상태이고 텍스트가 비어 있지 않습니다. response ID를 기록했으며, 사내 정보가 없는 모델 호출과 문서 기반 답변의 차이를 설명할 수 있습니다.

## 막혔을 때

`incomplete`/빈 output이면 “성공”으로 처리하지 않습니다. 출력 토큰 한도, 거절, 도구 요청, quota, trace를 확인합니다. 샘플은 비용과 중복 요청을 줄이기 위해 SDK 자동 재시도를 비활성화합니다. 429에 무한 재시도하지 않습니다.

## 정리

이 샘플의 `model` 명령은 agent나 vector store를 만들지 않습니다. 모델 배포는 계속 존재합니다.
