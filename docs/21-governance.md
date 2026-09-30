> **완성할 결과:** 여러 agent를 운영할 때 identity·데이터·네트워크·정책·비용의 통제 책임을 한 장으로 설명합니다.

## 목표

**Control Plane의 화면이 보이는 것과 정책이 실제로 강제되는 것은 다릅니다.** Operate의 Overview/Assets/Compliance와 Foundry AI Gateway 경험에는 Preview 범위가 있습니다.

## 개념과 실습 지도

**경험할 기능:** identity·RBAC scope·Control Plane·AI Gateway·private network의 책임 분리입니다.

**무엇이며 왜 중요한가요?** RBAC는 특정 주체가 특정 범위에서 할 수 있는 일을 정하고, 네트워크는 연결 가능한 경로를 정합니다. Gateway는 요청을 라우팅하거나 한도를 적용하는 진입점이며 원본 데이터 권한을 대신하지 않습니다. 직원 A에게 허용된 문서를 공용 캐시에 넣어 B에게 주는 문제는 네트워크가 private여도 생길 수 있습니다. 그래서 화면의 녹색 상태보다 실제 인증·데이터 흐름을 이해해야 합니다.

**어떻게 사용하나요?** 요청 하나가 사용자→agent→도구→데이터를 지날 때 각 단계의 identity·권한·네트워크를 그립니다. 포털에서는 현재 프로젝트 Manage와 여러 자산을 보는 Operate의 범위를 구분합니다. 정책을 바꾸는 대신 먼저 허용/거절 조건과 감사 담당자를 설계하세요.

**어디서 실행하나요?** 기본은 포털 읽기와 설계입니다. [infra/main.bicep](../infra/main.bicep), [runtime_roles.py](../scripts/runtime_roles.py)는 이 키트가 다루는 범위를 이해하는 참고 코드이며, 열어 읽는 것과 실제 실행하여 역할을 부여하는 것은 다릅니다.

## 준비

기본 과제는 설계·읽기 전용 확인입니다. 실제 role assignment, gateway, private endpoint, 정책 변경은 관리자와 별도 승인 후 진행합니다.

## 실행

### 1. identity 네 가지를 분리하기

| Identity | 사용하는 곳 | 질문 |
| --- | --- | --- |
| 개발자 | 개발·배포·평가 | 누가 agent를 바꿀 수 있나 |
| 프로젝트 managed identity | 연결 자원 | Search/Storage를 누가 읽나 |
| agent identity | runtime 도구 | agent 자신에게 어떤 권한이 있나 |
| 최종 사용자 | 위임된 데이터 접근 | 이 사용자가 원본 문서를 볼 수 있나 |

각 identity의 role·scope·만료/회수 담당자를 기록합니다. “agent가 접근할 수 있으니 사용자도 모두 볼 수 있다”는 설계를 하지 않습니다.

### 2. Control Plane에서 fleet 확인하기

**Operate → Assets**에서 권한이 허용하는 agent/model/tool을 찾습니다. 다른 프로젝트의 자원이 어떻게 보이는지 확인합니다. **Manage**는 현재 선택한 프로젝트/리소스의 quota·details·gateway 등이고, **Operate**는 fleet 관점입니다.

실행 상태·비용·경보·평가·정책 정보를 비교합니다. 외부 agent 등록은 관찰 범위를 늘리는 기능이며, 등록했다고 그 agent에 Foundry runtime guardrail이 자동 적용되지 않습니다.

### 3. AI Gateway 선택 과제

APIM 기반 gateway가 필요한 이유를 하나 정합니다: 토큰 한도, rate limit, 허용 backend, 관측, 라우팅 등.

| 정책 | 반드시 확인할 것 |
| --- | --- |
| rate/token limit | 사용자/agent/project 식별 기준과 초과 응답 |
| backend routing/fallback | 허용 모델·지역만 사용하는가 |
| caching | 사용자/권한별 데이터가 섞이지 않는가 |
| logging | prompt·비밀·PII가 로그에 노출되지 않는가 |
| tool/API 관리 | 원본 서비스 권한과 gateway 정책이 모두 있는가 |

작은 비운영 테스트 한도를 초과시켜 실제 거절 응답과 로그를 확인합니다. **quota는 청구 한도가 아니고, 예산 알림도 hard stop이 아닙니다.** Foundry의 gateway UI 상태와 Azure API Management 자체 서비스의 상태를 혼동하지 않습니다.

### 4. 네트워크 설계 과제

세 경로를 다른 색으로 그립니다: **사용자 → Foundry**, **Foundry → 도구/데이터**, **도구/데이터 → 외부**.

| 구성 | 해결하는 것 | 해결하지 않는 것 |
| --- | --- | --- |
| Private endpoint | Foundry로 들어오는 private 연결 | 모든 tool egress 차단 |
| VNet/managed network 설정 | 지원되는 outbound 경로 | 미지원 도구를 자동 지원 |
| Private DNS | 올바른 주소 해석 | RBAC·앱 인증 |
| Firewall/egress policy | 허용 목적지 통제 | 데이터 자체의 사용자 ACL |

private Search/Storage 등에는 각각 필요한 private endpoint를 준비합니다. Foundry private endpoint 하나가 모든 연결 자원을 private로 만드는 것은 아닙니다.

**대표적인 제약:** Memory store의 VNet 미지원, Routines의 CMK 미지원, 일부 browser/computer/image 도구의 network isolation 미지원, public web/Bing/SharePoint 도구의 public 통신. Hosted Agent private ACR은 **2026-06-25 이후 생성된 프로젝트** 등 문서의 조건을 재확인합니다.

### 5. 정책·암호화·정보 보호 확인하기

Azure Policy로 허용 모델·배포 유형·네트워크 조건을 검토합니다. CMK는 지원 자원의 저장 데이터 보호이고 runtime의 유출 방지나 모든 기능 지원을 의미하지 않습니다.

Defender·Purview·Entra 통합은 각 제품의 구성·권한·라이선스가 필요할 수 있습니다. 대시보드 존재를 조직 compliance 인증으로 제시하지 않습니다. 진단 로그와 content provenance, 사용자에게 AI 사용을 알리는 방식도 운영 문서에 포함합니다.

## 성공 기준

네트워크 경로, 네 가지 identity, 허용 모델/도구, 금지 데이터, 감사·회수 담당자가 명확합니다. 실제 테스트했다면 허용/거절 양쪽 증거를 남깁니다.

## 막혔을 때

403을 무조건 RBAC 문제로 판단하지 않습니다. endpoint DNS, public network 차단, VNet 경로와 identity를 분리합니다. 기능 미지원은 권한을 넓힌다고 해결되지 않습니다.

## 정리

임시 역할·정책·gateway·연결을 기록하고 관리자 절차로 회수합니다. 공유 네트워크와 운영 정책을 임의 삭제하지 않습니다.
