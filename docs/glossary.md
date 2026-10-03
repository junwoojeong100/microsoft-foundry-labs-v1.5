> **모델은 생각하고, agent는 목표를 수행하고, 도구는 실제 기능을 제공하며, 운영 계층은 그 행동을 확인·통제합니다.**

## 시작·PC 준비

| 용어 | 쉬운 뜻 | 혼동하지 않을 것 |
| --- | --- | --- |
| Azure | Microsoft의 클라우드 서비스 | 내 PC에서만 실행되는 프로그램 |
| Tenant / Microsoft Entra ID | 로그인 계정과 조직을 관리하는 경계 / ID 서비스 | 비용을 청구하는 구독 |
| Subscription / Resource group | 비용·관리 범위 / 그 안의 자원 묶음 | Foundry 프로젝트와 같은 객체 |
| Portal / Playground | 브라우저 관리 화면 / 입력을 보내 답변을 시험하는 화면 | 가이드를 읽는 이 웹페이지 |
| Endpoint | 코드가 요청을 보내는 서비스 주소 | 로그인 권한이나 API key |
| CLI / Terminal / SDK | 명령줄 도구 / 명령을 입력하는 창 / 코드에서 서비스를 쓰는 라이브러리 | 세 가지 모두 설치하는 하나의 앱 |
| `.env` / venv | 프로젝트 설정 파일 / Python 패키지를 분리하는 폴더 | 같은 환경 기능 |
| JSON / JSONL | 이름과 값으로 쓰는 데이터 / 한 줄에 JSON 하나인 기록 파일 | 터미널에서 실행할 명령 |
| `true` / `false` / `null` | 참 / 거짓 / 값 없음. 예: `order_submitted=false`는 주문하지 않았다는 뜻 | `null`을 성공·0원·문제없음으로 해석 |
| Receipt | 실습이 만든 자원 ID·소유 범위를 기록한 파일 | 결제 영수증이나 삭제 승인 자체 |
| RBAC / Scope | 역할 기반 권한 / 그 권한이 적용되는 범위 | 로그인만 하면 얻는 전체 권한 |
| Foundry resource | 보안·관리·청구 관련 자원을 묶는 상위 Azure 자원 | agent 한 개 |
| Project | agent·연결·데이터 등의 작업 공간 | Classic hub |

## 모델·문서·도구

| 용어 | 쉬운 뜻 | 혼동하지 않을 것 |
| --- | --- | --- |
| Model ID | 공급자가 정의한 모델 이름 | 내 deployment name |
| Model version | 모델의 특정 버전 | agent version |
| Deployment | API로 호출하도록 준비한 모델 | 모델 카탈로그 카드 |
| Prompt / Instructions | 이번 요청에 보내는 입력 / 에이전트가 따를 공통 지시문 | 실제 권한이나 회사 문서 자체 |
| Token / Latency | 모델이 입력·출력을 처리하는 조각 단위 / 응답까지 걸린 시간 | 토큰을 단어 수·글자 수·비용 금액과 같다고 생각 |
| Prompt Agent | model·instructions·tools로 정의한 관리형 agent | prompt 문자열 하나 |
| Hosted Agent | 내 코드/프레임워크를 Foundry에서 실행 | 로컬 Python 실행 |
| Conversation | 여러 turn의 대화 맥락 | 장기 memory |
| Response | 한 번의 모델/agent 실행 결과 | 최종 텍스트만 |
| Tool | agent가 호출할 수 있는 기능 | 호출 허가 자체 |
| SKU / Schema | 여기서는 `NB-14` 같은 품목 코드 / 입력·출력 이름과 타입의 약속 | Azure 배포의 SKU는 서비스 유형이며 품목 코드와 다른 문맥 |
| Function calling | 모델 요청을 앱의 함수가 실행하는 패턴 | 모델 안의 Python 실행 |
| MCP | 도구/맥락을 연결하는 공통 protocol | 권한을 주는 보안 정책 |
| OpenAPI | HTTP API 입력·출력 계약 | API를 배포하는 플랫폼 |
| A2A | agent 간 기능 호출/협업 protocol | 한 프로세스의 함수 호출 |
| Toolbox | 관리형 도구 묶음과 MCP endpoint | 모든 도구 유형을 무조건 담는 상자 |
| Skill | 반복 수행 방법을 재사용 가능하게 묶음 | role assignment |
| RAG | 검색한 근거를 이용한 답 생성 | 모델 가중치 학습 |
| Vector store / Indexing | 검색용 문서 보관소 / 문서를 검색할 수 있게 처리하는 과정 | 파일 업로드 완료를 검색 준비 완료로 처리 |
| Citation | 답변의 주장을 뒷받침하는 실제 근거 연결 | 모델이 적은 파일 이름만으로 근거 확인 완료 |
| Embedding | 의미를 수치 벡터로 표현 | 자연어 정답 |
| Hybrid search | keyword와 vector를 함께 사용 | multi-agent |
| Foundry IQ | 여러 소스의 기업 지식 검색 계층 | Fabric/Work IQ의 새 이름 |

## 평가·운영·심화

| 용어 | 쉬운 뜻 | 혼동하지 않을 것 |
| --- | --- | --- |
| Memory | 대화 사이에 유지할 기억 | 원본 회사 규정 저장소 |
| Routine | 시간/이벤트에 agent를 호출 | 복잡한 orchestration 자체 |
| Autopilot | agent user account를 포함한 조직의 지속적 agent | 모든 자동 실행 |
| Evaluation | 기대 행동과 실제 결과를 비교 | 문자열이 비어 있지 않은지 검사 |
| Judge / Native evaluation | 채점용 모델 / Foundry 서비스에서 수행한 평가 | 답을 만든 모델이나 무조건 옳은 판정 |
| Dev / Holdout | 개선 중 보는 연습 자료 / 개선에 노출하지 않는 별도 시험 자료 | 모든 `holdout` 이름 파일이 항상 미노출이라는 보장 |
| Groundedness | 제공 근거에 답이 뒷받침되는 정도 | 세계의 모든 사실에 대한 진실성 |
| Trace / Span | 실행 전체 경로 / 개별 작업 구간 | 원문을 무제한 저장할 허가 |
| Guardrail | 위험 탐지와 대응 규칙 묶음 | 업무 시스템의 인증·승인 |
| Control Plane | fleet 관점의 관리·관찰·정책 인터페이스 | runtime 자체 |
| AI Gateway | 요청의 정책·라우팅·한도를 적용하는 계층 | 모든 보안 문제의 자동 해결 |
| GA / Preview | 지원 상태와 사용 조건 | 모든 지역의 가용성 |
| Quota / Capacity | 사용 허용량 / 실제 제공 용량 | 청구 상한 |
| SFT / DPO / RFT | 예시 / 선호 / 보상 기반 모델 개선 | 문서를 검색에 추가하는 작업 |
| OIDC | CI 등이 짧은 수명의 신뢰 기반 인증을 받는 방식 | 장기 비밀 문자열 |
| CMK | 고객이 관리하는 암호화 키 | 모든 기능·모든 경로의 격리 |

## 가장 작은 해법 고르기

| 지금 필요한 것 | 가장 작은 출발점 | 다음 단계 |
| --- | --- | --- |
| 요약 한 번 | 모델 호출 | 반복 업무가 생기면 agent |
| 파일 3개 답변 | File search | index 제어 필요 시 Search |
| 여러 소스의 기업 지식 | Foundry IQ 검토 | ACL·freshness·관측 |
| API 하나 호출 | 함수/OpenAPI | 재사용 시 Toolbox |
| 사용자 지정 실행 코드 | Hosted Agent | CI/CD·scale·운영 |
| 단순 주기적 호출 | Routine | 복잡한 분기면 framework |
| 발화 기반 경험 | Voice Agent 검토 | 음성 품질·세션·도구 |
| 배포 전 품질 확인 | 고정 데이터 평가 | 운영 sampled evaluation |
| 팀별 AI 자산 통제 | RBAC·정책·Control Plane | gateway·보안/정보보호 연계 |

## 이 가이드의 상태 표기

**GA**는 해당 기능의 확인된 범위입니다. **부분 GA / 혼합**은 API·포털·세부 기능의 상태가 다름을 뜻합니다. **Preview**는 비운영 선택 실습으로 취급합니다. **조건부 실습**은 추가 자원·관리자·라이선스가 준비됐을 때만 실행합니다. **설계/참고**는 실제 cloud 성공으로 합산하지 않습니다.
