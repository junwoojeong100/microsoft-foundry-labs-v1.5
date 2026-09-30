> **완성할 결과:** 기본에서는 실제 응답 평가를 배우고, 심화에서는 독립 holdout으로 자동 품질 게이트를 판정합니다.

## 목표

**실행 성공, 자동 품질 통과, 사람 검토는 서로 다른 상태**입니다.
이 합성 실습의 현재 `automated-v3`는 사람이 없어도 코드 검사·native 평가로 완료할 수 있습니다.
사람 검토는 실제 운영 전 권장 사항으로만 안내하며, 하지 않은 검토를 완료로 표시하지 않습니다.

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

```bash
python samples/workshop.py evaluate --split dev --live
python samples/evaluation_lab.py calibrate --suite basic-learning --live
python samples/evaluation_lab.py run --suite basic-learning --split dev --input results/앞-명령이-출력한-responses.jsonl --live
```

원본 SDK 경로의 노출된 dev 10건으로 평가 절차를 학습합니다. 사람 판정값을 채울 필요는 없습니다.
모델 품질이 미달하면 평가 명령은 실패 상태를 표시하며, 이를 보고 원인과 다음 개선을 설명하는 것이 기본 학습 목표입니다.
`basic-learning` 결과는 독립 holdout을 통과한 배포 품질 증거가 아닙니다.
이 단계를 마쳤으면 L09로 진행하고, 아래 내용은 Hosted를 준비한 뒤 심화 연결로 실행합니다.

### 1. 로컬 자동 검사

```bash
python scripts/prepare_eval_v3.py
python -m unittest discover -s tests -v
```

첫 명령은 원본 및 노출된 v2 사례 30건을 dev 회귀로 만들며 v3 holdout을 읽거나 만들지 않습니다.
이미 준비된 파일이 다르면 덮어쓰지 않습니다. 이전 v1/v2 holdout은 v3의 최종 시험지가 아닙니다.
단위 테스트 통과만으로 실제 모델 품질을 주장하지 않습니다.

### 2. 모델이 검색을 생략하지 못하게 실행

Hosted는 질문을 받으면 서버가 먼저 Search를 조회합니다.
작은 합성 정책 집합 13절 전체를 실제 Search에서 함께 조회하여 복합 질문의 필요한 조항이 빠지지 않게 합니다.
질문에 명시된 SKU의 읽기 전용 재고 조회도 서버가 먼저 수행하여, '조회가 필요하다'는 계획만 답하지 않게 합니다.
수량 제한이 회사 정책이 아닌 도구 입력 제약임을 검증할 수 있도록 실제 함수 정의도 실행 증거에 포함합니다.
모델이 반환하는 `answer`와 `citation_ids`를 엄격한 JSON 계약으로 검사합니다.

빈 citation, 반환되지 않은 출처, 잘못된 문서명, 변조된 본문은 실패합니다.
서버가 파일명을 추측해 덧붙이지 않습니다. **모델이 선택한 실제 출처만** 표시 형식으로 렌더링합니다.
재고·초안의 숫자와 상태는 별도 실제 도구 결과와 대조합니다.
초안 수량이 실제 사용자 문장에 없으면 모델이 유효한 숫자를 제안해도 실행하지 않습니다.
출처 대응 확인 단계의 `raw_attribution`과 response ID도 원본으로 보존하여 근거 선택을 검증합니다.

### 3. dev에서 개선하고 설정 동결

```bash
python samples/hosted_client.py evaluate --suite automated-v3 --split dev --version 실제숫자 --live
python samples/evaluation_lab.py prepare --suite automated-v3 --split dev --input results/실제-dev-responses.jsonl
python samples/evaluation_lab.py calibrate --suite automated-v3 --live
python samples/evaluation_lab.py run --suite automated-v3 --split dev --input results/실제-dev-responses.jsonl --live
```

원본 응답은 append-only 증거와 함께 보존합니다. 재시도는 새 run으로 기록합니다.
같은 데이터·rubric·judge·모델·runtime hash를 비교하고, 검증할 후보를 동결합니다.
native 평가의 인증 주체가 달라 실패한다면 L22의 승인된 OIDC dev 경로로 동일 평가를 실행할 수 있습니다.

### 4. 새 holdout은 최종 한 번만 사용

```bash
python samples/hosted_client.py evaluate --suite automated-v3 --split holdout --version 동결한숫자 --live
python samples/evaluation_lab.py run --suite automated-v3 --split holdout --input results/실제-holdout-responses.jsonl --live
```

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
과거 v1의 9/10 실패는 `validation/history/v1/`에 보존하며 새 결과로 바꾸지 않습니다.

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
