> **완성할 결과:** API key 없이 Foundry 모델을 호출하고, 응답과 response ID를 확인합니다.

## 목표

모델을 호출하는 가장 작은 단위를 이해합니다. **아직 agent도, RAG도 아닙니다.**

## 준비

L01의 `.env`, 로그인, `requirements.txt` 설치와 L02의 준비된 배포가 필요합니다. 이 경로는 Azure public cloud 프로젝트를 대상으로 합니다. Government 등 sovereign cloud endpoint는 별도 공식 인증·도메인 설정을 적용해야 합니다.

## 실행

### 1. 아무 비용 없이 계획 먼저 확인하기

```bash
python samples/workshop.py model
```

`PLAN ONLY`가 나오고 Azure 요청은 발생하지 않습니다. `--live` 없는 성공 메시지는 모델 호출 성공이 아닙니다.

### 2. 실제 모델 호출하기

```bash
python samples/workshop.py model --live
```

응답 텍스트와 `response_id=...`가 나와야 합니다. 질문은 “회사 규정이 제공되지 않았을 때 어떻게 답해야 하는지”입니다. **회사 규정을 만들어내지 않는지** 확인합니다.

내 입력으로 호출하려면:

```bash
python samples/workshop.py model --live --query "회사 규정이 없는데 노트북 구매 상한을 단정할 수 있나요?"
```

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

| 기능 | 실습 방법 | 성공 판정 |
| --- | --- | --- |
| Streaming | 포털의 View code/공식 SDK 예제로 stream 이벤트를 수신 | 첫 출력 지연과 최종 완료를 따로 기록 |
| Structured outputs | 지원 모델의 JSON schema 출력 예제로 `sku`, `quantity` 필드 정의 | JSON parse와 필드·타입 검사에 모두 통과 |
| Embeddings | 지원 embedding 배포에서 문서를 벡터화 | 검색용 표현이지 사람이 읽을 정답이 아님 |
| Vision | 지원 모델에 합성 영수증 이미지를 입력 | 가격·수량·총액을 원본과 대조 |

이 확장들은 같은 API가 모든 모델에서 동일하게 지원한다는 뜻이 아닙니다. 새 parameter를 추가할 때 모델 카드의 지원 여부를 확인합니다. 특히 reasoning 모델에 기존 `temperature` 설정을 그대로 복사하지 않습니다.

## 성공 기준

실제 `--live` 응답이 완료 상태이고 텍스트가 비어 있지 않습니다. response ID를 기록했으며, 사내 정보가 없는 모델 호출과 문서 기반 답변의 차이를 설명할 수 있습니다.

## 막혔을 때

`incomplete`/빈 output이면 “성공”으로 처리하지 않습니다. 출력 토큰 한도, 거절, 도구 요청, quota, trace를 확인합니다. 샘플은 비용과 중복 요청을 줄이기 위해 SDK 자동 재시도를 비활성화합니다. 429에 무한 재시도하지 않습니다.

## 정리

이 샘플의 `model` 명령은 agent나 vector store를 만들지 않습니다. 모델 배포는 계속 존재합니다.
