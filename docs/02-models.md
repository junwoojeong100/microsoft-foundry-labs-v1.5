> **완성할 결과:** 내가 배포한 모델의 이름·버전·처리 범위·호출 한도를 확인하고 코드에서 사용할 값을 저장합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** L01에서 만든 배포를 포털과 소유 기록으로 확인합니다. 중복 배포하지 않습니다.

**먼저 할 일:** 자신의 프로젝트에서 `contoso-chat`의 Model ID·Version·Deployment Name을 구분합니다.

**확인할 결과:** 실제 배포가 준비됐고 TPM/RPM이 계획을 충족합니다. 첫 답변은 L03에서 받습니다.

</div>

## 목표

**모델 ID·모델 버전·배포 이름은 서로 다릅니다.** 이 키트의 chat 구성은 `gpt-6-sol / 2026-09-22`이며, L01의 생성 코드가 붙이는 호출 이름은 `contoso-chat`입니다. 해당 조합의 실제 지역·구독 가용성은 배포 시 확인해야 합니다.

## 개념과 실습 지도

**경험할 기능:** 직접 만든 모델 배포의 설정·지원 기능·처리량을 확인합니다.

**무엇이며 왜 중요한가요?** 모델 ID는 제품, version은 출시판, deployment name은 코드가 호출하는 이름입니다. `model="contoso-chat"`은 그 배포를 사용하며 모델을 새로 만들지 않습니다.

**어떻게 사용하나요?** 포털의 준비 상태와 소유 기록을 대조하고 같은 이름을 `.env`에 저장합니다. 용량이 부족하면 조회 결과를 읽고 자신의 범위에서 보정합니다.

**어디서 실행하나요?** Microsoft Foundry 포털의 Models와 터미널의 [model_capacity.py](../samples/model_capacity.py)를 사용합니다. 모델 목록·한도 조회는 추론 요청이 아닙니다.

## 준비

L01의 `results/azure-environment.json`, `.env`, 생성한 프로젝트·모델이 필요합니다. L01의 배포가 실패했다면 먼저 그 오류를 해결합니다. 이 장에서 다른 환경이나 모델을 대신 선택하지 않습니다.

## 실행

### 1. 내가 배포한 모델 확인하기

1. **Build → Models → Deployments**에서 `contoso-chat`을 엽니다.
2. Model ID·Version·배포 유형·준비 상태를 아래 표와 소유 기록의 `model_configuration`에 대조합니다.
3. `contoso-judge`, `contoso-embedding`도 확인합니다. 배포가 없으면 L01의 배포 상태를 점검하고, 포털에서 같은 이름을 추가 생성하지 않습니다.

| 용도 | 모델 ID / 버전 | L01이 만드는 배포 이름 |
| --- | --- | --- |
| 답변·에이전트 | `gpt-6-sol` / `2026-09-22` | `contoso-chat` |
| L08 평가 | `gpt-4.1` / `2025-04-14` | `contoso-judge` |
| L11 검색·L15 Memory | `text-embedding-3-small` / `1` | `contoso-embedding` |

![Microsoft Foundry의 실제 Discover → Models 화면. 검색창, Available in my project 필터, 지원 기능·배포 유형 필터와 모델 카드가 보인다.](../assets/portal/02-model-catalog.png)

**화면 따라 읽기:** **Discover → Models**는 후보와 모델 카드를 찾는 곳이고 **Build → Models → Deployments**는 실제 배포를 확인하는 곳입니다. 카드가 보인다고 quota·capacity가 확보된 것은 아닙니다. Responses API·함수 호출·File search 지원과 현재 가격·종료 정책을 확인합니다.

### 2. 처리 지역과 비용 조건 읽기

L01의 `GlobalStandard`는 사용량 기반 예시입니다. 프로젝트 지역, 모델 가용 지역, 추론 처리 범위는 같지 않을 수 있습니다. 조직 정책에 맞는 배포 유형인지 확인합니다.

| 유형 | 확인할 조건 |
| --- | --- |
| Standard | 해당 Microsoft Azure geography의 처리 범위·가용성 |
| Global Standard | 전 세계 지원 지역의 처리 범위가 허용되는지 |
| Data Zone Standard | 지정 zone의 처리 범위. APAC을 한국 한 나라로 해석하지 않음 |
| Provisioned / PTU | 예약 비용·용량. 이 기본 코스에서는 만들지 않음 |

저장 위치와 추론 처리 위치를 구분합니다. 새 유형이나 모델을 시험하려면 비용·권한·비교 조건을 따로 확인하고 결과를 별도 실험으로 남깁니다.

### 3. 포털의 배포 이름을 코드에 연결하기

L01 경로의 `.env` 값은 `FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat`입니다. API의 `model` 인수에는 Model ID가 아니라 **실제 배포 이름**을 넣습니다.

| 포털에서 보는 값 | Python에서 쓰이는 곳 |
| --- | --- |
| Home → Project endpoint | `AIProjectClient(endpoint=project_endpoint, ...)` |
| Deployments → Name | `responses.create(model=deployment_name, ...)` |
| Model ID / Version | 배포 설정과 소유 기록에서 비교. 추론 요청마다 별도 지정하지 않음 |

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 배포 이름이 Python 요청에 들어가는 위치 — 읽기용</summary>

다음은 L03에서 볼 **요청 부분 발췌**입니다. `client`는 L01/L03의 프로젝트 client, `question`은 보낼 합성 질문입니다. 이 구문은 모델 배포가 아니라 유료 추론 요청입니다.

```python
response = client.responses.create(
    model=deployment_name,
    input=question,
    max_output_tokens=512,
    store=False,
)
```

</details>

지금은 값을 대조하는 단계이므로 이 구문을 실행하지 않습니다. 포털 Name·소유 기록의 `model_deployments.chat`·`.env`가 모두 `contoso-chat`인지 확인합니다.

<a id="l02-capacity"></a>

### 4. TPM/RPM 계획과 실제 한도 비교하기

**TPM은 분당 토큰, RPM은 분당 요청 수**입니다. 실제 청구 토큰뿐 아니라 입력과 최대 출력 예약량이 처리량 추정에 영향을 줍니다. 둘 다 비용 금액 상한은 아닙니다.

| 용도 | 1인 기준 권장 TPM / RPM | 계획 가정 |
| --- | --- | --- |
| chat | 100,000 / 60 | `(8,192 + 2,048) × 분당 6회 × 여유 1.5`를 10,000 단위로 올림 |
| judge | 100,000 / 60 | 같은 시작 예산. 평가의 병렬 처리·문맥에 따라 추가 여유 필요 |
| embedding | 10,000 / 6 | `8,192 × 분당 1회 × 여유 1.2`를 1,000 단위로 올림 |

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 권장 TPM의 계산식 — 실행할 계획 명령은 아래에 있습니다</summary>

계획 계산은 다음과 같습니다. **서비스 최소치나 429가 없다는 보장은 아닙니다.**

```python
from math import ceil

learners = 1
chat_tpm = ceil((8192 + 2048) * 6 * 1.5 * learners / 10000) * 10000
embedding_tpm = ceil(8192 * 1 * 1.2 * learners / 1000) * 1000
print(chat_tpm, embedding_tpm)
```

</details>

L01의 foundation은 카탈로그의 모델별 capacity 단위·증분·quota로 위 계획을 환산합니다. 모든 모델에 `capacity=100`을 그대로 적용하지 않습니다.

포털 배포 양식과 비교할 때는 모델 카드의 **Deploy → Custom settings**에 있는 지역·유형·TPM 필드가 코드의 지역·SKU·처리량 계획에 대응합니다. L01에서 배포했으므로 이 양식을 추가 제출하지 않습니다.

```bash
python samples/model_capacity.py plan --learners 1
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `plan --learners 1` | 용도별 요청 예산과 권장 TPM/RPM을 계산합니다. | 로컬 계산만 합니다. 공유 배포는 실제 동시 인원으로 바꿉니다. |

</div>

**계획을 읽은 뒤 실제 한도를 조회합니다.** 이 명령은 모델에 질문을 보내거나 배포를 바꾸지 않습니다.

```bash
python samples/model_capacity.py check --learners 1 --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `check ... --live` | 자신의 RG·모델·version·SKU와 실제 `rateLimits`를 조회합니다. | 읽기 전용. 한도가 부족하면 실패하며 모델 시험을 보내지 않습니다. |

</div>

`deployments.<용도>`의 `tpm`, `rpm`, `minimum_tpm`, `minimum_rpm`, `ready`를 대조합니다. 숫자를 조회하지 못했다면 준비 완료로 표시하지 않습니다.

<details class="optional-path" markdown="1">
<summary>용량이 부족할 때만: 내 배포의 처리량 보정</summary>

소유 기록의 정확한 `run_id`와 실제 변경 권한·비용 범위를 확인한 뒤 실행합니다. 이미 충분한 배포는 줄이지 않습니다.

```bash
python samples/model_capacity.py apply --learners 1 --max-capacity 100 --confirm OWN_RUN_ID --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `apply ... --confirm ... --live` | 필요 단위·quota를 확인하고 부족한 배포의 capacity만 변경·재조회합니다. | 실제 Microsoft Azure 변경. Model ID·version·보호 정책은 유지하며 새 PTU는 만들지 않습니다. |

</div>

필요 단위가 상한을 넘거나 quota가 부족하면 변경 전에 중단합니다. 임의로 모델·지역을 바꿔 검사를 통과시키지 않습니다.

</details>

<details class="optional-path" markdown="1">
<summary>선택: 여러 모델의 연결 확인 — L03 첫 호출과 중복 실행하지 않기</summary>

기본 코스의 첫 추론은 L03입니다. 다음 시험은 chat 최대 3회·judge 1회·embedding 1회가 별도로 필요할 때만 선택합니다.

```bash
python samples/model_capacity.py test --learners 1 --confirm OWN_RUN_ID --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `test ... --confirm ... --live` | 실제 한도를 다시 읽고 최대 5건의 모델 요청을 보냅니다. | 최대 180초·재시도 0회·생성 요청당 출력 최대 2,048토큰. 연결 시험이지 품질 통과가 아닙니다. |

</div>

Embedding은 부모 리소스의 `/openai/v1/embeddings`를 사용합니다. 프로젝트 Responses 지원을 embeddings 지원과 혼동하지 않습니다.

</details>

### 5. 선택 확장: Model router

Model router는 요청에 따라 모델을 선택하는 별도 배포입니다. 허용 모델·지역·fallback·가격을 확인하고 **같은 dev 질문**으로 비교합니다. 독립 holdout을 개선 과정에 노출하지 않으며 더 저렴하거나 정확하다고 미리 가정하지 않습니다. Batch·PTU·fine-tuning은 기본 실습과 다른 사용 조건·비용이 있는 별도 경로입니다.

## 성공 기준

내 배포의 제공자·Model ID·version·Name·지역·유형과 실제 TPM/RPM을 설명할 수 있습니다. 포털·`.env`·소유 기록의 호출 이름이 일치하고, L03 실행 전에 배포가 준비된 상태입니다.

## 막혔을 때

모델이 없거나 한도 조회가 실패하면 지역·유형·quota·접근 권한을 확인합니다. quota가 있어도 특정 capacity 배포는 실패할 수 있습니다. 429 뒤 무한 재시도를 하지 않습니다.

## 정리

L01에서 만든 세 배포를 다음 장에서 이어 사용합니다. 선택 실험으로 추가한 배포가 있다면 이름·비용·보존 기한을 별도 기록하고 L19에서 확인합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** chat/judge/embedding의 실제 배포 이름·모델 버전·TPM/RPM과 준비 상태. 포털·`.env`·소유 기록이 일치해야 합니다.

**다음:** [L03 첫 답변](#l03). 이미 준비된 배포를 사용하며 모델을 다시 배포하지 않습니다.

</div>
