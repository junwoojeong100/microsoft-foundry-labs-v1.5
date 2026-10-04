> **완성할 결과:** 실습에 사용할 모델 배포 1개의 정보와 선택 이유. 대안 모델 비교는 선택입니다.

<div class="lab-brief" markdown="1">

**진행 방식:** Foundry 포털 · 이미 제공된 모델 배포가 있으면 다시 만들지 않습니다.

**먼저 할 일:** 자신의 프로젝트에서 모델 ID·버전·배포 이름을 서로 구분해 적습니다.

**확인할 결과:** 준비된 배포와 처리 지역·비용 조건을 확인하고 `.env`에 이름을 저장합니다. 첫 필수 호출은 L03입니다.

</div>

## 목표

**이 가이드의 실습 대상 모델은 OpenAI `gpt-6-sol`입니다.** 모델 버전은 `2026-09-22`로 확인하고, 모델 ID·버전·배포 이름을 구분합니다. 다른 모델과의 비용·성능 비교는 선택 확장입니다.

## 개념과 실습 지도

**경험할 기능:** 실습에서 호출할 모델 배포 한 개를 확인합니다.

**무엇이며 왜 중요한가요?** 모델 ID는 제품 이름, 버전은 출시판, 배포 이름은 내 코드가 호출할 이름입니다. `gpt-6-sol`을 `contoso-chat`으로 배포했다면 코드는 `contoso-chat`을 사용합니다.

**어떻게 사용하나요?** 제공된 배포의 모델·버전·준비 상태를 읽고 **실제 배포 이름**을 `.env`에 기록합니다. 새 배포와 질문 비교는 필요한 경우에만 선택합니다.

**어디서 실행하나요?** Foundry 포털과 [.env.example](../.env.example)을 사용합니다. 목록 읽기는 모델 호출이 아니며, 배포·Playground 전송에는 별도 권한·비용 승인이 필요합니다.

## 준비

L01의 프로젝트와 제공된 모델을 확인·사용할 권한이 필요합니다. **이미 준비된 모델을 쓰는 학습자에게 새 모델 배포 권한은 필요하지 않습니다.**

**이 장의 기본 경로는 확인 → 비용 조건 확인 → 이름 저장입니다.** 새 배포·추가 질문·Model router는 접힌 선택 절에만 있습니다.

## 실행

### 1. 제공된 모델 배포부터 확인하기

1. 자신의 프로젝트에서 **Build → Models → Deployments**를 엽니다.
2. 강사가 준 배포 이름을 선택하고 **모델 ID / 버전 / 준비 상태**를 아래 표와 대조합니다.
3. 배포가 없거나 준비 상태가 실패이면 다음 호출을 진행하지 말고 담당자에게 확인합니다. **Create / Deploy를 눌러 새 자원을 만드는 단계가 아닙니다.**

<details markdown="1">
<summary>선택 참고: 모델 카탈로그와 모델 카드 읽기</summary>

**Discover → Models**에서 **`gpt-6-sol`**을 검색하고 OpenAI 모델 카드를 엽니다. Azure가 직접 제공하는 모델이며 Responses API·구조화 출력·함수 호출 지원을 확인합니다. v1/v2 비교에서는 두 지침 모두 이 동일 모델·버전을 사용합니다.

![Foundry의 실제 Discover → Models 화면. 검색창, Available in my project 필터, 지원 기능·배포 유형 필터와 모델 카드가 보인다.](../assets/portal/02-model-catalog.png)

**화면 따라 읽기:** 상단 **Discover** → 왼쪽 **Models** → **Available in my project** 순서로 범위를 확인합니다. 검색창에서 후보를 찾고 **Supported features / Deployment options / Region**을 좁힙니다. 카드에 보인다는 것과 실제 quota·capacity가 확보됐다는 것은 다릅니다. 촬영 당시의 모델 목록/개수는 학습자의 필수 모델 목록이 아닙니다.

| 모델 카드에서 볼 것 | 확인 이유 |
| --- | --- |
| Responses / function calling / File search 지원 | 이 가이드의 실제 기능과 맞아야 함 |
| 입력·출력 modality | 이미지 입력 지원과 이미지 생성은 별개 |
| 지역·배포 유형·quota | 카탈로그에 보여도 배포 불가능할 수 있음 |
| 모델 버전·종료 정책 | 동일 이름도 버전별 행동이 달라질 수 있음 |
| 가격·문맥 길이·입출력 제한 | 최대 문맥이 길다고 비용이 저렴하지 않음 |
| 라이선스·데이터 처리 조건 | 공급자와 배포 방식별 조건이 다름 |

</details>

| 이번 실습 설정 | 값 |
| --- | --- |
| 공급자 / 모델 ID | OpenAI / `gpt-6-sol` |
| 모델 버전 | `2026-09-22` |
| 권장 실습 배포 이름 | `contoso-gpt-6-sol` |
| 배포 유형 | 가용성과 조직 정책을 확인한 `GlobalStandard` |
| 호출 API | Responses API |

모든 구독에서 quota·capacity가 같지는 않습니다. 카드가 보이더라도 현재 프로젝트에서 지원되는 버전·용량을 확인합니다. 배포가 불가능하면 다른 모델로 조용히 바꾸지 않고 해당 제한을 기록합니다.

### 2. 처리 지역과 비용 조건 확인하기

처음에는 **관리자가 승인한 사용량 기반 유형 한 개**만 사용합니다. `GlobalStandard`는 이 가이드의 예시이지 모든 조직의 정답이 아닙니다. 배포 유형은 비용뿐 아니라 데이터 처리 위치에 영향을 줍니다.

<details markdown="1">
<summary>선택 참고: 다른 배포 유형과 처리 범위</summary>

| 유형 | 언제 사용 | 이번 실습에서 |
| --- | --- | --- |
| Standard / Global Standard / Data Zone Standard | 사용량 기반 서비스 | 정책이 허용하는 1개 선택 |
| Provisioned / PTU | 지속적으로 큰 처리량, 예측 가능한 성능 | 기본 코스에서는 만들지 않음 |
| Batch | 대량 비동기 작업 | 온라인 채팅과 다른 경로로 설계 |
| Developer | fine-tuned 모델 임시 평가 | 일반 base-model 개발 tier와 혼동 금지 |
| Managed compute | 모델용 전용 VM 용량 | Preview 배포 방식·유휴 비용 확인 |
| Instant access | 배포 없이 지원 모델을 즉시 호출 | Preview, 기본 코스의 필수 전제 아님 |

**저장 위치와 추론 처리 위치는 다릅니다.** Global은 전 세계 가용 지역, Data Zone은 지정된 zone, geography 기반 Standard는 해당 Azure geography 범위를 확인해야 합니다. APAC zone은 한국 한 나라를 뜻하지 않습니다.

</details>

### 3. 실제 배포 이름을 설정 파일에 저장하기

이름을 `contoso-gpt-6-sol`로 지정했다면 `.env`에 `FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-gpt-6-sol`을 설정합니다. API에는 모델 카드의 이름이 아니라 **실제 배포 이름**을 넘깁니다.

L01의 관리자 foundation 스크립트는 같은 모델을 `contoso-chat`이라는 배포 이름으로 만들 수 있습니다. 이 경로를 사용했다면 실제 출력된 이름을 설정하고 배포를 중복 생성하지 않습니다. 모델 배포를 바꾸었다고 기존 Hosted 에이전트 코드나 설정이 자동 재배포되는 것은 아닙니다.

**멈춰서 확인:** 포털의 배포 이름과 저장한 `.env`의 값이 같은가요? 아래 TPM/RPM 준비 확인까지 마친 뒤 **성공 기준 → L03**으로 갑니다. 관리자가 연결 시험을 마쳤다면 학습자가 같은 유료 시험을 반복할 필요는 없습니다.

<details class="operator-only" markdown="1">
<summary>관리자만: 새 배포가 없고 생성 승인을 받은 경우</summary>

모델 카드의 **Deploy → Custom settings**에서 **모델 `gpt-6-sol` / 버전 `2026-09-22` / 승인된 배포 유형 / 배포 이름**을 확인합니다. TPM 제한의 표시 단위를 확인하고 **chat은 한 명 기준 100,000 TPM**으로 설정한 뒤 **Deploy**를 선택합니다. 여러 명이 공유하면 아래 표의 인원별 예산을 반영합니다. 권장값을 설정할 수 없으면 낮은 값으로 먼저 배포하지 말고 quota를 확인합니다. **Succeeded/준비됨**과 실제 TPM/RPM을 확인한 뒤 이름을 학습자에게 전달합니다.

</details>

<a id="l02-capacity"></a>

### 4. TPM/RPM 설정 후 연결 시험하기

**TPM은 분당 토큰 처리량, RPM은 분당 요청 수입니다.** 실제 청구 토큰만으로 TPM을 계산하지 않습니다. Azure는 입력과 최대 출력 예약량 등을 추정하며, RPM은 짧은 시간 구간의 몰린 요청도 제한합니다.

| 역할 | 한 명 기준 최소 권장 TPM / RPM | 산정 가정 |
| --- | --- | --- |
| chat | **100,000 / 60** | `(입력 8,192 + 출력 2,048) × 분당 6회 × 여유 1.5 = 92,160`을 10,000 단위로 올림 |
| judge | **100,000 / 60** | 같은 요청 예산. 관리형 평가의 실제 병렬 처리·문맥이 더 크면 추가 여유 필요 |
| embedding | **10,000 / 6** | `입력 8,192 × 분당 1회 × 여유 1.2`를 1,000 단위로 올림 |

**절대적인 서비스 최소나 429가 없다는 보장은 아닙니다.** 한 명이 한 실습을 진행하는 시작 기준입니다. 공유 배포는 동시 학습자 수만큼 늘리고, 입력이 길거나 다른 앱이 함께 호출하면 다시 산정합니다. L15는 최대 세 에이전트가 겹쳐 실행하지만 요청 시작은 최소 1초 간격으로 제한합니다.
상세한 서비스 계산은 [공식 quota·rate limit 안내](https://learn.microsoft.com/azure/foundry/openai/how-to/quota#understanding-rate-limits)를 확인합니다. TPM/RPM은 비용 금액 상한이 아닙니다.

**기본 순서는 권장값으로 배포 → 실제 한도 확인 → 연결 시험입니다.** L01의 `foundation`은 모델을 만들기 전에 지역별 카탈로그의 SKU 단위·증분·quota를 확인하고 역할별 capacity를 설정합니다. 수동 배포도 위 Custom settings에서 권장 TPM을 먼저 지정합니다.
`results/azure-environment.json`은 L01에서 관리자가 제공한 자신의 소유 기록이어야 합니다. 아래 `plan`은 기준을 읽는 명령이고 `check`는 배포 결과를 확인하는 명령입니다.

```bash
python samples/model_capacity.py plan --learners 1
python samples/model_capacity.py check --learners 1 --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `model_capacity.py plan --learners 1` | 요청 예산·여유분에서 역할별 최소 권장 TPM/RPM을 계산합니다. 공유 배포라면 실제 동시 인원으로 바꿉니다. | 로컬 계산만 하며 Azure에 접속하지 않습니다. |
| 2. `check --learners 1 --live` | 소유 RG와 실제 배포의 `rateLimits`, SKU·모델·버전을 확인합니다. | 읽기 전용. TPM 또는 RPM이 부족하면 실패하며 모델 시험을 보내지 않습니다. |

</div>

`deployments.<역할>`의 `tpm`, `rpm`, `minimum_tpm`, `minimum_rpm`, `proposed_capacity`, `ready`를 대조합니다.
**capacity=100을 모든 모델에 동일하게 적용하지 않습니다.** 첫 배포는 원본 ARM 카탈로그의 단위별 TPM/RPM과 명시된 용량 제약으로 환산합니다. CLI의 모델 목록은 `rateLimits.key`를 생략할 수 있으므로 이 값을 추측하지 않습니다. quota 이름도 모델명으로 조합하지 않고 SKU의 `usageName`으로 대조합니다. 배포 후 실제 한도가 기준에 못 미치면 준비 완료로 표시하지 않으며 시험을 보내지 않습니다.

<details class="operator-only" markdown="1">
<summary>기존 배포 보정용: 부족한 처리량을 승인 범위에서 맞추기</summary>

새 `foundation` 배포가 권장값을 충족하면 이 단계는 건너뜁니다. 기존·수동 배포가 부족하거나 동시 학습자 수가 늘었을 때만 사용합니다. 할당량 조회와 배포 변경 권한이 필요합니다. `OWN_RUN_ID`는 소유 기록의 `run_id`로 바꿉니다. 아래 `100`은 배포당 허용할 capacity 단위 상한이며 TPM이나 비용 금액이 아닙니다.

```bash
python samples/model_capacity.py apply --learners 1 --max-capacity 100 --confirm OWN_RUN_ID --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `apply ... --confirm OWN_RUN_ID --live` | 모든 대상의 필요 단위·가용 quota를 먼저 확인한 뒤 부족한 배포의 SKU capacity만 PATCH하고 재조회합니다. | 실제 Azure 설정 변경. 모델·버전·보호 정책은 바꾸지 않고 충분한 용량은 줄이지 않습니다. 새 자원·PTU를 생성하지 않습니다. |

</div>

필요 단위가 상한을 넘거나 quota가 부족하면 변경 전에 중단합니다. 관리자가 별도 승인한 경우에만 인원·상한을 조정합니다. 일부 변경 후 오류가 나면 `Evidence:`의 요청·확인 기록을 읽고 모든 역할이 준비되기 전에는 모델 시험을 실행하지 않습니다.

</details>

<details class="optional-path" markdown="1">
<summary>선택: 설정을 맞춘 뒤 비용 승인을 받은 연결 시험</summary>

관리자가 이미 연결 시험을 마쳤다면 반복하지 않습니다.
Embedding 시험은 같은 소유 Foundry 리소스의 `/openai/v1/embeddings`를 사용합니다. 프로젝트 endpoint의 Responses 지원이 embeddings 지원을 뜻하지는 않습니다.

```bash
python samples/model_capacity.py test --learners 1 --confirm OWN_RUN_ID --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `test ... --confirm OWN_RUN_ID --live` | 실제 TPM/RPM을 다시 확인한 뒤 chat 최대 3회, judge 1회, embedding 1회를 시험합니다. | 최대 5회 모델 요청·180초·재시도 0회. 생성 모델은 최대 2,048 출력 토큰입니다. 결과는 고유 `Evidence:` 파일에 보존하며 전체 실습·품질 통과로 표시하지 않습니다. |

</div>

</details>

한 역할만 필요하면 모든 명령에 `--roles chat`처럼 지정합니다. 기본 평가 준비는 `--roles chat judge`, L15는 `--roles chat`만 확인해도 됩니다.
오류나 429가 발생하면 반복 호출하지 않습니다. 토큰·요청 한도, 인증·권한, 공유 배포의 다른 트래픽을 확인한 뒤 다음 행동을 승인받습니다. 이 시험은 **설정·연결 확인이지 최소 TPM의 부하 한계 측정이나 전체 과정 검증이 아닙니다.**

<details class="optional-path" markdown="1">
<summary>선택: 추가 비용 승인 후 모델 답변 두 개 비교하기</summary>

준비된 배포의 **Playground → Chat**에서 다음 입력을 각각 한 번만 전송합니다. L08의 v1/v2 실측은 별도의 고정 복합 질문 12개를 사용합니다.

```prompt
다음 규칙을 한 문장으로 요약해줘:
총액 200만 원 이하는 팀장 승인, 200만 원 초과는 팀장과 구매 담당자 승인.
```

```prompt
규칙: 총액 200만 원 이하는 팀장 승인, 초과는 팀장과 구매 담당자 승인.
총액 200만 원인 경우와 200만 1원인 경우를 표로 비교해줘.
규칙에 없는 내용은 추가하지 마.
```

| 후보 | 두 질문의 실제 결과 | 대략적 지연 | 토큰/가격 조건 | 선택 |
| --- | --- | --- | --- | --- |
| `gpt-6-sol` | 직접 기록 | 직접 기록 | 모델 카드 기준 | 실습 대상 |
| 별도 승인한 대안(선택) | 실행했다면 기록 | 직접 기록 | 모델 카드 기준 | 비교 이유 |

공개 leaderboard는 후보를 줄이는 출발점이지 내 업무 데이터의 성능 보증이 아닙니다.

</details>

### 5. 선택 확장: Model router

<details class="optional-path" markdown="1">
<summary>기본 실습에는 불필요: 요청별 모델 선택을 더 비교할 때</summary>

Model router는 요청별로 적절한 모델을 고르는 **모델 배포**입니다. 가능하면 `Balanced`부터 비교하고 `Cost`, `Quality`, 허용 model subset을 검토합니다. 같은 20개 평가 데이터를 사용하세요.

라우팅 pool은 같은 router 버전 식별자에서도 업데이트될 수 있습니다. 허용 모델·최소 context window·데이터 처리 범위·fallback을 확인합니다. 사용자 정의 subset은 승인된 모델만 포함하며 fallback 실험에는 둘 이상이 필요합니다. **반드시 더 저렴하거나 더 정확하다고 가정하지 않습니다.**

<details markdown="1">
<summary>비용·성능을 더 다룰 때</summary>

Prompt caching은 동일 prefix와 실제 선택 모델 등 조건에 영향을 받습니다. Batch는 온라인 요청의 단순 옵션 변경이 아니라 별도의 비동기 작업 흐름입니다. Flex/Priority는 지원 배포에서의 처리 tier이며 각각 지연 허용/우선 처리라는 목적이 있습니다. PTU는 예약 비용·용량·취소 조건을 검토한 후 별도 승인으로 진행합니다.

</details>

</details>

## 성공 기준

모델 **제공자 / ID / 버전 / 배포 이름 / 지역 / 유형**을 각각 적을 수 있고, 가격·기능·데이터 처리 조건을 근거로 선택 이유를 설명할 수 있습니다.

## 막혔을 때

**배포 메뉴에 모델이 없으면** 모델·지역·유형 지원과 접근 조건을 먼저 확인합니다. **quota와 실제 capacity는 동일하지 않습니다.** quota가 있어도 특정 용량 배포는 실패할 수 있습니다. 기능을 확인하지 않은 다른 모델로 몰래 바꾸지 않습니다.

## 정리

사용할 배포만 남기고 비교용 배포의 유지 필요성을 확인합니다. 사용량 기반 모델 외에 고정 비용 자원을 만들었다면 별도로 기록합니다.
