## 목표

Azure portal과 Microsoft Foundry에서 내 scope·권한·연결·안전 경계를 읽기 전용으로 점검합니다. 정책 문장과 실제 enforcement를 구분합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 포털 읽기 전용 관찰과 결정표 실습. 역할·네트워크·정책을 변경하지 않습니다.

**먼저 할 일:** 내 자원 그룹·프로젝트·현재 사용자 역할만 확인합니다.

**확인할 결과:** 사용자/런타임/데이터 scope 구분, 증거 유무, 민감정보 없는 결정표.

</div>

## 개념과 실습 지도

**경험할 기능:** RBAC·managed identity·연결·guardrail·데이터 격리 관찰.

**무엇이며 왜 중요한가요?** Agent Instructions는 권한 시스템이 아닙니다. 같은 답변을 재사용하는 cache도 사용자·tenant·문서 ACL을 잃으면 정보 유출 경로가 됩니다.

**어떻게 사용하나요?** 내 접근과 연결의 실제 scope를 읽고 가상의 두 사용자 결정표를 검토합니다. 실제 금지 데이터 요청은 하지 않습니다.

**어디서 실행하나요?** Azure portal의 내 자원 IAM·Identity·Networking, Microsoft Foundry의 내 프로젝트 연결·agent 설정.

## 준비

사람 목록·메일·object ID·token·key는 녹화/공유하지 않습니다. `View my access` 등 내 역할 확인을 우선하고 타인의 전체 권한 목록은 열지 않습니다. 프로젝트 Contributor만으로 로그·Blob·Search 데이터 읽기가 된다고 가정하지 않습니다.

## 실행

### 1. 내 scope와 runtime identity 구분

녹화에는 IAM 역할 상세·Identity·Networking의 실제 값이 없습니다. 아래 진입점·경고 사진을 그 설정의 확인 결과로 쓰지 않습니다. 내 범위에서 읽을 수 없는 값은 `미노출/미검증`으로 남깁니다.

<div class="screen-step" markdown="1">

**Scope 확인: Overview에서 내 IAM 읽기로 이동**

![전용 그룹 Overview의 Access control IAM과 Tags 진입 위치.](../assets/portal/steps/rg-created.png)

**1 IAM:** `View my access`로 내 권한만 읽습니다. 이 그림은 메뉴 진입점이지 역할 목록·권한 검사 완료 화면이 아닙니다. **2 Tags:** 소유 기록과 scope를 먼저 대조합니다.

[자막 영상 01 · 01:04](../downloads/portal/index.html?clip=01-environment&t=64&lang=ko#01-environment)

</div>

<div class="screen-step" markdown="1">

**Runtime identity: 개인 로그인과 다를 수 있음**

![프로젝트 managed identity에 별도 역할을 요구하는 실제 Memory 설정 경고.](../assets/portal/steps/memory-warning.png)

**1 Memory 0개 / 2 Setup incomplete:** 실제 관찰한 의존성 경고입니다. 역할 부여나 실제 접근 거부 시험은 하지 않았습니다. `Resolve`로 권한을 확대하지 않습니다.

[자막 영상 05 · 01:58](../downloads/portal/index.html?clip=05-inspection-retention&t=118&lang=ko#05-inspection-retention)

</div>

<div class="practice-block" markdown="1">

**직접 해보기:** 아래 읽기 전용 단계를 수행하고 각 항목을 `확인/미노출/미검증`으로 표시합니다.

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | Azure portal의 전용 그룹 `Overview → Access control (IAM) → View my access`를 엽니다. | 내 실제 역할과 적용 scope입니다. | 역할 추가·Owner 확대를 하지 않습니다. |
| 2 | 내 Microsoft Foundry account/project의 `Identity`·권한 화면을 읽습니다. | 사용자 identity와 runtime managed identity를 구분합니다. | toggle·role assignment를 바꾸지 않습니다. |
| 3 | `Networking`의 현재 접근 상태를 읽습니다. | 승인된 public/private 경계입니다. | private endpoint·방화벽을 꺼서 우회하지 않습니다. |

### 2. 연결·도구·보호 정책·실행 기록을 나눠 읽기

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | Microsoft Foundry `Manage → Connected resources`를 엽니다. | 내 연결의 대상·인증 유형·범위입니다. | key·connection string 원문을 열거나 녹화하지 않습니다. |
| 2 | `Build → Agents → 내 agent`의 Tools·Guardrails를 읽습니다. | 실제 도구·필터·권한 의존성이 나옵니다. | Instructions만으로 tool authorization을 입증하지 않습니다. |
| 3 | L09의 실제 안전 결과와 L10의 traces 접근 상태를 비교합니다. | guardrail 관찰과 data-plane 허용/거부가 분리됩니다. | 설정 화면을 실제 차단 로그로 바꾸지 않습니다. |

<div class="screen-step" markdown="1">

**인증 유형: 폼 기본값과 저장된 연결을 구분**

![연결하지 않은 IQ 폼의 resource 선택과 API Key 기본 Auth Type.](../assets/portal/steps/iq-connect.png)

**1 대상 / 2 Auth Type:** 이 사진은 L11의 미연결 폼입니다. `API Key` 기본값이 내 저장 연결의 인증이나 키 사용 승인은 아닙니다. 실제 저장된 대상·인증을 따로 읽고 원문 key는 열지 않습니다. **3 새 자원 생성:** 누르지 않습니다.

[자막 영상 05 · 01:46](../downloads/portal/index.html?clip=05-inspection-retention&t=106&lang=ko#05-inspection-retention)

</div>

<div class="screen-step" markdown="1">

**연결된 도구: 실제 정책 agent에는 File search**

![현재 정책 agent에 저장된 모델과 File search 도구.](../assets/portal/steps/policy-final.png)

**1 모델 / 2 File search:** 저장된 실제 구성을 적습니다. File search 연결만으로 주문 도구·사용자별 문서 ACL·Memory가 구현된 것은 아닙니다. 취소한 MCP allowlist를 저장된 제한이라고 기록하지 않습니다.

[자막 영상 05 · 01:36](../downloads/portal/index.html?clip=05-inspection-retention&t=96&lang=ko#05-inspection-retention)

</div>

<div class="screen-step" markdown="1">

**보호 정책: 적용 대상이 어디인지 확인**

![DefaultV2의 실제 Applied to와 Model deployments 및 Agents 상세.](../assets/portal/steps/guardrail-targets.png)

**1 Applied to / 2 Model deployments / 3 Agents:** 내 대상의 실제 적용 범위를 읽습니다. 모델 보호가 적용돼도 문서·주문 API의 서버 권한 검사는 별개입니다. 정책은 변경하지 않습니다.

[자막 영상 03 · 03:41](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=221&lang=ko#03-retrieval-boundaries)

</div>

<div class="screen-step" markdown="1">

**실행 기록: 반환 정책은 확인됐지만 ACL 시험은 아님**

![실제 File search span의 Input + Output와 반환 정책 본문.](../assets/portal/steps/trace-input-output.png)

**1 Input + Output / 2 Content source:** 실제 반환된 문서까지 읽습니다. 이 한 요청의 합성 공용 정책 조회는 다른 사용자·tenant의 접근 거부나 cache 격리를 검증하지 않았습니다.

[자막 영상 03 · 04:18](../downloads/portal/index.html?clip=03-retrieval-boundaries&t=258&lang=ko#03-retrieval-boundaries)

</div>

### 3. Cache 결정표: 화면 관찰이 아닌 수동 판단

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | 아래 가상 cache 결정표를 채웁니다. | 사용자·tenant·문서 ACL 확인 위치가 보입니다. | 포털이 cache 구현을 검사했다고 주장하지 않습니다. |

| 가상 요청 | 안전한 결정 | 필요한 검증 |
| --- | --- | --- |
| 같은 tenant·사용자 A, 권한 있는 공용 합성 정책 | 재사용 후보 | 현재 권한·문서 버전·보존·key 범위 |
| 같은 tenant·사용자 B, A 전용 문서에 권한 없음 | 거부 | **cache hit 전에** B의 현재 ACL 검사 |
| 다른 tenant 또는 프로젝트 | 분리/거부 | tenant·project 경계, 공유 저장소 격리 |
| 권한 철회·문서 갱신 후 과거 cache | 폐기/재검증 | authorization·문서 버전 재확인 |

**한 가지 바꾸기:** 첫 행의 사용자만 A→B로 바꾸고 “같은 질문이므로 답을 재사용”해도 되는지 결정합니다. A의 문서 접근권한을 B가 상속하지 않는 이유를 설명합니다.

**결과 설명하기:** cache key에 tenant/project/user를 넣는 것만으로 충분하지 않으며, **매 요청의 현재 authorization·ACL 검사**가 필요하다고 설명합니다. 이 표는 로컬 코드 수정이나 실제 교차 사용자 보안 시험이 아닙니다.

</div>

## 성공 기준

실제 확인한 scope·역할·연결과 미검증 항목을 나눴습니다. 역할 확대·공개 전환 없이 읽기 전용으로 끝냈습니다. Cache 결정표를 실제 구현·보안 통과 결과로 주장하지 않았습니다.

## 막혔을 때

권한 미노출은 `미확인`으로 남기고 정확한 최소 작업·scope를 담당자에게 요청합니다. Azure Policy의 assignment가 보이는 것만으로 agent의 문서 ACL이 적용됐다고 판단하지 않습니다.

## 정리

민감한 identity 정보가 없는 점검표만 남깁니다. 사람·그룹·메일 목록이 녹화되었다면 해당 구간을 배포하지 않습니다. 권한/네트워크/정책 변경은 별도 승인 작업입니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 내 scope·identity·연결 점검표, cache 결정표와 실제 교차 사용자 격리 미검증.

**다음:** [L18 평가 gate·버전·배포 판단](#l22).

</div>
