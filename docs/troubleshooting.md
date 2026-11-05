> **먼저:** 보내기/생성을 반복하지 않습니다. 내 전용 scope·실제 오류·시각·이미 생성된 대상을 확인한 뒤 한 단계만 수정합니다.

## 증상별 다음 행동

| 증상 | 포털에서 확인 | 다음 행동 |
| --- | --- | --- |
| 로그인 필요·잘못된 tenant | 새 창의 계정·디렉터리·구독 | 허용 계정으로 직접 로그인. 인증은 녹화 제외 |
| 메뉴가 다름 | 새 Microsoft Foundry 여부·현재 프로젝트·공식 문서 | classic/new 경로를 구분. 다른 프로젝트를 대신 사용하지 않음 |
| 새 프로젝트 선택이 안 됨 | 초기 홈의 `Create new → Microsoft Foundry resource → Next` | Advanced options에서 전용 기존 그룹·account·지역 확인 |
| 401 | 세션 만료·계정·현재 프로젝트 | 새 로그인 창으로 재인증. token/key를 복사하지 않음 |
| 403 | 내 역할·정확한 scope·runtime/data/log identity | 필요한 최소 작업과 오류를 담당자에게 전달. Owner/공개 전환 금지 |
| 404·배포 없음 | 실제 account·project·deployment 이름 | catalog 모델명과 deployment를 구분. 새 자원 반복 생성 금지 |
| 모델/버전 없음 | 카탈로그 필터·지역·구독·지원 버전 | 원본 대상 차단으로 기록. 다른 모델로 몰래 대체하지 않음 |
| quota·429 | 배포 SKU·TPM·같은 account의 한도 | 전송 중단. 자동 한도 확대·PTU·다른 지역 생성 금지 |
| 생성 버튼 뒤 결과 없음 | Notifications·Deployments·실제 자원 목록 | 성공/실패를 먼저 확인. 중복 제출하지 않음 |
| Application Insights 목록 비어 있음 | 전용 workspace·Application Insights 실제 생성 여부 | Azure portal에서 workspace 먼저 생성 후 Insights에 선택. Microsoft Foundry 연결 목록 Refresh |
| Insights가 다른 그룹 workspace를 기본 선택 | Basics의 정확한 workspace | 내 전용 workspace로 바꾼 뒤 Review. 기본 공유 자원을 묵인하지 않음 |
| 파일 업로드 뒤 답 없음 | vector store 처리 상태·실패 수·agent 연결 | 3파일 Ready 확인. 다운로드 ZIP 전체를 올리지 않음 |
| 인용이 없음/가짜 | 실제 citation annotation·원본 파일/절 | 없는 citation을 후처리로 만들지 않음. 검색 실패로 남김 |
| 재고 조회·초안 저장했다고 답함 | 실제 연결 도구와 output·저장 기록 | 포털 함수 backend 없으면 미실행. 자연어·schema는 증거가 아님 |
| MCP 승인이 반복됨 | 서버 URL·allowlist·요청별 승인 | Learn의 읽기 도구만 승인. 쓰기·다른 서버·승인 해제는 중단 |
| 평가 입력 mapping 없음 | 대상 유형·CSV header·제공된 필드 | query는 agent 입력, context/ground_truth는 evaluator용. 예상 답을 response로 입력 금지 |
| 평가 Partial/Failed·행 누락 | 실제 12행·run 상세·오류 | 실패를 보존. 성공 행만으로 평균·gate를 만들지 않음 |
| Traces가 비어 있음 | 요청 전 로그 연결·기간·agent/version·로그 읽기 역할 | 같은 요청의 시각/ID로 확인. 예전 요청 소급 수집을 기대하지 않음 |
| L12/L13 SDK 의존성 충돌 | 현재 Python 환경·설치한 requirements | Hosted 2.7.0과 MAF 2.6.0의 project SDK를 별도 환경에 설치. 기존 공용 환경을 덮어쓰지 않음 |
| MAF가 `PLAN ONLY`만 출력 | 실행 명령의 `--offline` 또는 승인된 `--live` | 기본 계획은 실행이 아님. 먼저 네트워크 차단 fixture 사용 |
| CLI 소유 receipt 없음 | L01의 기존 scope·태그·프로젝트·언어 | L12/L13의 읽기 전용 `adopt_portal.py`로 검증. 수작업 소유 주장·중복 `create`/`foundation` 금지 |
| Hosted Search schema/hash 오류 | 코드의 정책 절·1536차원 schema와 기존 Search 결과 | 임의 포털 index를 호환으로 가장하지 않음. 승인 범위에서만 L12 초기화 |
| MAF handoff 결과 없음 | 실제 tool 호출·specialist 응답·호출 상한 | 분류 문장·직접 답변으로 대체하지 않고 실패 보존. 원격 A2A·업무 승인과 구분 |
| Memory UI 없음 | 실제 연결·store·scope 노출·지원 조건 | CRUD/격리 미실행. “기억했다”를 item 저장 증거로 삼지 않음 |
| Routines 메뉴 없음 | 지역·구독 기능 활성·agent 종류 | 미활성 기록. CLI·다른 지역 생성으로 우회하지 않음 |
| Routine 시간이 다름 | 브라우저 현지 시간대·One-time/Recurring | 기본은 생성 전 취소. 시간대 고정 API 기능을 UI로 가장하지 않음 |
| 비용 0원 | 날짜·통화·그룹 filter·집계 지연 | 비용 종료로 판단하지 않음. 보존 자원 다음 확인 시각 지정 |

## 요청별로 남길 정보

질문·원문·오류·시각·대상 name/version·표시 response/trace ID를 비공개로 적습니다. 원문과 실패를 나중에 고치지 않습니다. token·key·connection string·계정·사람 목록을 공유하지 않습니다.

## 읽기와 실제 실행

회색 설정 화면·과거 screenshot·영상·진도 체크는 내 실행 증거가 아닙니다. L12–L14의 실제 코드 실행은 각 장의 로그로 확인하며 offline fixture를 Microsoft Azure 증거로 바꾸지 않습니다. 포털에 없는 Function backend·Memory CRUD·실제 승인·게시는 성공으로 추정하지 않습니다. [진행표](#instructor)에서 수행 범위를 나눕니다.
