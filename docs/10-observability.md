> **완성할 결과:** “왜 틀렸는지 / 왜 느린지 / 얼마나 썼는지”를 한 번의 실행 증거로 설명합니다.

## 목표

**Evaluation은 좋았는지, Trace는 무슨 일이 있었는지, Monitoring은 시간이 지나며 어떻게 변하는지**를 보여줍니다.

## 준비

L05 또는 L06 실행 결과, 프로젝트에 연결 가능한 Application Insights, 로그 읽기 권한이 필요합니다. 로그 수집·보존에도 비용이 있습니다.

새 전용 환경의 관리자는 `python scripts/azure_environment.py monitoring --live`로
Log Analytics/App Insights와 프로젝트 연결을 만듭니다.
동봉 Bicep의 연결 비밀은 Azure 내부에서만 참조하고 출력·Git·패키지에 넣지 않습니다.
30일 로그 보존과 일일 수집 제한은 총 과금의 강제 차단 장치가 아닙니다.

## 실행

### 1. 서버 측 추적부터 연결하기

**Agents → Traces → Connect**에서 Application Insights를 연결합니다. 버튼이 없으면 **Manage → Project details → Connected resources → Add connection → Application Insights** 경로를 사용합니다.

Prompt/Hosted agent의 server-side tracing은 연결 후 코드 변경 없이 시작하는 경로입니다. 자체 클라이언트 함수 내부 로직까지 모두 자동으로 추적되는 것은 아닙니다.

### 2. 새 실행을 만들고 찾기

합성 질문을 한 번 더 실행하고 response ID·시간을 기록합니다. 수집에 시간이 걸릴 수 있으므로 잠시 후 Traces에서 검색합니다. 현재 선택된 프로젝트와 시간 범위를 함께 확인하세요.

trace에서 다음을 찾습니다.

| 증거 | 기록 |
| --- | --- |
| agent/model 실행 | 이름·버전·전체 시간 |
| 검색 호출 | 실제 반환 문서·빈 결과 여부 |
| 함수/MCP 호출 | 도구 이름·인수·오류 |
| model usage | input/output token, 가능한 비용 지표 |
| conversation/response | 사용자 요청과 실행의 연결 |

### 3. 세 가지 실패를 구분하기

**잘못된 정책 답변:** 올바른 문서가 검색됐는가 → 검색되지 않았다면 retrieval 문제 → 검색됐다면 지시·모델·답변 합성 문제.

**느린 답변:** 전체 지연을 모델, 검색, 도구, 네트워크/대기 단계로 나눕니다. 도구가 느린데 모델을 바꾸는 처방을 하지 않습니다.

**함수는 성공했는데 답변이 실패:** 도구 출력이 같은 conversation/call ID에 반영됐는지, final output이 완료됐는지 봅니다.

동봉 CLI는 실제 응답 파일의 response/trace ID로 App Insights를 조회합니다.

```bash
python samples/trace_lab.py --input results/실제-responses.jsonl --app-id 실제-AppInsights-app-ID --agent 실제-agent-name
python samples/trace_lab.py --input results/실제-responses.jsonl --app-id 실제-AppInsights-app-ID --agent 실제-agent-name --live
```

먼저 KQL을 출력해 범위를 검토합니다. 최근 24시간, 최대 200행이며 token/본문 전체를 조회하지 않습니다.
`app-id`는 계측 키나 connection string이 아닙니다. 조회 결과 0행은 **상관관계 미확인**으로 실패하며,
request ID를 trace ID로 바꾸어 채우지 않습니다. Hosted 응답의 `contract.sha256`과 version도 함께 대조합니다.

### 4. 선택: 클라이언트 추적 추가하기

자체 함수나 외부 애플리케이션 내부까지 보려면 OpenTelemetry와 사용하는 프레임워크의 instrumentation을 추가합니다. VS Code Toolkit의 로컬 OTLP tracing을 활용하면 클라우드 로그 없이 개발 중 실행을 볼 수 있습니다.

민감한 입력·출력의 원문 수집은 기본값으로 켜지 않습니다. trace/span ID로 연결하고, 필요한 업무 지표만 최소 수집하세요. server-side와 client-side trace를 중복으로 내보내지 않는지도 확인합니다.

### 5. 조건부: 모니터링과 지속 평가

Monitoring dashboard와 continuous evaluation은 Preview 범위를 확인한 뒤 비운영 환경에서 사용합니다. 작은 샘플링 비율, 적은 evaluator, 별도 judge quota부터 시작합니다.

예: 하루 1,000회 요청에서 5%를 평가하면 먼저 50건이 평가 대상이 됩니다. evaluator 수, 재시도, 여러 turn이 비용에 추가 영향을 줍니다. **샘플링 비율만으로 전체 비용을 계산하지 않습니다.**

사용자 thumbs-up/down은 유용한 신호지만 정답 라벨이 아닙니다. 실패 trace → 익명화·검토 → 평가 데이터 → prompt 수정 → 재평가로 연결합니다. traces-to-dataset·cluster analysis 등은 Preview 상태를 확인합니다.

## 성공 기준

새 실행 하나를 trace에서 찾았고, 실제 bottleneck 또는 실패 지점을 근거로 설명합니다. trace가 보이지 않는 상태를 “오류 없음”으로 기록하지 않습니다.

## 막혔을 때

프로젝트 권한만으로 로그 조회가 허용되지 않을 수 있습니다. Application Insights/Log Analytics 쪽 읽기 권한, 연결 상태, 수집 지연, 시간 필터를 확인합니다. 보호 테이블에는 별도 권한이 필요할 수 있습니다.

## 정리

진단할 trace ID와 최소 증거만 기록합니다. 로그의 보존 기간·원문 포함 여부·접근자를 정하고 불필요한 지속 평가를 중지합니다.
