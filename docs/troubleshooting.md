> **먼저 확인할 네 가지:** 지금 선택한 프로젝트, 실제 endpoint, 호출 identity, 실행한 SDK 환경.

## Azure에 연결하기 전 막혔다면

| 보이는 증상 | 지금 할 일 |
| --- | --- |
| 명령을 어디에 넣을지 모르겠음 | VS Code에서 실습 폴더를 열고 **터미널 → 새 터미널**. 브라우저 주소창에 넣지 않음 |
| `python3` / `python3.13`을 찾지 못함 | Python 설치와 버전 확인. Windows는 L01의 `py -3.13` 경로 사용 |
| `can't open file` / `No such file or directory` | 연 폴더에 `samples`·`data`·`requirements.txt`가 함께 있는지 확인. `samples` 안에서 명령을 실행하지 않음 |
| Python의 `>>>` 또는 `SyntaxError` | `exit()`로 Python을 나온 뒤 터미널에서 명령 실행. 질문·JSON·`.env` 설정은 본문이 지정한 곳에 입력 |
| Windows의 `source` / `curl --fail` 오류 | L01의 `.venv\Scripts\python.exe` 사용. HTTP 확인은 `curl.exe` 사용 |
| 어제 되던 `python`에서 패키지를 못 찾음 | [L01 새 터미널 확인](#l01-new-terminal)으로 현재 실행기 경로 확인. 다른 Python에 패키지를 다시 설치하지 않음 |
| `read-result`에서 파일·형식·언어 오류 | L06의 `Responses:` 경로와 `-responses.jsonl` 끝부분 확인. 소유 receipt나 L08 JSON은 다른 형식이며 새 유료 호출로 해결하지 않음 |
| 포털에서 프로젝트가 안 보임 | 올바른 계정·조직과 제공된 프로젝트 이름을 강사에게 확인. 새 프로젝트나 구독을 임의로 만들지 않음 |

## 60초 진단 순서

1. 오류가 **로컬 설치 / 관리 평면 / 모델 호출 / agent / tool / 평가 / 로그** 중 어디서 났는지 분류합니다.
2. 발생 시각, status/error code, request/response ID를 기록합니다. token·API key는 기록하지 않습니다.
3. 기존 출력·파일·설정을 먼저 읽습니다. 새 유료 요청은 필요성과 범위를 확인한 뒤에만 재현합니다. 기능을 한꺼번에 다시 만들지 않습니다.

## 증상별 해결표

| 증상 | 먼저 확인 | 다음 행동 | 하지 말 것 |
| --- | --- | --- | --- |
| 401 | CLI 로그인·tenant·token audience | 올바른 tenant로 로그인, 서비스에 맞는 인증 | 토큰을 채팅/스크린샷에 붙이기 |
| 403 | data-plane 역할, agent/project identity, 네트워크 | 해당 scope와 private 경로를 분리 점검 | 구독 Owner를 모두에게 부여 |
| 404 | project endpoint, 모델 배포 이름, agent version | 포털에서 값을 다시 복사 | model ID와 deployment name을 같다고 가정 |
| 429 | RPM/TPM·judge quota·동시 실행 | 입력/동시성 축소, Retry-After, 제한된 재시도 | 무한 loop로 재호출 |
| quota는 있는데 배포 실패 | capacity, 유형·지역·접근 제한 | 다른 승인된 배포 조합 검토 | 국가/지역 정책 무시 |
| 연결 timeout | DNS·proxy·private endpoint·방화벽 | 승인된 VNet 내 환경에서 확인 | public access 켜서 통과 |
| `PublicNetworkAccessDisabled` | 실행 위치가 승인된 경로 안인지 | VPN/개발 VM 등 지원 경로 사용 | 리소스 보안 해제 |
| `ImportError` / module 없음 | Python 경로·venv·requirements | 해당 venv Python으로 설치/실행 | 전역 pip에 무작정 재설치 |
| dependency conflict | 기본/advanced 환경 혼용 | 두 requirements와 venv 분리 | 최신 버전 하나만 억지로 올리기 |
| `.env` 오류 | 이름·형식·placeholder·저장 여부 | `.env.example`에서 현재 장에 필요한 값만 입력하고 나머지는 비움 | API key 추가·`.env.txt`로 저장 |
| agent가 도구 성공을 주장하지만 호출 없음 | actual tool call·trace | 프롬프트와 도구 registration 검사 | 자연어 답변만 믿기 |
| 함수 도구가 멈춤 | 클라이언트 실행 loop 유무 | SDK runner 또는 hosted로 전환 | 포털이 로컬 함수를 실행할 것이라 기대 |
| file 검색 결과 없음 | ingest status·store ID·파일 내용 | 파일→store→agent 연결 순서 확인 | upload 완료=인덱싱 완료로 처리 |
| citation 없는 정답 | 실제 annotation과 원문 | citation을 UI에서 보존/표시 | 파일 이름 문자열을 증거로 간주 |
| IQ 권한 누출 | ACL metadata·user token·서버 검증 | 원본부터 query-time 권한까지 추적 | prompt로만 접근 통제 |
| MCP 승인 후 진행 안 됨 | approval request ID·동일 conversation | 올바른 승인 응답을 돌려주기 | 모든 요청 자동 승인 |
| Toolbox 403 | developer·agent identity·user 위임 구분 | 실제 호출 주체에 최소 권한 | creator 권한이 자동 상속된다고 판단 |
| 평가 `Partial` | evaluator 필수 필드·judge quota·tool runtime | 실패 evaluator를 확인하고 재실행 | 완료된 일부만으로 평균 산출 |
| Gate에서 `null` 오류 | 누락된 결과·평가자 오류·해당 기준 | 실제 원본과 요구 필드를 확인하고 미확인은 미확인으로 유지 | `true` 일괄 입력·기준 완화 |
| trace 없음 | App Insights 연결·권한·시간·수집 지연 | 기존 response ID와 조회 범위를 먼저 대조 | 반복 모델 호출·빈 화면=오류 없음 |
| memory가 안 보임 | scope·새 conversation·업데이트 지연 | item/retrieval을 직접 확인 | 출력 형식만으로 기억 여부 판정 |
| Teams 게시 후 응답 없음 | active version·Bot route·도구 실행 위치 | 게시와 실제 호출을 따로 테스트 | 앱 목록 표시를 최종 성공으로 판단 |
| 비용이 계속 증가 | routine·voice·지속 평가·Search/PTU/runtime | 활성·유휴·고정 비용 분리 | 브라우저 닫기만 하기 |
| cleanup 실패 | receipt endpoint·권한·소유권 | 남은 ID를 기록하고 재시도 | 전체 리소스 그룹 삭제 |

## 관리자 전달

외부 진단 workspace나 조직 정책과 관련된 오류는 governance 담당자에게 전달합니다. 정확한 자원·correlation ID는 승인된 비공개 경로로 공유하고, 담당자의 승인 없이 외부 자원을 조회하거나 정책·권한을 변경하지 않습니다. 오류를 숨기거나 광범위한 역할을 추가해 우회하지 않습니다.

## 문의에 첨부할 안전한 정보

웹 도움말을 다 읽었으면 **읽던 실습으로 돌아가기**를 선택합니다. 기본·90분 경로와 진도는 그대로 유지됩니다. 휴대폰에서는 **목차**에서 도움말을 다시 찾을 수 있습니다.

```text
모듈:
실행 방식: portal / SDK / hosted / 설계
SDK 환경: 기본 또는 advanced
오류 발생 시각과 타임존:
status / error code:
response 또는 request ID:
기대 결과:
실제 결과:
직전 변경:
이미 확인한 항목:
남아 있을 수 있는 유료 자원:
```

내부 endpoint·tenant·subscription ID도 공유 대상에 맞춰 가립니다. 비밀·토큰·실제 사용자 데이터는 첨부하지 않습니다.

## 화면이 문서와 다를 때

새/Classic 포털, 기능의 Preview 접근, tenant rollout, 지역, RBAC를 먼저 확인합니다. 버튼 이름이 다르면 **만들려는 자원과 동작**을 기준으로 공식 출처를 확인합니다. 사진과의 일치보다 해당 단계의 작업·필드·성공 기준을 확인하며 진행합니다.
