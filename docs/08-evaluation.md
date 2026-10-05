> **이 모듈에서 만드는 것:** 같은 조건의 v1/v2 답변을 비교하고, 점수와 채점 이유를 근거로 차이·동점·실패를 설명하는 방법입니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 지침·질문 비교 → 내 응답 수집 → 같은 원문의 Foundry 평가 → 이유 분석.

**먼저 할 일:** 동봉 지침 두 개와 고정 질문을 읽고, 답변에서 확인해야 할 항목을 적습니다.

**확인할 결과:** 같은 문항의 내 v1/v2 원문·점수·채점 이유를 연결합니다. 실행 조건이 부족하면 읽기만 했다고 기록합니다.

</div>

## 목표

**답변의 차이와 평가자의 판단을 구분합니다.** v1은 역할·목표 중심의 시작 지침, v2는 답변 절차를 구체화한 지침입니다. v2라는 이름만으로 더 좋은 답이라고 판단하지 않습니다.

## 개념과 실습 지도

**경험할 기능:** 같은 질문의 두 답변과 평가 이유를 비교합니다.

**무엇이며 왜 중요한가요?** 평가는 기대한 행동과 실제 답을 비교하는 일입니다. 지침만 바꾸고 모델·정책·질문·채점 기준을 같게 해야 차이를 해석할 수 있습니다.

**어떻게 사용하나요?** 고정된 질문·지침을 읽고 요청 예산을 확인합니다. 내 원문을 한 번 수집해 평가하며 동점·하락도 그대로 해석합니다.

**어디서 실행하나요?** [질문·체크리스트](../data/evaluation/instruction-comparison.json), [v1](../data/prompts/agent-v1.txt)·[v2](../data/prompts/agent-v2.txt)를 읽고, 승인된 경우 [응답 수집 코드](../samples/instruction_prompt_agent_lab.py)와 [평가 코드](../samples/instruction_evaluation.py)를 사용합니다.

## 준비

L01에서 만든 **자신의 프로젝트·chat/judge 배포·소유 기록**을 사용합니다. 타인의 결과를 받아 실습 성공으로 기록하지 않습니다. Azure 실행 조건이 없을 때는 지침·질문·채점 기준만 읽고 실제 평가 미실행으로 남깁니다.

| 용어 | 쉬운 뜻 |
| --- | --- |
| v1 / v2 | 시작 지침 / 개선한 지침. 서비스의 agent version 번호와는 별개 |
| Judge / Native 평가 | 채점용 모델 / Foundry 서비스가 수행하는 평가 |
| 완결성 / 관련성 / 근거성 | 요청을 다 다뤘는가 / 질문에 맞는가 / 자료가 답을 뒷받침하는가 |
| Dev / Holdout | 개선 과정에서 보는 연습 자료 / 개선에 노출하지 않는 별도 최종 시험지 |

L01의 환경과 L02의 **`gpt-6-sol` / `2026-09-22`**, 호출 이름 `contoso-chat`을 사용합니다. `.env`와 소유 기록의 대상이 같아야 합니다.

Native 평가에는 L01이 만든 **`gpt-4.1` / `2025-04-14`** judge, `FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge`가 필요합니다. L02에서 실제 chat/judge TPM/RPM을 확인합니다. Search·Hosted·Optimizer·holdout은 필요하지 않습니다.

새 실행은 **자신의 `results/azure-environment.json`과 `.env`**를 사용합니다. 수집 코드는 현재 RG 소유 태그·프로젝트·배포·TPM/RPM을 조회하고, 충돌하지 않는 평가용 Prompt Agent 이름과 고정된 v1/v2 버전을 사용합니다.

한국어는 기본값입니다. 영어는 별도 폴더에서 `FOUNDRY_LAB_LANGUAGE=en`을 유지합니다. 두 지침에는 같은 합성 정책 문맥을 제공하며 이를 실제 Search 조회라고 표시하지 않습니다. 질문의 기대 행동과 채점 기준은 대상 모델 입력에 넣지 않고 judge에게만 제공합니다.

## 실행

### 1. 질문과 지침을 먼저 비교하기

질문 파일에서 `compound-request-no-tools`를 찾고 **상한 / 현재 재고 / 승인자 / 초안** 요청을 구분합니다. 두 지침이 각각 어떤 답변 절차를 요구하는지 읽으세요. 이 비교에는 도구가 없으므로 재고 조회나 초안 생성 성공을 주장해서는 안 됩니다.

| v1의 일반 지침 | v2에서 구체화한 행동 | 답변에서 확인할 항목 |
| --- | --- | --- |
| 모르는 정보는 추측하지 않기 | 비공개 부분을 거절해도 확인 가능한 공용 질문은 끝까지 답하기 | 숫자·통화·부가세 기준 |
| 실제 문서 인용하기 | 주장별로 관련된 근거 절 연결하기 | 다른 판단에 같은 일반 소개 절을 대신 인용하지 않기 |
| 정책과 도구 사용하기 | 상한·견적·실제 단가·환율·초안 상태 구분하기 | 미확인 조건을 확정 사실로 만들지 않기 |
| 안전하게 초안 만들기 | 명시적 요청·수량·실제 도구 결과 확인하기 | 승인·주문·결제 완료를 가장하지 않기 |

지침에 질문별 정답이나 평가 사례 ID를 넣지 않습니다. 계정 없이 참여했다면 **동일하게 고정할 조건 / 답변에서 찾을 근거 / 실행하지 않은 범위**를 정리합니다. 아직 답을 수집하지 않았다면 우열이나 점수를 작성하지 않습니다.

### 2. 내 응답을 한 번 수집하고 평가하기

내 프로젝트·언어·요청 수·시간·비용 범위를 확인합니다. 조건을 갖춘 기본 실습 경로는 **계획 → 수집 → 평가**입니다.

```bash
python samples/instruction_prompt_agent_lab.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py` | v1/v2와 고정 질문 12개, 모델, 호출 상한을 읽습니다. | 계획만 출력하며 Azure 호출은 없습니다. |

</div>

계획이 자신의 범위와 일치하면 첫 줄을 실행합니다. **수집 파일의 정상 완료를 확인한 뒤** 두 번째 줄로 진행합니다. 두 줄을 한꺼번에 실행하지 않습니다.

```bash
python samples/instruction_prompt_agent_lab.py --live --output results/instruction-prompt-agent-ko.json
python samples/instruction_evaluation.py --input results/instruction-prompt-agent-ko.json --output results/instruction-native-prompt-agent-ko.json --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. 응답 수집 `--live` | 자신의 소유 프로젝트에 도구 없는 Prompt Agent와 지침별 버전을 만들고 같은 문맥·질문으로 답을 수집합니다. | 언어별 최대 24건·600초·재시도 0회·응답당 최대 2,048 출력 토큰. 원문과 실패를 별도 파일에 보존합니다. |
| 2. Native 평가 `--live` | `--input`에 지정한 실제 원문 24개를 Foundry 평가에 제출합니다. | 대상 모델 재호출 0건. 언어별 Native 1회·600초·취소 확인 90초 이내. 점수와 이유는 `--output` 파일에 기록합니다. |

</div>

영어는 영어 환경에서 입력·출력 파일 이름도 `en`으로 구분합니다. 두 언어 합계는 대상 응답 최대 48건·수집 최대 1,200초입니다. 기존 파일을 덮어쓰거나 점수가 오를 때까지 반복 수집하지 않습니다. 실패 시 원본 오류와 이미 완료된 요청 수를 확인합니다.

`agent_reference`로 호출할 때는 Agent 정의의 `reasoning`·`text` 설정을 요청에 중복 지정하지 않습니다.

#### 포털 평가와 실제 SDK 호출의 대응

응답 수집과 평가는 서로 다른 API 호출입니다. 수집 스크립트는 대상 Prompt Agent를 v1/v2의 고정 버전으로 한 번씩 호출하고, 평가는 저장된 24개 원문을 Foundry evaluator에 제출합니다.
아래는 실제 호출 부분 발췌입니다. `shared_input`은 한 문항의 질문과 동일 정책 문맥, `criteria`는 완결성·관련성·근거성의 고정 evaluator 설정, `rows`는 저장된 24개 원문입니다. `data_source_config`는 각 행의 필수 필드를 정의한 schema이며 코드 발췌를 단독 실행하지 않습니다.

```python
# instruction_prompt_agent_lab.py: one row in the fixed v1/v2 collection
response = client.responses.create(
    input=shared_input,
    extra_body={"agent_reference": {
        "type": "agent_reference",
        "name": agent_name,
        "version": versions[label],
    }},
    max_output_tokens=MAX_OUTPUT_TOKENS,
    store=False,
)

# instruction_evaluation.py: evaluate those saved rows; do not call the target again
group = client.evals.create(
    name=f"Contoso {LANGUAGE} instruction comparison",
    data_source_config=data_source_config,
    testing_criteria=criteria,
)
native = client.evals.runs.create(
    eval_id=group.id,
    name=f"Contoso {LANGUAGE} v1-v2 one comparison",
    data_source={"type": "jsonl", "source": {"type": "file_content", "content": [{"item": row} for row in rows]}},
)
```

| Foundry portal | 원본 코드에서 확인할 값 |
| --- | --- |
| Agents → Versions | `agent_reference.name/version`이 각 응답에 사용한 지침 버전 |
| Evaluations → Criteria | `testing_criteria=criteria`와 고정 judge deployment |
| Evaluations → Run | `client.evals.runs.create(...)`의 입력은 저장된 JSONL rows |
| Results | 같은 `case_id`의 실제 답변·점수·이유; `completed`만으로 품질 통과라고 하지 않음 |

실제 실행은 앞의 `--live` 경로를 사용합니다. 코드 발췌를 읽거나 포털 결과를 확인하는 일은 추가 target 호출이 아닙니다. 기존 질문·rubric·threshold는 바꾸지 않습니다.

### 3. 같은 문항의 원문·점수·이유 연결하기

수집 파일의 `rows`에서 같은 `id`의 v1/v2를 찾습니다. 평가 파일은 `comparison.rows`의 `case_id`와 `instructions`로 연결합니다.

| 필드 | 읽는 방법 |
| --- | --- |
| `rows[].raw_answer`, `response_id` | 실제 원문과 응답 식별자 |
| `prompt_agent_versions` | 호출한 agent 이름과 지침별 고정 버전 |
| `comparison.rows[].metrics` | 문항별 Native 점수·통과 여부·채점 이유 |
| `comparison.local_checklist` | 수집 파일의 보조 텍스트·인용 체크 |
| `comparison.usage_latency` | 지침별 토큰·시간과 차이 |
| `instructions_sha256`, `cases_sha256`, `context_sha256` | 비교 조건이 같았는지 대조할 입력 해시 |

질문별로 **요청한 내용 / 두 실제 답 / 관련 정책 절 / 평가자의 이유 / 동의 여부**를 기록합니다. `raw_answer`는 JSON 문자열이므로 `answer`와 `citation_ids`를 나누어 읽습니다.

### 4. 점수와 실행 완료를 구분하기

Native 완결성·관련성·근거성은 **1–5 ordinal** 점수입니다. 관련성·근거성은 built-in evaluator, 완결성은 두 지침에 같은 기준을 적용하는 custom evaluator입니다. 4점 이상이라는 이진 요약과 5점 척도는 다릅니다.

로컬 체크리스트는 12문항의 총 40개 기준을 검사하는 **기계적인 텍스트·인용 체크**입니다. 표현 차이를 놓칠 수 있으므로 자동 의미 평가나 업무 safety/access 게이트로 사용하지 않습니다.

![Foundry 평가 화면. 실행 상태와 행별 점수·오류·누락을 구분하는 위치를 확인합니다.](../assets/portal/08-evaluations.png)

포털 **Build → Evaluations**에서 자신의 실행을 찾고 상태, 평가자, 행별 결과를 확인합니다. `completed`만으로 모든 행의 점수가 유효하다고 판단하지 않습니다. 오류·누락·숫자가 아닌 점수는 실패이며, 임의로 0점이나 통과로 채우지 않습니다.

### 5. 차이·동점·하락을 설명하기

v1이 이미 충분한 답을 냈으면 동점일 수 있고, 생성 변동으로 v2가 낮을 수도 있습니다. 원문과 채점 이유에서 원인을 찾되 v1을 약화하거나 기준을 사후 변경하지 않습니다.

이 질문은 노출된 **dev** 자료입니다. 독립적인 **holdout**이나 일반화 검증이 아니며, **Optimizer** 후보 생성도 별도 과제입니다. 전체 90% 이상·safety/access 실패 0 같은 기존 업무 게이트는 이 작은 학습용 점수로 대체하거나 낮추지 않습니다.

## 성공 기준

지침·질문 읽기만 했다면 비교 조건과 확인할 근거를 설명하고 **실제 평가 미실행**으로 기록합니다.
실행했다면 12문항의 v1/v2 원문·고정 버전·Native 점수·채점 이유·오류/누락을 연결하고, 근거에 따라 차이·동점·하락을 설명합니다. 점수 향상을 미리 약속하지 않습니다.

## 막혔을 때

401/403은 자신의 프로젝트와 인증 주체·역할을, 404는 실제 배포 이름과 endpoint를 확인합니다. 429는 TPM/RPM·공유 트래픽을 확인하고 무한 재시도하지 않습니다. 수집 파일이 실패·부분 완료이면 평가에 제출하지 않습니다. 모델이나 judge를 임의로 바꾸어 비교 조건을 섞지 않습니다.

## 정리

응답 파일 `results/instruction-prompt-agent-ko.json`과 평가 파일 `results/instruction-native-prompt-agent-ko.json`을 함께 보관합니다. 비교를 위해 만든 agent·평가 자원은 자신의 소유 기록과 보존 정책에 따라 관리하며 별도 삭제 승인 전에는 지우지 않습니다.
