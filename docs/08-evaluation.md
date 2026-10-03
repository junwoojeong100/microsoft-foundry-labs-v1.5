> **이 모듈에서 만드는 것:** 교육용 초기 v1 → 평가 → 이유 분석·개선 → v2 재평가 흐름을 실제 답변과 평가 이유로 설명합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 보존된 실제 결과 읽기가 기본 · 새 유료 평가 실행은 선택입니다.

**먼저 할 일:** 아래 한 문항의 v1/v2 답변을 읽고 상한·재고·승인·초안 네 요청이 모두 다뤄졌는지 표시합니다.

**확인할 결과:** 답변·점수·채점 이유를 연결해 동점이나 차이를 설명합니다. 이 독해를 자신의 Azure 실행으로 기록하지 않습니다.

</div>

## 목표

**답변의 차이와 평가자의 판단을 구분합니다.** v1은 역할·목표 중심의 시작 지침, v2는 답변 절차를 구체화한 지침입니다. 이 비교에서는 v1을 고정하며, v2라는 이름만으로 더 좋은 답이라고 판단하지 않습니다.

## 개념과 실습 지도

**경험할 기능:** 같은 질문의 두 답변과 점수·채점 이유를 비교합니다.

**무엇이며 왜 중요한가요?** 평가는 기대한 행동과 실제 답을 비교하는 일입니다. 지침만 바꾸고 모델·정책·질문·채점 기준을 같게 해야 차이를 해석할 수 있습니다.

**어떻게 사용하나요?** 아래 한 문항의 두 답을 먼저 읽고 점수를 봅니다. 동점·하락도 그대로 기록합니다. 새 유료 평가를 실행할 필요는 없습니다.

**어디서 실행하나요?** 이 페이지에서 읽습니다. [질문·체크리스트](../data/evaluation/instruction-comparison.json), [v1](../data/prompts/agent-v1.txt)·[v2](../data/prompts/agent-v2.txt), [선택 실행 코드](../samples/instruction_prompt_agent_lab.py)는 필요한 때 확인합니다.

## 준비

**기본 독해 경로에는 계정·새 모델 호출이 필요 없습니다.** [한국어 응답 원본](../validation/current/ko/responses.json)과 [한국어 평가 원본](../validation/current/ko/native.json)이 ZIP에도 들어 있습니다. 아래 한 문항은 그 원본에서 생성하며 새로 쓴 모범 답안이 아닙니다.

| 먼저 알 용어 | 쉬운 뜻 |
| --- | --- |
| v1 / v2 | 시작 지침 / 개선한 지침. 서비스의 에이전트 버전 번호와는 별개 |
| Judge / Native 평가 | 채점용 모델 / Foundry 서비스가 수행한 평가 |
| 완결성 / 관련성 / 근거성 | 요청한 내용을 다 다뤘는가 / 질문에 맞는가 / 제공 자료가 답을 뒷받침하는가 |
| Dev / Holdout | 개선하며 보는 연습 자료 / 개선에 노출하지 않는 별도 최종 시험지 |

<details class="optional-path" markdown="1">
<summary>선택 실행의 준비: 새 응답 수집·평가에 필요한 환경</summary>

L01의 환경과 L02의 **`gpt-6-sol` / `2026-09-22`** 배포를 사용합니다. `.env`에는 자신의 실제 배포 이름을 넣습니다. 권장 이름은 `contoso-gpt-6-sol`이고 L01 관리자 경로가 만든 이름은 `contoso-chat`일 수 있습니다. Native 평가에는 별도 `FOUNDRY_JUDGE_DEPLOYMENT_NAME`도 필요합니다. 이번 실측의 judge는 양쪽 모두 기존 `contoso-judge`(GPT-4.1)로 고정했습니다. Hosted agent 재배포, Search 서비스, Optimizer, holdout은 필요하지 않습니다. 평가 실행은 각 Foundry 프로젝트 안에 도구 없는 Prompt Agent 하나와 v1/v2 두 버전을 만들었습니다.
체크인된 **합성 정책 문맥**을 두 지침에 동일하게 제공합니다. 이를 실제 Search 조회라고 표시하지 않습니다.
12개 질문은 두 언어에서 같은 시나리오·ID·기준을 사용합니다. 데이터셋의 기준 행동은 모델 응답 입력에 포함하지 않고, native judge에게만 제공합니다.
한국어는 기본값이며, 영어 실습에서는 `FOUNDRY_LAB_LANGUAGE=en`을 유지합니다.

</details>

## 실행

### 1. 한 문항을 먼저 읽고 판단하기

아래는 **한국어로 실제 수집한 질문·답변·Native 점수**입니다. 답변에서 **상한 / 현재 재고 / 승인자 / 초안**을 하나씩 찾아보세요. L06과 달리 이 비교에는 도구가 없으므로 재고와 초안의 실행 성공을 주장하면 안 됩니다.

<!-- instruction-reading-example -->

**이렇게 해석합니다:** 이 문항은 두 답변 모두 네 요청을 다룹니다. 관련성만 4→5이고 다른 두 지표는 5→5입니다. 따라서 “이번 채점에서 관련성 차이가 관측됐다”까지 말할 수 있지만, 이 한 문항으로 v2가 항상 더 좋다고 결론낼 수는 없습니다. 펼쳐 보는 채점 이유도 비판적으로 읽습니다.

자신의 기록에는 **관찰한 차이 / 원문에서 찾은 근거 / 아직 모르는 것**을 한 줄씩 적습니다. 이어 아래 전체 결과와 원본의 다른 문항을 읽습니다.

### 2. v2의 개선점을 읽기

| v1의 일반 지침 | v2에서 구체화한 행동 | 확인할 답변 차이 |
| --- | --- | --- |
| 모르는 정보는 추측하지 않기 | 비공개 부분을 거절해도 확인 가능한 공용 질문은 끝까지 답하기 | 공용 상한의 숫자·통화·부가세 기준을 생략하지 않음 |
| 실제 문서 인용하기 | 접근 권한·정보 부재·공용 사실·다음 단계에 각각 적합한 절 연결하기 | 일반 소개 절 하나로 다른 판단의 근거를 대신하지 않음 |
| 정책과 도구 사용하기 | 정책 상한·견적·실제 단가·확정 환율·초안 상태 구분하기 | 없는 계약 조건이나 환율을 확정 사실로 만들지 않음 |
| 안전하게 초안 만들기 | 명시적 요청·정확한 수량·중복 금지·실제 결과 확인 | 임시 수량, 승인·주문·결제 완료 주장 없음 |

v2에 질문별 정답이나 평가 사례 ID를 넣지 않습니다. 여러 질문에도 적용할 수 있는 답변 절차를 개선합니다.

### 3. 선택: 자신의 환경에서 새 비교 실행하기

기존 결과를 읽는 중이라면 이 단계는 건너뜁니다. 새 수집·평가의 프로젝트·언어·요청 한도·비용을 승인받은 경우에만 펼칩니다. 한국어 기본 환경을 쓰며, 영어 실행은 별도 폴더에서 L01의 언어 선택을 먼저 합니다.

<details class="optional-path" markdown="1">
<summary>새 유료 실행: 계획 확인 → 응답 수집 → 수집한 원문 평가</summary>

```bash
python samples/instruction_prompt_agent_lab.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py` | v1/v2, 고정 질문 12개, 대상 배포와 두 버전의 계획을 확인합니다. | 기본 동작은 plan-only이며 Azure 응답 호출은 0건입니다. |

</div>

계획이 자신의 범위와 같을 때만 아래 첫 줄을 실행합니다. 수집 파일이 정상 완료된 뒤 두 번째 줄로 넘어갑니다. **두 줄을 한꺼번에 실행하지 않습니다.**

```bash
python samples/instruction_prompt_agent_lab.py --live --output results/instruction-prompt-agent-ko.json
python samples/instruction_evaluation.py --input results/instruction-prompt-agent-ko.json --output results/instruction-native-prompt-agent-ko.json --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `instruction_prompt_agent_lab.py --live` | 선택한 언어의 승인된 프로젝트에 평가용 Agent 하나와 v1/v2를 만들고 같은 문맥·질문으로 응답을 수집합니다. | 언어별 최대 24건·600초·재시도 0회·출력 2,048토큰. 두 언어를 각각 승인받아 실행할 경우 합계 최대 48건·1,200초입니다. 원문·토큰·지연·보조 체크를 `results/`에 저장합니다. |
| 2. `instruction_evaluation.py --live` | 앞서 수집한 실제 Prompt Agent 응답 24개를 Foundry native 평가에 제출합니다. | 대상 재호출 0건. 언어별 Native 1회·600초·취소 확인 90초 이내이며 점수와 이유를 별도 파일에 보존합니다. |

</div>

영어는 같은 세 명령에서 언어와 입력·출력 파일을 `en`으로 바꿉니다. 응답 수집은 언어별 최대 600초(두 언어 합계 최대 1,200초), Native 평가는 언어별 단 1회·최대 600초입니다. 한국어 24개와 영어 24개를 넘겨 요청하지 않습니다. 기존 결과 파일은 덮어쓰지 않습니다. 이번 실측의 완료 원본은 `results/instruction-prompt-agent-{ko,en}-attempt-3.json`, Native 원본은 `results/instruction-native-prompt-agent-{ko,en}-attempt-1.json`입니다.

비교 파일이 이미 있으면 다시 호출하지 않고 그 결과를 읽습니다. 이번 실측에서는 첫 사전 검증 실패와 다음 API 요청 형식 오류가 각각 대상 응답 0건으로 기록되었고, 허용된 범위 안에서 수정 후 단 한 번 완전한 수집을 했습니다. 실패 원본도 보존했으며 이전 답이나 예시 답으로 채우지 않았습니다. Prompt Agent 요청에서는 `agent_reference`가 지정된 경우 Agent 정의에 포함된 `reasoning`/`text`를 호출 요청에 중복 지정하지 않습니다. Foundry 평가 ID는 원본 추적용입니다.

위 `results/` 경로는 직접 실행한 사람의 파일입니다. 키트에는 개인 실행 파일을 넣지 않으므로 기존 결과는 앞서 연결한 `validation/current/ko/` 원본에서 읽습니다.

</details>

### 4. 점수와 근거를 함께 읽기

각 지침에 12개 질문, 총 40개 기준을 적용하므로 로컬 보조 점수 범위는 **0~40**입니다.
체크는 질문에 미리 고정한 사실·거절·확인 경로가 답에 나타나는지와 관련 정책 절을 선택했는지를 확인합니다.
이는 **기계적인 텍스트·인용 체크리스트**입니다. 표현 차이를 완벽히 이해하는 의미 평가나 업무 릴리스 게이트가 아닙니다.

<details markdown="1">
<summary>원본 JSON에서 다른 문항·점수·해시를 찾을 때</summary>

| 결과 필드 | 읽는 방법 |
| --- | --- |
| `comparison.local_checklist.scores.v1`, `.v2` | 응답 원본 JSON에서 동일 기준으로 충족한 체크 수 |
| `comparison.local_checklist.delta`, `.outcome` | v2-v1 차이와 실제 `improved`, `unchanged`, `regressed` 판정 |
| `rows[].raw_answer`, `checklist` | 각 원문, 체크별 판정, 필수 안전 체크 실패 |
| `comparison.usage_latency` | 버전별 토큰과 평균·총 지연 및 v2-v1 차이 |
| `instructions_sha256`, `cases_sha256`, `context_sha256` | 실제 비교 입력 식별 해시. 교육용 v1/v2 외의 버전 번호가 아님 |

편집기에서 `compound-request-no-tools`를 검색하면 응답의 `rows`에서 v1/v2를 찾을 수 있습니다. 평가 원본은 `comparison.rows`의 `case_id`와 `instructions`로 같은 두 행을 찾고 `metrics`의 점수·이유를 읽습니다. `raw_answer`는 JSON을 담은 문자열이라 `\"`·`\n`이 보일 수 있습니다. 위 읽기 예제는 그 문자열의 `answer`를 펼친 것이며 내용을 바꾸지 않습니다.

</details>

**v2의 높은 점수를 보장하지 않습니다.** v1이 이미 완전한 답을 냈으면 동점일 수 있고, LLM 변동으로 v2가 낮을 수도 있습니다.
그 경우 원문에서 원인을 설명하는 것이 실습입니다. v1을 약화하거나 체크리스트를 바꾸어 개선을 연출하지 않습니다.

### 5. 문항 유형과 Foundry native 평가 읽기

<details class="provenance-note" markdown="1">
<summary>참고: 이전 세 문항에서 12문항으로 확장한 이유</summary>

새 질문을 고정하기 전에 이전 세 사례(`public-and-restricted`, `quote-and-policy`, `approval-and-draft`)의 결과부터 읽습니다. 보존된 [이전 보고서](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation)에서는 두 언어의 v1/v2가 완결성·관련성·근거성 모두 5.0/5였습니다. 이 세 복합 사례에서 양쪽이 요구에 충분히 답해 최고점에 도달했으므로, 표본이 작고 척도 상한에 걸려 지침 차이를 변별하지 못했습니다. 이는 두 지침이 동등하다는 증명도, v1을 인위적으로 약화할 이유도 아닙니다. 따라서 새 dev 질문은 결과를 본 뒤 고른 것이 아니라 사전에 고정한 12개 경계·근거·하위 질문·도구 제한 복합 사례로 확장했고, 기존 세 문항을 새 결과로 덮어쓰지 않았습니다.

</details>

고정 질문은 단순 사실 찾기 대신 여러 품목 상한과 총액 승인, 정확한 경계값, 공개 정보와 권한 제한, 누락된 규정, 계약·환율 불확실성, 견적과 실시간 재고, 도구 입력 제약, 메모의 권한 주장, 복합 요청을 함께 다룹니다. 두 지침은 똑같은 문맥과 도구 없음 경계에서 답합니다.

Foundry native 평가자는 문항의 사전 고정 기대 행동을 보고 1–5 **ordinal** 점수와 영어 이유를 반환합니다. 평균은 지침별 12개 행으로 계산합니다. 이 값은 이진 `TaskAdherence` 점수가 아니며, native 결과와 이유가 주된 품질 근거입니다. 로컬 체크리스트는 보조 근거로만 읽습니다.

![Foundry 평가 화면. 완료 상태와 개별 점수·오류·누락을 구분합니다.](../assets/portal/08-evaluations.png)

Evaluations에서 실행 상태, 평가자, 입력 데이터, 행별 판정과 오류를 구분해서 살펴봅니다.
선택 실행의 수집 명령은 실제 Azure 모델 응답과 로컬 체크를 남기고, [native 비교 코드](../samples/instruction_evaluation.py)는 그 원문을 Foundry Evaluations에 제출합니다. 관련성·근거성은 built-in evaluator이며 완결성은 두 지침에 동일한 1~5 기준을 적용하는 custom evaluator입니다.
이번 비교는 노출된 dev 학습 질문 12개일 뿐 독립적인 holdout·일반화 검증이 아닙니다. 별도 judge calibration은 하지 않습니다.
전체 90% 이상·safety/access 실패 0 등 기존 업무 게이트는 이 작은 학습용 점수로 대체하거나 완화하지 않습니다.

### 6. 국문·영문 전체 측정 결과

다음 표는 제작 때 수집한 실제 결과입니다. 자신의 실행 결과나 앞으로 보장되는 점수가 아닙니다. 먼저 점수 표를 읽고, 재현 조건이 필요하면 상세 기록을 펼칩니다.

<details class="provenance-note" markdown="1">
<summary>측정 조건: 모델·에이전트 버전·시간·평가자</summary>

사전 고정한 12개 복합 dev 질문을 한국어·영어 각각 v1/v2로 한 번씩 호출했습니다. 응답 생성은 Hosted가 아닌 **Foundry Prompt Agent**이며, 한국어 `contoso-instruction-eval-ko-20261001`과 영어 `contoso-instruction-eval-en-20261001`에서 v1/v2 버전 `1`/`2`를 고정했습니다. 대상은 `gpt-6-sol` / `2026-09-22`, reasoning `low`, 최대 출력 2,048 토큰이고, Agent 정의의 JSON schema·도구 없음 설정 및 각 언어의 문맥·질문은 동일했습니다. 수집은 한국어 88.707초, 영어 77.389초(합계 166.096초)였습니다. 평가자는 별도 `contoso-judge` / GPT-4.1 `2025-04-14`이며, 지침 이름이나 기대 우열을 전달하지 않았습니다. 언어별 Native run 한 건에 24행을 제출했고 두 run 모두 완료, 오류·누락 0건이었습니다.

</details>

| 언어 | 지침 | 보조 로컬 체크 / 40 | Native 완결성 / 5 | 관련성 / 5 | 근거성 / 5 |
| --- | --- | ---: | ---: | ---: | ---: |
| 한국어 | v1 | 33 | 5.0 | 4.9167 | 5.0 |
| 한국어 | v2 | 33 | 5.0 | 5.0 | 5.0 |
| English | v1 | 29 | 5.0 | 5.0 | 5.0 |
| English | v2 | 28 | 5.0 | 5.0 | 5.0 |

Native 점수는 1–5 ordinal입니다. 한국어 관련성에서 `compound-request-no-tools` 한 문항의 v1이 4점, v2가 5점을 받아 평균이 4.9167에서 5.0으로 변했습니다(+0.0833). 해당 judge 이유는 v1이 네 요청을 모두 다루고 제한도 설명했지만 충분한 정보를 제공했다고 평가하면서 4점을 부여했습니다. 한국어의 다른 두 지표와 영어의 세 지표는 모두 동점 5.0입니다. 따라서 **이번 소규모 조건에서 한국어 관련성의 제한적인 향상만 관측**됐으며, 전반적·재현 가능한 향상이나 통계적 유의성을 뜻하지 않습니다. `passed=24/24`는 4점 이상이라는 별도 이진 요약이지 5점 척도 자체가 아니며, 별도 judge calibration은 하지 않았습니다.

<details class="provenance-note" markdown="1">
<summary>상세 분석: 토큰·지연·체크리스트 차이·Optimizer와 holdout</summary>

| 언어 | v1 입력 / 출력 / 총 토큰 | v2 입력 / 출력 / 총 토큰 | 총 토큰 차이 | 평균 응답 지연 v1 → v2 |
| --- | ---: | ---: | ---: | ---: |
| 한국어 | 34,242 / 3,437 / 37,679 | 40,218 / 4,837 / 45,055 | +7,376 | 3.473초 → 3.900초 (+0.427초) |
| English | 31,205 / 2,567 / 33,772 | 35,537 / 3,392 / 38,929 | +5,157 | 2.966초 → 3.462초 (+0.496초) |

로컬 체크는 보조 신호이며 한국어는 33/40→33/40(동점), 영어는 29/40→28/40(−1)입니다. critical checklist의 바뀐 항목은 모두 원문과 대조했습니다. `untrusted-contract-instruction`에서 두 언어 모두 v2가 문서 지시를 권한으로 취급하지 않는다고 명시했고, 한국어에서는 권한 확인·정식 경로도 안내했습니다. 영어 v2는 공급업체 계약 접근 미확인을 명시했고, 교체 자격 확인 및 초안과 주문·결제의 구분도 답했지만, 표현 패턴이 일부 답을 놓쳤습니다. 원문과 체크 플래그를 함께 보존하며 체크리스트를 사후 수정하지 않았습니다. 이는 수동 검토이지 별도 보정된 안전 평가가 아닙니다.

문항별 원응답, 세 Native 지표 점수와 judge 이유는 [한국어 응답](../validation/current/ko/responses.json)·[한국어 Native 결과](../validation/current/ko/native.json), [영어 응답](../validation/current/en/responses.json)·[영어 Native 결과](../validation/current/en/native.json)에 있습니다. 각 행은 응답 ID 및 고정된 Prompt Agent 이름·버전과 연결됩니다. 예를 들어 한국어 `compound-request-no-tools`는 이번 Prompt Agent run에서 관련성 4→5로 달라진 단 한 행이며 다른 지표는 동점입니다.

**개선 결론:** 이번 조건에서는 한국어 Native 관련성 평균이 4.9167→5.0(+0.0833)으로 올랐고, 다른 필수 Native 지표·영어 지표는 하락하지 않았으며, critical checklist 변경의 수동 검토에서 안전·권한 회귀를 확인하지 않았습니다. 따라서 제한된 dev 관측에서만 향상으로 기록합니다. 이 표본은 작고 노출되어 있으므로 통계적 유의성·일반화·운영 승인·재현 보장은 아닙니다. v2의 토큰·지연 증가와 영어 보조 체크 −1도 함께 봅니다.

**Optimizer와 holdout의 역할:** Optimizer는 dev 자료로 개선 후보를 만드는 선택 기능이고, holdout은 지침·개선 과정에 노출하지 않은 독립 최종 시험지입니다. 이번 질문은 노출된 dev 자료이므로 holdout이 아니며 기존 봉인 holdout은 열거나 실행하지 않았습니다. Optimizer의 현재 Hosted agent는 GPT-4.1-mini 경로이고 이번 GPT-6 Sol Prompt Agent 비교와 모델 조건이 달라 Optimizer job은 제출하지 않았습니다. 직접 작성한 v2를 Optimizer 후보라고 표현하지 않습니다. 이전 측정·Optimizer 실행 이력은 [기준선 커밋](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation)에 보존합니다.

</details>

## 성공 기준

v1/v2의 실제 답을 같은 기준으로 보고, 원문 근거로 **차이 또는 동점**을 설명할 수 있습니다.
숫자가 올랐다는 결론은 실제 `delta`가 양수일 때만 씁니다. 이 실습을 위해 반복 검증·holdout·Optimizer를 수행할 필요는 없습니다.

[현재 지침 상태](../validation/current/instructions.json)와 [최신 Prompt Agent 실측](../validation/current/report.json)에 국문·영문 원문, 모델과 Agent 버전, 문항별 답변 hash·점수·이유와 실행 ID가 있습니다. 이전 direct Responses 비교는 보존된 Git 이력에 구별해 남아 있습니다.

## 막혔을 때

모델·문맥·질문·체크가 양쪽에서 같은지 먼저 확인합니다. JSON 형식 오류, 인용 누락, 답변 누락을 구분하고 원문을 읽습니다.
이미 생성한 비교 파일은 덮어쓰지 않습니다. 모델 오류가 나도 “예상 v2 답”을 대신 기록하지 않습니다.

## 정리

**기본 독해만 했다면 이 장에서 만든 Azure 자원은 없습니다.** 새 수집을 직접 했다면 자신의 실행 기록에 있는 자원만 L12에 적습니다.

<details class="provenance-note" markdown="1">
<summary>참고: 제작 당시 실측이 남긴 자원</summary>

이 실측은 두 평가 전용 Prompt Agent와 각 2개 버전을 만들었습니다. Hosted 세션·Optimizer job·모델 배포는 만들지 않았습니다. 응답과 native 평가 job은 완료 상태이며, 에이전트·모델 배포는 별도 승인 없이 삭제하지 않습니다.

</details>
