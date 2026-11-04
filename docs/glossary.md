## 이름과 선택 기준

| 용어 | 뜻·포털에서의 판단 |
| --- | --- |
| Microsoft Azure | 구독·리소스·비용·권한을 관리하는 클라우드 플랫폼 |
| Azure portal | 전용 그룹·로그·Search·Storage·IAM·비용을 관리하는 화면 |
| Microsoft Foundry / Foundry portal | 모델·agent·지식·평가·관측을 다루는 개발/운영 경험 |
| Account / Project | AI 자원과 그 안의 작업 범위. 현재 선택된 이름을 매번 확인 |
| Resource group | 함께 소유·비용·수명주기를 관리하는 묶음. 전용 그룹만 사용 |
| Model / Deployment | catalog 모델과 실제 호출할 배포 이름은 다름 |
| Version / SKU / TPM | 모델 버전·배포 처리 유형·분당 토큰 한도. TPM은 금액 상한 아님 |
| Global / Data Zone / Regional | 처리 위치 경계. 전 세계 처리와 저장 지역은 구분 |
| Prompt Agent | 모델·Instructions·서비스 도구로 정의하는 agent |
| Hosted Agent | 직접 작성한 코드/컨테이너 runtime. 포털 Instructions 저장으로 배포되지 않음 |
| Instructions / Chat | 지속 역할·규칙과 현재 대화 질문의 다른 입력 위치 |
| Conversation / Response | 대화와 개별 응답. 새 대화는 같은 대화 문맥을 이어받지 않음 |
| File search / RAG | 처리 완료 파일에서 실제 근거를 찾아 답하기 |
| Citation | 실제 응답 annotation의 문서 근거. 모델이 쓴 파일명만으로는 부족 |
| Function calling | 모델의 구조화 호출 요청과 실제 backend 실행은 별개 |
| Draft | 사람 승인 대기 초안. 저장 증거 없으면 저장됐다고 말하지 않음 |
| MCP / OpenAPI | 서버 도구 연결 규약과 HTTP API 계약. 둘 다 실제 서버·권한 필요 |
| Foundry Toolbox | 공통 도구 endpoint·버전 관리. 이 코스의 Learn MCP 시험과 별도 |
| Azure AI Search / Foundry IQ | index 검색과 knowledge source/base 경로. 추가 자원·권한 확인 |
| Embedding / Dimension | 텍스트 vector와 길이. 모델 output·index 차원 일치 필수 |
| Evaluation / Grader | 실제 출력 평가와 채점기. 예상 답을 agent 입력에 넣지 않음 |
| Ground truth | evaluator용 행동 요구사항. 실제 agent 응답·human approval 아님 |
| Gate / Holdout | 통과 기준과 독립 미사용 질문. 고정 12문항은 holdout 아님 |
| Guardrail / RBAC / ACL | 콘텐츠 통제·Microsoft Azure 작업 권한·문서별 접근. 서로 대체하지 않음 |
| Trace / Span | 같은 실행과 내부 작업의 실제 기록. 겹치는 duration은 합산 금지 |
| Manual role comparison | 사람이 복사·전달한 Chat 비교. SDK concurrency·handoff 실행 아님 |
| Memory / Scope / TTL | 서버 장기 기억·격리 key·보존 시간. 회상 문장만으로 CRUD·격리 증명 불가 |
| Routine / Dispatch | 자동 호출 규칙과 개별 실행 전달. 생성 폼 읽기≠예약 성공 |
| Agent / Creator identity | 기본 routine 실행 주체와 명시적으로 선택한 생성자 권한. 연결 소유자와 다름 |
| Publish / Active version | 버전 게시와 호출자가 쓰는 활성 대상 선택. 관찰≠전환 |
| RTO / RPO | 복구 시간/데이터 유실 목표. 계획≠실제 복구 시험 |
| Budget | 비용 알림. hard spending cap이 아니고 자동화·리소스 종료도 아님 |
| SDK / CLI / Skill | 개발자용 참고. 이 포털 학습 경로의 설치·실행 의존성이 아님 |

## 어디로 갈까요?

파일 3개 근거는 [L05](#l05), 함수 실행 경계는 [L06](#l06), 고정 평가 비교는 [L08](#l08), traces는 [L10](#l10)입니다. 추가 검색은 [L11](#l13), 실제 비용·보존은 [L19](#l12)에서 확인합니다.
