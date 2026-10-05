> **완성할 결과:** “왜 틀렸는지 / 왜 느린지 / 얼마나 썼는지”를 한 번의 실행 증거로 설명합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** L01에서 연결한 로그로 내 agent 실행을 조회하고 해석합니다.

**먼저 할 일:** L05/L06의 응답 ID·시간·에이전트 버전으로 Traces에서 같은 실행을 찾습니다.

**확인할 결과:** 관찰한 작업·시간·다음 조치를 적습니다. 로그 접근이 없으면 아래 합성 예제로 연습하고 실제 추적은 미확인으로 남깁니다.

</div>

## 목표

**Evaluation은 좋았는지, Trace는 무슨 일이 있었는지, Monitoring은 시간이 지나며 어떻게 변하는지**를 보여줍니다.

## 개념과 실습 지도

**경험할 기능:** 이미 실행한 질문 하나의 작업 순서와 소요 시간을 읽습니다.

**무엇이며 왜 중요한가요?** Trace는 한 요청의 실행 기록, span은 검색·모델·도구 같은 개별 작업입니다. 전체 시간만 보지 않고 어느 작업이 오래 걸렸는지 찾습니다. 로그가 없으면 “오류 없음”이 아니라 “미확인”입니다.

**어떻게 사용하나요?** L05·L06의 응답 ID·시간·버전으로 같은 실행을 찾습니다. 작업별 시간과 상태를 읽고 다음에 확인할 원인을 하나 고릅니다.

**어디서 실행하나요?** 기본은 포털의 **Traces**, [trace_lab.py](../samples/trace_lab.py)는 선택 조회입니다. 로그 접근이 없으면 아래 합성 시간표로 읽는 법만 연습합니다.

## 준비

L01에서 만든 Application Insights 연결·로그 읽기 권한과 자신의 L04–L06 결과를 사용합니다. Application Insights는 Azure의 로그 수집·조회 서비스이며 수집·보존에도 비용이 있습니다.

<details class="optional-path" markdown="1">
<summary>연결이 아직 없다면: 내 프로젝트의 로그 설정 보완</summary>

소유 기록의 `monitoring`과 포털 연결을 먼저 확인합니다. 없다면 **L01 5단계**의 `monitoring` 계획·실행으로 자신의 RG에 Log Analytics·App Insights·프로젝트 연결을 만듭니다. 이미 있는 자원을 다시 생성하지 않습니다. 30일 보존·일일 수집 제한은 총 과금의 강제 차단이 아닙니다.

포털 **Agents → Traces → Connect** 또는 **Manage → Project details → Connected resources**에서 자신의 App Insights 연결을 확인합니다. 기존 연결이 있으면 교체하지 않습니다. 로그는 **연결 이후 실행**부터 수집되며 이전 호출을 소급해서 만든 것이 아닙니다.

</details>

## 실행

### 1. 로그 수집 연결부터 확인하기

자기 에이전트의 **Traces**를 엽니다. **Connect**만 보이면 위 연결과 현재 프로젝트를 대조합니다. 403이면 자신의 App Insights/Log Analytics **IAM → View my access**에서 로그 읽기 권한을 확인하고 필요한 최소 범위의 역할을 설정합니다. 권한이 없으면 조회를 보류하고 실제 trace는 미확인으로 기록합니다.

Prompt/Hosted agent의 server-side tracing은 연결 후 코드 변경 없이 시작하는 경로입니다. 자체 클라이언트 함수 내부 로직까지 모두 자동으로 추적되는 것은 아닙니다.

### 2. 자기 실행 하나를 찾아 연결하기

연결 이후 수집된 L05/L06 실행이 있으면 먼저 그 결과를 사용합니다. 없다면 승인된 합성 질문 한 번만 실행하고 response ID·시간을 기록합니다. 목록이 비어 있다는 이유로 질문을 반복 전송하지 않습니다.

| 필요한 값 | 어디서 가져오나요? | 바르게 연결됐는지 확인 |
| --- | --- | --- |
| 응답 JSONL | L05/L06 SDK 마지막 `Responses:`에 출력된 `results/contoso-lab-…-responses.jsonl` | L06의 `read-result`로 기록 ID·응답 ID·에이전트·버전을 읽기. 원본에서는 `id`, `response_id`, `agent_name`, `configuration.agent_version` |
| agent 이름·버전 | 그 행의 값 또는 포털에서 직접 실행한 agent의 설정 | L08 평가 전용 agent나 L12 Hosted 이름으로 바꾸지 않음 |
| Application Insights 앱 ID | 내가 만든 환경의 `results/azure-environment.json` → `monitoring.appId.value` 또는 해당 자원의 Overview | `monitoring.appInsightsId.value`가 프로젝트 연결과 같은 자원인지 대조. 키/connection string을 복사하지 않음 |

포털만 사용했다면 그 response ID로 **포털 경로만** 진행해도 됩니다. 존재하지 않는 JSONL을 만들거나 L08의 JSON 비교 파일을 아래 JSONL 입력으로 넘기지 않습니다. 동봉 CLI는 최근 24시간만 조회하므로 오래된 결과는 포털의 승인된 보존 범위에서 읽거나 미확인으로 남깁니다.

![실행 기록 목록 예시. Prompt Agent의 Traces에서 ID 검색, 버전·상태·기간 필터와 실행 시간·토큰·예상 비용 열을 확인한다.](../assets/portal/06-traces.png)

**화면 따라 읽기:** **Build → Agents → 자신의 agent → Traces**에서 **Date range**와 **Version**을 먼저 맞춥니다. 검색창에는 자신의 trace/conversation/response ID를 넣고, 행을 열어 개별 작업을 확인합니다. **Completed**는 실행 완료 상태이지 답변 정답 여부가 아닙니다.

trace에서 다음을 찾습니다.

| 증거 | 기록 |
| --- | --- |
| agent/model 실행 | 이름·버전·시작 시각·전체 시간 |
| 검색 호출 | 실제 반환 문서·빈 결과 여부. 본문을 볼 권한이 없으면 미관찰 |
| 함수/MCP 호출 | 도구 이름·인수·오류. 로컬 함수 내부 span이 없으면 JSONL의 `tool_calls`로 별도 확인 |
| model usage | input/output token, 가능한 비용 지표. 없으면 0이 아니라 미수집 |
| conversation/response | 사용자 요청과 실행의 연결. 같은 trace의 `operation_Id`, 부모 `operation_ParentId`와 자식 `id` |

### 3. 세 가지 실패를 구분하기

**잘못된 정책 답변:** 올바른 문서가 검색됐는가 → 검색되지 않았다면 retrieval 문제 → 검색됐다면 지시·모델·답변 합성 문제.

**느린 답변:** 전체 지연을 모델, 검색, 도구, 네트워크/대기 단계로 나눕니다. 도구가 느린데 모델을 바꾸는 처방을 하지 않습니다.

**함수는 성공했는데 답변이 실패:** 도구 출력이 같은 conversation/call ID에 반영됐는지, final output이 완료됐는지 봅니다.

**시간을 읽는 예시 — 설명용 합성이며 실제 Azure trace가 아닙니다.** 아래 자식 작업은 겹치지 않고 순차 실행됐다고 가정합니다.

| 작업 | 시작~종료(ms) | 관찰 시간 | 판단 |
| --- | ---: | ---: | --- |
| 전체 요청 | 0~4,000 | 4,000ms | 부모 span; 아래 시간을 다시 더하지 않음 |
| 정책 검색 | 100~800 | 700ms | 근거 절이 맞는지도 별도로 확인 |
| 모델 응답 | 900~3,800 | 2,900ms | 가장 큰 관찰 구간; 출력 길이·토큰부터 조사 |
| 재고 도구 | 3,800~3,850 | 50ms | 이 예시에서는 주된 병목이 아님 |

관찰된 자식 합계는 3,650ms, 나머지는 350ms입니다. **350ms를 증거 없이 네트워크 지연이라고 단정하지 않습니다.** 병렬 span은 겹치므로 단순 합산도 불가능합니다. 실제 실행에서 모델이 길면 입력·출력 토큰과 반복 호출을, 검색이 길면 반환량·검색 단계를 먼저 봅니다. 정상 실행이라면 오류를 만들어내지 말고 가장 오래 걸린 관찰 구간과 미수집 구간을 구분해 설명하세요.

동봉 CLI는 실제 응답 파일의 response/trace ID로 App Insights를 조회합니다.

```bash
python samples/trace_lab.py --input results/실제-responses.jsonl --app-id 실제-AppInsights-app-ID --agent 실제-agent-name
python samples/trace_lab.py --input results/실제-responses.jsonl --app-id 실제-AppInsights-app-ID --agent 실제-agent-name --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `trace_lab.py` | `--input`은 실제 응답 JSONL, `--app-id`는 해당 Application Insights의 앱 ID, `--agent`는 조회할 agent 이름입니다. 파일에서 식별자를 읽고 KQL 계획을 출력합니다. | Azure 조회 없음. 시간 범위와 ID 조건이 자신의 실행만 가리키는지 확인합니다. |
| 2. 같은 명령에 `--live` | 확인한 KQL로 실제 로그를 읽습니다. 최근 24시간·최대 200행으로 제한되며 새 모델 추론을 실행하지 않습니다. | Azure 읽기 요청과 조회 결과 기록. 0행이면 상관관계 미확인이며 임의 ID로 채우지 않습니다. 로그 서비스의 이용 조건은 별도입니다. |

</div>

먼저 KQL을 출력해 범위를 검토합니다. 최근 24시간, 최대 200행이며 token/본문 전체를 조회하지 않습니다.
`app-id`는 계측 키나 connection string이 아닙니다. 조회 결과 0행은 **상관관계 미확인**으로 실패하며,
request ID를 trace ID로 바꾸어 채우지 않습니다. L12의 Hosted 결과를 선택했을 때만 `contract.sha256`과 version도 대조합니다. 기본 Prompt Agent JSONL에는 그 Hosted 계약을 요구하지 않습니다.

출력의 `input_rows`와 `correlated_rows`가 같고 `missing_case_ids`가 비어 있으면 **입력과 로그의 연결**이 확인된 것입니다. `model_response_spans_observed`와 `request_trace_ids_observed`는 관찰 계층이 다릅니다. 이 CLI는 연결을 검사하지, 병목이나 답변 정답을 자동 판정하지 않습니다. 출력된 `Evidence:` 파일의 조회 행과 포털 상세를 읽어 위 표를 자신의 값으로 작성하세요.

#### 포털 Traces와 실제 상관 조회 코드

포털에서는 **Traces**에서 agent·version·기간과 자신의 response ID를 선택합니다. 동봉 Python은 같은 ID를 JSONL에서 읽고 KQL을 만든 뒤 Application Insights에 한 번 읽기 요청을 보냅니다.

```python
rows = load_jsonl(args.input)
query = query_for(rows, args.agent)

result = rest.request(
    "POST",
    f"/v1/apps/{args.app_id}/query",
    {"query": query, "timespan": "P1D"},
)
report = correlation_report(rows, result)
```

| 포털에서 보는 값 | 코드가 사용하는 값 |
| --- | --- |
| Traces의 agent 필터 | `args.agent` |
| 요청 상세의 response/trace ID | `rows`의 `response_id` / `trace_id`, KQL의 `responseIds` / `traceIds` |
| Application Insights 앱 선택 | `args.app_id` (app ID이며 connection string이 아님) |
| 시간 범위 | `timespan="P1D"` 및 최근 24시간 KQL |
| 연결된 행 수 | `correlation_report()`의 `correlated_rows`와 `missing_case_ids` |

코드 경로는 **로그 읽기만** 하고 모델을 호출하지 않습니다. 0행이나 빠진 ID는 미관찰/실패로 남기며 포털 화면에서 보인 값으로 채우지 않습니다.

### 4. 선택: 클라이언트 추적 추가하기

자체 함수나 외부 애플리케이션 내부까지 보려면 OpenTelemetry와 사용하는 프레임워크의 instrumentation을 추가합니다. VS Code Toolkit의 로컬 OTLP tracing을 활용하면 클라우드 로그 없이 개발 중 실행을 볼 수 있습니다.

민감한 입력·출력의 원문 수집은 기본값으로 켜지 않습니다. trace/span ID로 연결하고, 필요한 업무 지표만 최소 수집하세요. server-side와 client-side trace를 중복으로 내보내지 않는지도 확인합니다.

### 5. 조건부: 모니터링과 지속 평가

Monitoring dashboard와 continuous evaluation은 Preview 범위를 확인한 뒤 비운영 환경에서 사용합니다. 작은 샘플링 비율, 적은 evaluator, 별도 judge quota부터 시작합니다.

예: 하루 1,000회 요청에서 5%를 평가하면 먼저 50건이 평가 대상이 됩니다. evaluator 수, 재시도, 여러 turn이 비용에 추가 영향을 줍니다. **샘플링 비율만으로 전체 비용을 계산하지 않습니다.**

사용자 thumbs-up/down은 유용한 신호지만 정답 라벨이 아닙니다. 실패 trace → 익명화·검토 → 평가 데이터 → prompt 수정 → 재평가로 연결합니다. traces-to-dataset·cluster analysis 등은 Preview 상태를 확인합니다.

## 성공 기준

자기 실행 하나의 **response/trace ID, 버전, 관찰된 작업·시간, 판단, 다음 조치**를 연결했습니다. 예시만 읽었다면 **설계 완료 / 실제 trace 미확인**으로 구분합니다. trace가 없는 상태를 “오류 없음”으로 기록하지 않습니다.

## 막혔을 때

| 증상 | 먼저 볼 것 | 다음 행동 |
| --- | --- | --- |
| JSONL을 열지 못함 / 실제 ID 없음 | `Responses:` 경로와 파일의 한 행 | L05/L06 출력 파일을 선택. 예시 ID나 L08 비교 JSON으로 대체하지 않음 |
| 403 | 프로젝트 역할과 별개인 로그 읽기 권한 | 내 App Insights/Log Analytics IAM에서 최소 역할·scope 확인. 권한이 없으면 조회 보류 |
| 0행 / 일부만 연결 | 프로젝트 연결, 실행 시각, 24시간 범위, 수집 지연 | 새 모델 요청 없이 범위와 ID를 먼저 대조. 여전히 없으면 상관관계 미확인 |
| 부모만 있고 함수·내용 없음 | instrumentation과 민감 내용 읽기 권한 | 기본 JSONL과 관찰 범위를 함께 기록. 원문 수집을 무조건 켜지 않음 |

## 정리

진단할 trace ID와 최소 증거만 기록합니다. 로그의 보존 기간·원문 포함 여부·접근자를 정하고 불필요한 지속 평가를 중지합니다.
