> **먼저 확인할 네 가지:** 지금 선택한 프로젝트, 실제 endpoint, 호출 identity, 실행한 SDK 환경.

## 60초 진단 순서

1. 오류가 **로컬 설치 / 관리 평면 / 모델 호출 / agent / tool / 평가 / 로그** 중 어디서 났는지 분류합니다.
2. 발생 시각, status/error code, request/response ID를 기록합니다. token·API key는 기록하지 않습니다.
3. 가장 작은 요청으로 재현합니다. 기능을 한꺼번에 다시 만들지 않습니다.

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
| `.env` 오류 | 이름·형식·placeholder | 지원되는 두 설정만 입력 | API key 추가 |
| agent가 도구 성공을 주장하지만 호출 없음 | actual tool call·trace | 프롬프트와 도구 registration 검사 | 자연어 답변만 믿기 |
| 함수 도구가 멈춤 | 클라이언트 실행 loop 유무 | SDK runner 또는 hosted로 전환 | 포털이 로컬 함수를 실행할 것이라 기대 |
| file 검색 결과 없음 | ingest status·store ID·파일 내용 | 파일→store→agent 연결 순서 확인 | upload 완료=인덱싱 완료로 처리 |
| citation 없는 정답 | 실제 annotation과 원문 | citation을 UI에서 보존/표시 | 파일 이름 문자열을 증거로 간주 |
| IQ 권한 누출 | ACL metadata·user token·서버 검증 | 원본부터 query-time 권한까지 추적 | prompt로만 접근 통제 |
| MCP 승인 후 진행 안 됨 | approval request ID·동일 conversation | 올바른 승인 응답을 돌려주기 | 모든 요청 자동 승인 |
| Toolbox 403 | developer·agent identity·user 위임 구분 | 실제 호출 주체에 최소 권한 | creator 권한이 자동 상속된다고 판단 |
| 평가 `Partial` | evaluator 필수 필드·judge quota·tool runtime | 실패 evaluator를 확인하고 재실행 | 완료된 일부만으로 평균 산출 |
| Gate에서 `null` 오류 | 사람 검토 누락 | 실제 응답과 근거를 검토해 boolean 기록 | `true` 일괄 입력 |
| trace 없음 | App Insights 연결·권한·시간·수집 지연 | 새 요청을 만들고 ID로 검색 | 빈 화면=실행 문제 없음 |
| memory가 안 보임 | scope·새 conversation·업데이트 지연 | item/retrieval을 직접 확인 | 출력 형식만으로 기억 여부 판정 |
| Teams 게시 후 응답 없음 | active version·Bot route·도구 실행 위치 | 게시와 실제 호출을 따로 테스트 | 앱 목록 표시를 최종 성공으로 판단 |
| 비용이 계속 증가 | routine·voice·지속 평가·Search/PTU/runtime | 활성·유휴·고정 비용 분리 | 브라우저 닫기만 하기 |
| cleanup 실패 | receipt endpoint·권한·소유권 | 남은 ID를 기록하고 재시도 | 전체 리소스 그룹 삭제 |

## 관리자 전달: 외부 로그 워크스페이스를 참조하는 진단 정책

**상태: 전달 내용 준비, 미발송·관리자 확인 대기.** [영어판 실행 요약](../index.html#l00)에 연결된 기존 영어 보고서는 상속된 조직 진단 설정 배포가 실습 그룹 밖의 존재하지 않는 Log Analytics workspace를 참조해 실패했다고 기록합니다. 실습 소유 foundation·observability 배포는 성공했습니다. 이 기록만으로 외부 workspace의 현재 상태나 조직 전체의 준수 상태를 확인했다고 판단하지 않습니다.

승인된 영어 v4 live에서는 **소유 RG 안의 실패 배포 1건**을 다시 읽어 `DeploymentFailed` / `ResourceNotFound`와 실제 correlation·오류 세부 정보를 비공개 `results/live-v4-policy-handoff.json`에 보존했습니다. 외부 workspace 조회, 관리자 발송, 정책 변경이나 remediation은 하지 않았으며 확인 대기 상태를 유지합니다.

후속 영어 v5에서도 이 외부 workspace나 조직 정책을 조회·변경하지 않았습니다. [새 dev 결과](../validation/english/automated-v5/quality.json)는 40건 전체 native 실행을 완료했지만, `v5-dev-30`의 필수 근거 누락으로 access 게이트가 실패했습니다. 97.5% 전체 점수나 정상 서비스 상태로 이 실패를 덮지 않으며, 봉인된 holdout을 열거나 실패 사례를 재샘플링하지 않습니다.
| 전달 항목 | 관리자 확인·반환 증거 |
| --- | --- |
| 원래 실패 찾기 | 소유 영어 리소스 그룹의 배포 이력에서 실패 배포 이름·UTC 시각·correlation ID·오류 코드·중첩 진단 설정 대상을 보존합니다. 조사 목적으로 실습 전체를 다시 배포하지 않습니다 |
| 담당 정책·소유자 | 실제 policy assignment/definition ID와 할당 scope를 오류·배포 세부 정보에서 확인하고 해당 관리 그룹/구독 governance 담당자에게 전달합니다 |
| 외부 의존성 확인 | 승인된 내부 채널에서 정확한 workspace resource ID·존재 여부·지역·의도된 소유자를 확인합니다. 공개 요약에는 이 식별자와 관리자 답변이 없습니다 |
| 수정 결정 | 권한 있는 소유자가 원래 workspace 복구 또는 정책 목적지 수정을 결정합니다. 정책 예외·역할 변경·자원 복구/삭제·remediation 배포는 각각 별도 승인이 필요합니다 |
| 완료 증거 | 원래 실패는 유지하고, 승인된 변경 번호·새 scoped remediation/배포 성공·진단 설정의 실제 목적지·승인된 로그 도착 확인을 별도로 남깁니다 |

전달 문안: “영어 Contoso 실습의 상속 진단 정책 소유자와 의도된 로그 목적지 확인을 요청합니다. 실습 자체 배포는 성공했으나 조직 진단 배포는 외부 workspace 누락을 보고했습니다. 정확한 assignment/workspace ID, 승인된 수정 결정 및 확인 증거를 내부 채널로 회신해 주세요. 실습 후속 작업은 조직 정책·권한·workspace 변경이나 자원 삭제를 승인하지 않았습니다.”

진단을 끄거나 실패 이력을 숨기거나, 광범위한 역할을 추가하거나, 경고를 없애려고 실습 그룹에 같은 이름의 workspace를 만들지 않습니다. 관리자 회신과 별도로 승인된 검증이 있기 전에는 **관리자 확인 대기** 상태를 유지합니다.

## 문의에 첨부할 안전한 정보

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

새/Classic 포털, 기능의 Preview 접근, tenant rollout, 지역, RBAC를 먼저 확인합니다. 버튼 이름이 다르면 **만들려는 자원과 동작**을 기준으로 공식 출처를 확인합니다. 오래된 화면을 현재 화면인 것처럼 사용하지 않기 위해 이 가이드는 고정 스크린샷보다 작업·필드·완료 기준을 중심으로 구성했습니다.
