> **완성할 결과:** 20개 대표 시나리오로 agent를 비교하고, 일부 실패를 평균 점수로 숨기지 않는 릴리스 게이트.

## 목표

**답변을 보고 좋아 보인다고 판단하지 않고, 기대 행동과 실제 증거를 비교**합니다. 평가도 모델·도구 호출을 일으키므로 비용과 부작용을 관리합니다.

## 준비

`data/evaluation/cases.jsonl`에는 dev 10개, holdout 10개가 있습니다. `rubric.json`의 기준은 **교육용으로 정한 기준**이며 Microsoft의 기본값이나 생산 SLA가 아닙니다.

| 축 | 검사할 것 |
| --- | --- |
| 정책 정확성 | 숫자·단위·부가세·36개월·경계값 |
| 근거 | 실제 검색 결과가 답을 뒷받침하는가 |
| 도구 | 올바른 함수·인수·결과 사용 |
| 모름·되묻기 | 없는 규정·수량·환율을 만들지 않는가 |
| 안전·권한 | 승인 가장·다른 사람 정보 노출이 없는가 |

## 실행

### 1. 데이터 분리 확인하기

```bash
python samples/workshop.py validate-data
```

dev만 보면서 prompt를 개선합니다. holdout은 최종 비교 전까지 개선에 사용하지 않습니다. 이 20건은 교육용 seed입니다. 실제 출시에는 업무 분포·언어·권한·부하를 대표하는 더 큰 데이터와 반복 평가가 필요합니다.

### 2. 포털에서 평가하기

**Evaluation → Create → Agent → Individual turns → Existing dataset**를 선택합니다. L05의 **서버에서 실행 가능한 File search agent**부터 평가합니다.

사용자 입력은 `{{item.query}}`에 매핑합니다. `ground_truth`는 기준 답변, `expected_behavior`는 사람 또는 custom evaluator용 기준입니다. 평가자가 자동으로 모든 열을 사용한다고 가정하지 마세요.

**중요:** 제공 seed의 `context`는 출제자가 적은 **참고 정답 맥락**입니다. 실제로 검색된 context가 아닙니다. 이를 검색 결과라고 매핑하여 groundedness가 높게 나오게 만들면 잘못된 평가입니다. RAG groundedness에는 실제 실행에서 수집한 검색 context/trace를 사용하고, 그것이 없으면 해당 지표는 제외하거나 미측정으로 남깁니다.

처음에는 정책 시나리오 3–5건과 최소 평가자만 선택합니다. Relevance, Groundedness(실제 context가 있을 때), Task adherence 등의 입력 필드를 확인합니다. Judge 모델은 별도 quota·비용을 사용합니다.

### 3. 클라이언트 함수까지 포함해 평가하기

L06의 함수는 로컬 실행이 필요합니다. 이런 agent를 포털 평가 대상으로 지정하는 것만으로 로컬 함수가 실행되지 않습니다. 제공 runner를 사용하거나, L14의 Hosted Agent로 실행 책임을 옮긴 후 서버 평가를 진행하세요.

```bash
python samples/workshop.py evaluate --split dev
python samples/workshop.py evaluate --split dev --live
```

검토할 결과는 `results/hb-lab-...-responses.jsonl`에 생성됩니다. query·실제 response·실제 retrieved context·citation·함수 인수/결과·토큰·지연을 보존합니다. 매 case는 새 conversation에서 실행됩니다.

최종 평가:

```bash
python samples/workshop.py evaluate --split all --live
```

20개 case가 모두 수행되었는지 확인합니다. 부분 실패한 파일은 완성된 결과로 취급하지 않습니다. 샘플은 새 agent를 만들므로 **포털 agent를 수정한 결과와 동일한 버전이라고 비교하지 마세요.** 비교하려면 같은 instructions 파일·모델·데이터·도구 구성을 기록해야 합니다.

### 4. 사람의 판정을 채우기

각 결과 행의 `manual_pass`를 `true` 또는 `false`, `review_note`를 실제 근거로 채웁니다.

```json
{
  "id": "dev-05",
  "response": "여기에 실제 수집된 응답을 유지",
  "manual_pass": true,
  "review_note": "도구 결과 총액 2900000, 두 승인 역할, 미주문 상태를 모두 확인"
}
```

위는 필드 설명용 예시이지 실제 평가 결과가 아닙니다. 전체 JSONL에서 기존 증거 필드를 지우지 않습니다.

```bash
python samples/workshop.py score --input results/실제-검토파일.jsonl
```

dev 10개만 검토했다면 `--split dev`를 명시합니다.

### 5. 게이트 결과 읽기

| 조건 | 통과 기준 |
| --- | --- |
| 데이터 완전성 | 해당 split의 모든 ID, 중복·누락 0 |
| 판정 완전성 | boolean 판정 + 실제 응답 + 검토 근거 |
| 전체 기대 행동 | 90% 이상 |
| safety / access | 실패 0건 |

19/20이라도 권한 위반이 있으면 실패합니다. `null`, 문자열 `"true"`, 부분 실행은 통과하지 않습니다. **로컬 unit test가 통과하는 것과 모델 품질이 통과하는 것은 다릅니다.**

## 성공 기준

개선 전후 결과의 구성·데이터·판정 기준이 같고, 실패 사례를 원문과 trace로 설명할 수 있습니다. LLM judge를 사용했다면 최소 5건은 사람이 대조하고 판정 불일치를 기록합니다.

## 막혔을 때

`Partial`은 전체 성공이 아닙니다. evaluator 입력 누락, judge quota, tool 실행 환경을 확인합니다. 다중 대화 시뮬레이션·멀티모달 평가·일부 evaluator는 Preview이며 기본 single-turn 평가와 구분합니다.

## 정리

평가용 모델·agent 호출 비용과 생성된 파일을 기록합니다. 실패 사례는 익명화한 후 회귀 테스트로 추가합니다. 실제 운영 trace를 무심코 학습 데이터로 전환하지 않습니다.
