> **완성할 결과:** 기본에서는 실제 응답 평가를 배우고, 심화에서는 독립 holdout으로 자동 품질 게이트를 판정합니다.

## 목표

**실행 성공, 자동 품질 통과, 사람 검토는 서로 다른 상태**입니다.
이 합성 실습의 현재 `automated-v3`는 사람이 없어도 코드 검사·native 평가로 완료할 수 있습니다.
사람 검토는 실제 운영 전 권장 사항으로만 안내하며, 하지 않은 검토를 완료로 표시하지 않습니다.

## 개념과 실습 지도

**경험할 기능:** 실제 응답 수집, 코드 기반 업무 검사, native evaluator, judge calibration, dev/holdout 품질 게이트입니다.

**무엇이며 왜 중요한가요?** 평가는 정해 둔 질문과 기준으로 결과를 비교하는 절차입니다. Target은 평가받는 도우미, judge는 답을 판정하는 별도 모델입니다. Calibration은 정답·오답 대조군으로 그 judge의 판단부터 점검하는 일입니다. Dev는 개선하며 반복해서 보는 연습 문제, holdout은 동결된 후보의 마지막 독립 시험입니다. 시험지를 보면서 프롬프트를 고치거나 쉬운 행만 평균내면 숫자는 좋아져도 신뢰할 수 없습니다.

**어떻게 사용하나요?** 기본 코스에서는 L05/L06의 응답을 모아 “어떤 이유로 통과·실패했는가”를 읽습니다. 심화에서는 같은 질문·모델·코드·기준을 고정해 dev를 검사하고 마지막에만 독립 holdout을 사용합니다. 서비스의 `completed`는 작업 종료일 뿐, 품질 게이트 통과 여부는 개별 결과와 필수 조건으로 따로 판단합니다.

**어디서 실행하나요?** 수집·자동 검사는 CLI/SDK, 결과 탐색은 포털 Evaluations에서 합니다. [평가 runner](../samples/evaluation_lab.py), [suite 선택 코드](../samples/evaluation_data.py), [v3 판정 기준](../data/evaluation/v3/rubric.json)을 먼저 읽습니다. 봉인된 holdout을 미리 열거나 스크린샷을 위해 재실행하지 않습니다.

## 준비

**기본 순차 경로:** L05/L06의 프로젝트·Prompt Agent·클라이언트 함수 준비만 필요합니다.
L13 Search나 L14 Hosted를 먼저 끝낼 필요가 없습니다. Target과 별도의 judge 배포를 L02에서 준비합니다.

**심화 자동 릴리스 경로:** L13/L14의 실제 Search·Hosted agent와
`FOUNDRY_JUDGE_DEPLOYMENT_NAME`을 준비합니다. 아래 `automated-v3`는 이 경로입니다.

| 자료 | 용도 |
| --- | --- |
| `data/evaluation/cases.jsonl`, `rubric.json` | 원본 v1. 과거 실패와 기존 명령 재현용으로 보존 |
| `data/evaluation/v2/` | 첫 자동 검증의 dev/holdout/기준을 그대로 보존 |
| `data/evaluation/v3/dev.jsonl` | 이미 노출된 v1/v2 총 30건을 dev 회귀로 전환 |
| `data/evaluation/v3/holdout.jsonl` | 독립적으로 작성하고 hash를 봉인한 새 10건. 개선에 사용하지 않음 |
| `data/evaluation/v3/calibration.jsonl` | 정답·오답 8건으로 judge 자체를 검사. target 실행 증거가 아님 |
| `data/evaluation/v3/rubric.json` | 사람 검토는 선택, 90%·safety/access 실패 0건은 그대로 |

`context`는 출제자의 참고 정답 맥락입니다. 실제 검색 결과 대신 넣어 groundedness를 높이지 않습니다.
새 runner는 실제 `retrieved_sources`, 도구 인수/결과, citation, response/trace ID를 사용합니다.

## 실행

### 기본 코스: L05/L06 결과를 학습용으로 자동 평가

![실제 Build → Evaluations의 Runs 목록. 평가 이름·마지막 실행·횟수와 Completed, Canceled, Partial 상태가 함께 표시된다. 작성자 이름은 가렸다.](../assets/portal/08-evaluations.png)

**화면 따라 읽기:** **Build → Evaluations → Runs**에서 자신이 실행한 평가 이름과 시각을 찾습니다. **Status of last run**은 서비스 작업 상태이며, 개별 run을 열어 사례별 점수·오류·누락을 확인해야 품질을 판단할 수 있습니다. **Evaluator catalog**는 평가 기준 탐색, **Recurring configs**는 지속 실행 설정이므로 기본 실습에서 무심코 예약을 만들지 않습니다. 이미 있던 실패·취소를 숨기지 않고 촬영했으며 새 평가를 제출하지 않았습니다.

```bash
python samples/workshop.py evaluate --split dev --live
python samples/evaluation_lab.py calibrate --suite basic-learning --live
python samples/evaluation_lab.py run --suite basic-learning --split dev --input results/앞-명령이-출력한-responses.jsonl --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — 기본 코스에서는 이 세 단계만 수행하고 L09로 진행합니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `workshop.py evaluate --split dev --live` | 기본 SDK 도우미를 dev 질문들에 실제 실행하여 응답·도구·인용을 모읍니다. `--split dev`는 개발용 질문만 선택합니다. | 모델·검색 호출 비용과 새 응답 JSONL이 생깁니다. 출력된 실제 파일 경로를 3번 명령에 넣습니다. |
| 2. `calibrate --suite basic-learning --live` | `--suite`로 학습용 평가 정책을 선택하고 정답/오답 대조군을 judge에 전달합니다. | judge 호출 비용이 발생합니다. 판정 일치는 평가자 검사이며 target의 품질 통과가 아닙니다. |
| 3. `run --suite basic-learning ...` | `--input`의 실제 응답 파일을 같은 dev 기준으로 평가합니다. `run`은 새 target 응답을 꾸며 만드는 명령이 아닙니다. | native 평가·judge 비용이 발생합니다. 점수·오류·실패 이유를 확인하며, 학습용 결과를 독립 릴리스 증거로 쓰지 않습니다. |

</div>

원본 SDK 경로의 노출된 dev 10건으로 평가 절차를 학습합니다. 사람 판정값을 채울 필요는 없습니다.
모델 품질이 미달하면 평가 명령은 실패 상태를 표시하며, 이를 보고 원인과 다음 개선을 설명하는 것이 기본 학습 목표입니다.
`basic-learning` 결과는 독립 holdout을 통과한 배포 품질 증거가 아닙니다.
이 단계를 마쳤으면 L09로 진행하고, 아래 내용은 Hosted를 준비한 뒤 심화 연결로 실행합니다.

### 1. 로컬 자동 검사

```bash
python scripts/prepare_eval_v3.py
python -m unittest discover -s tests -v
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `prepare_eval_v3.py` | 이미 공개된 v1/v2 사례를 v3 dev 회귀 데이터로 준비합니다. 동일 파일은 확인하고, 다른 기존 파일은 덮어쓰지 않습니다. | 로컬 데이터 준비/일치 검사. v3 holdout을 읽거나 새 Azure 응답을 만들지 않습니다. |
| 2. `python -m unittest discover -s tests -v` | `unittest` 모듈이 `tests/` 아래 테스트를 찾습니다. `-s`는 시작 폴더, `-v`는 각 테스트 이름을 표시합니다. | 로컬 계약·회귀 검사를 수행합니다. 통과해도 실제 Azure 품질 증거는 아닙니다. |

</div>

첫 명령은 원본 및 노출된 v2 사례 30건을 dev 회귀로 만들며 v3 holdout을 읽거나 만들지 않습니다.
이미 준비된 파일이 다르면 덮어쓰지 않습니다. 이전 v1/v2 holdout은 v3의 최종 시험지가 아닙니다.
단위 테스트 통과만으로 실제 모델 품질을 주장하지 않습니다.

### 2. 모델이 검색을 생략하지 못하게 실행

Hosted는 질문을 받으면 서버가 먼저 Search를 조회합니다.
작은 합성 정책 집합 13절 전체를 실제 Search에서 함께 조회하여 복합 질문의 필요한 조항이 빠지지 않게 합니다.
현재 공통 엔진은 SKU만 있다는 이유로 재고를 선조회하지 않습니다. 재고·실제 단가·납기를 명시적으로 물었거나 유효한 초안을 요청한 경우에만 허용하며 각 호출을 실행 직전에 다시 검사합니다.
초안 수량이 없거나 모호하거나 잘못되었으면 별도로 요청하지 않은 재고 조회를 하지 않습니다. 도구가 허용되지 않는 정책·명확화 질문은 도구 계획 호출을 건너뜁니다.
수량 제한이 회사 정책이 아닌 도구 입력 제약임을 검증할 수 있도록 실제 함수 정의도 실행 증거에 포함합니다.
모델이 반환하는 `answer`와 `citation_ids`를 엄격한 JSON 계약으로 검사합니다.

빈 citation, 반환되지 않은 출처, 잘못된 문서명, 변조된 본문은 실패합니다.
서버가 파일명을 추측해 덧붙이지 않습니다. **모델이 선택한 실제 출처만** 표시 형식으로 렌더링합니다.
재고·초안의 숫자와 상태는 별도 실제 도구 결과와 대조합니다.
초안 수량이 실제 사용자 문장에 없으면 모델이 유효한 숫자를 제안해도 실행하지 않습니다.
출처 대응 확인 단계의 `raw_attribution`과 response ID도 원본으로 보존하여 근거 선택을 검증합니다.
초안·승인·문서 지시의 권한 판단에 필요한 실제 정책 근거가 모델 선택에서 빠지면 실패하며, 인용을 자동으로 채우지 않습니다. 공통 코드 개선을 과거 한국어 v3 Azure 통과 기록의 재검증으로 해석하지 않습니다. 영어 후속 후보는 별도 v5 동결·독립 시험지를 사용하며 기존 v4 미사용 시험지는 그대로 보존합니다.

### 3. dev에서 개선하고 설정 동결

```bash
python samples/hosted_client.py evaluate --suite automated-v3 --split dev --version 실제숫자 --live
python samples/evaluation_lab.py prepare --suite automated-v3 --split dev --input results/실제-dev-responses.jsonl
python samples/evaluation_lab.py calibrate --suite automated-v3 --live
python samples/evaluation_lab.py run --suite automated-v3 --split dev --input results/실제-dev-responses.jsonl --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — L13/L14를 끝낸 심화 경로입니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `hosted_client.py evaluate ... --version` | `--suite automated-v3 --split dev`의 30건을 정확한 숫자 버전의 Hosted agent에 보냅니다. `실제숫자`를 배포 결과로 바꾸며 `latest`는 쓰지 않습니다. | 실제 Hosted·모델·검색 비용과 새 응답 JSONL 생성. 끝나면 해당 세션 compute 중지를 확인합니다. |
| 2. `evaluation_lab.py prepare ... --input` | 앞 명령의 실제 파일을 읽어 ID·질문·검색·도구·인용과 판정 입력을 검사합니다. `--live` 없이 로컬에서 수행됩니다. | 행 수·해시·evidence 실패 목록을 읽습니다. 점수나 모델 응답을 새로 생성하지 않습니다. |
| 3. `calibrate --suite automated-v3 --live` | v3의 대조군 8건으로 judge의 기대 판정을 확인합니다. | judge 비용 발생. 불일치하면 기준을 낮추지 말고 평가자·설정을 진단합니다. |
| 4. `run --suite automated-v3 --split dev` | 수집한 같은 dev 원본과 고정 기준으로 native 평가·업무 게이트를 판정합니다. | 원격 평가 비용 발생. 코드 검사와 judge 양쪽의 실패를 보존합니다. |

</div>

원본 응답은 append-only 증거와 함께 보존합니다. 재시도는 새 run으로 기록합니다.
같은 데이터·rubric·judge·모델·runtime hash를 비교하고, 검증할 후보를 동결합니다.
native 평가의 인증 주체가 달라 실패한다면 L22의 승인된 OIDC dev 경로로 동일 평가를 실행할 수 있습니다.

### 4. 새 holdout은 최종 한 번만 사용

```bash
python samples/hosted_client.py evaluate --suite automated-v3 --split holdout --version 동결한숫자 --live
python samples/evaluation_lab.py run --suite automated-v3 --split holdout --input results/실제-holdout-responses.jsonl --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — dev 승인·설정 동결 후 최종 시험으로만 실행합니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `evaluate --split holdout --version` | 독립 holdout 10건을 동결한 정확한 버전에 한 번 수집합니다. suite 실행 표식이 재수집을 제한합니다. | 실제 Hosted·검색·모델 비용과 원본 응답 생성. 실패했다고 통과할 때까지 재실행하지 않습니다. |
| 2. `run --split holdout --input` | 방금 보존한 원본을 같은 suite·judge로 판정합니다. `--input`에는 dev 파일이 아닌 해당 holdout 응답 파일을 지정합니다. | 원격 평가 비용 발생. 전체 90%뿐 아니라 safety/access 실패 0건 등 모든 게이트를 확인합니다. |

</div>

봉인된 suite fingerprint별로 실행 표식을 남겨 무심코 다시 샘플링하지 않게 합니다.
모델 응답이 실패했다고 같은 시험지가 통과할 때까지 재실행하지 않습니다.
추가 개선이 필요하면 기존 시험지는 진단 자료로 보존하고, 새 버전의 독립 holdout을 준비합니다.
JSON 파서/전송 문제를 보정할 때도 원래 응답은 바꾸지 않고 같은 원본을 다시 검사합니다.

### 5. 자동 게이트 읽기

| 검사 | 통과 기준 |
| --- | --- |
| 완전성 | 요청 split의 모든 ID, 중복·누락 0, 원래 query와 일치 |
| 검색 | 모델 호출 전에 실제 서버 검색, 원본 절/해시 일치 |
| 인용 | 모델이 선택한 실제 출처가 비어 있지 않고 필수 근거 충족 |
| 업무 도구 | 올바른 함수·인수·실제 결과, 미주문·초안 상태 보존 |
| Native judge | 고정 1~5점 중 4점 이상, score/passed 모순 없음 |
| 전체 품질 | 위 자동 검사와 native 판정을 모두 만족한 사례 90% 이상 |
| safety/access | 실패 0건 |
| Calibration | 8개 대조군의 기대 판정과 모두 일치 |

서비스가 `completed`를 반환해도 evaluator 오류나 누락이 있으면 실패입니다.
9/10이라도 safety 사례가 실패하면 게이트는 통과하지 않습니다.
`manual_pass`는 이 자동 게이트의 입력이 아니며 `human_review_completed=false`로 남습니다.

## 성공 기준

실제 응답·도구·인용과 native 판정이 연결되고, dev와 봉인 holdout의 결과를 구분해 기록했습니다.
사람 검토는 완료 조건이 아닙니다. 향후 실제 운영에 적용할 때 업무 담당자의 표본 검토를 권장합니다.
별도 [영어 v5 실제 결과](../validation/english/automated-v5/quality.json)는 dev 40건 수집·native 평가를 모두 완료했습니다. Native 40/40·오류/누락 0이지만 실제 근거를 합친 판정은 39/40(97.5%)이며, access 사례 `v5-dev-30`의 필수 인용 그룹 누락 때문에 critical 실패 0 기준을 통과하지 못했습니다. 새 holdout 10건은 열지 않았고, 실패 응답·기준을 고치거나 재샘플링하지 않았습니다. 이는 한국어 v3 성적의 변경이나 영어 릴리스 승인이 아닙니다.

과거 v1의 9/10 실패는 [정리 전 커밋의 v1 원본](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/faa5ec26f15cfeb38f69de4036acedc3151c3df4/validation/history/v1)에서 확인합니다. 현재 파일 목록에서는 이전 기록을 정리하지만 과거 판정은 바꾸지 않습니다.

v2의 새 시험지는 복합 질문 누락과 근거 선택 문제를 드러냈으므로 원본 실패를 보존하고 v3 dev로 전환했습니다.
한 개발 사례의 실제 계약서 사용 거절은 SEC1 또는 PROC5가 같은 주장에 유효한 근거임을 원문으로 대조했습니다.
v3에는 이 주장에 한해서만 명시적 근거 대체 그룹을 기록하며, 권한 SEC2·노트북 상한 PROC2와 원래 기대 행동은 유지합니다.
이는 답을 바꾸거나 출처를 자동으로 끼워 넣는 방식이 아닙니다. 원래의 엄격한 v2 판정과 v3 최초 dev 초안도 보존합니다.

## 막혔을 때

검색 결과 없음, JSON/citation 계약 오류, 업무 검사 실패, native judge 오류를 분리합니다.
평가자의 `score`와 `passed`가 서로 다른 항목으로 반환되면 같은 evaluator의 정합한 한 쌍만 사용합니다.
오류 항목을 버리고 성공한 행만 평균내지 않습니다. `--suite legacy-v1`은 원본 재현용이지 새 완료 근거가 아닙니다.

## 정리

Hosted compute와 평가 작업 상태를 확인합니다. 원시 결과/환경은 `results/`에 보존하고
검토한 합성 최소 증거만 `validation/automated-v3/`로 공유합니다.
실제 주문·결제·업무 승인 기능은 계속 사용하지 않습니다.
