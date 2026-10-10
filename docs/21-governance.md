> **완성할 결과:** 여러 agent를 운영할 때 identity·데이터·네트워크·정책·비용의 통제 책임을 한 장으로 설명합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 로컬 코드 수정 + 선택 설계 · Microsoft Azure 계정 없이 시작합니다.

**먼저 할 일:** 합성 캐시/권한 과제의 두 실패를 재현한 뒤, 사용자 → 에이전트 → 도구 → 데이터의 책임을 연결합니다.

**확인할 결과:** 허용·거절 조건, 네트워크 경로와 담당자 표를 만듭니다. 표 작성은 실제 권한 부여나 보안 검증이 아닙니다.

</div>

## 목표

**Foundry Control Plane의 화면이 보이는 것과 정책이 실제로 강제되는 것은 다릅니다.** Operate의 Overview/Assets/Compliance와 AI gateway in Foundry Agent Service 경험에는 Preview 범위가 있습니다.

## 개념과 실습 지도

**경험할 기능:** 권한 검사 순서를 고치고 사용자→도구→데이터의 책임을 그립니다.

**무엇이며 왜 중요한가요?** Identity는 호출 주체, RBAC는 역할 기반 권한, scope는 적용 범위입니다. 네트워크와 Gateway가 안전해도 A의 문서를 B에게 주는 캐시 문제까지 해결되지는 않습니다.

**어떻게 사용하나요?** 로컬 결함 과제를 고친 뒤 각 단계의 주체·허용 작업·거절 조건을 적습니다. 실제 권한이나 네트워크를 바꾸는 과제가 아닙니다.

**어디서 실행하나요?** 기본은 Codespaces의 Python과 설계표입니다. [인프라](../infra/main.bicep)·[역할 설정 코드](../scripts/runtime_roles.py)는 읽을 참고 자료이며 실행하지 않습니다.

## 준비

기본 과제는 Python 로컬 수정과 설계입니다. 자신의 **주체 → 작업 → scope → 거절 조건 → 확인·회수 방법**을 작성합니다. Microsoft Azure 계정 없이도 가능하지만 실제 권한 검증은 아닙니다. 실제 role assignment·gateway·private endpoint·정책 변경은 해당 권한과 변경 범위를 갖춘 뒤 별도 실행합니다.

### 먼저 경로 정하기

| 목표 | 따라갈 순서 | 남길 결과 |
| --- | --- | --- |
| 권한과 캐시의 관계 직접 확인 | 1단계 복사 → 실패 2건 → `exercise.py` 수정 → 같은 테스트 5개 통과 | 로컬 수정 전·후와 이유 |
| 조직 적용 설계 | 위 실습 → 2단계 주체표 → 4·5단계 Gateway/네트워크 경계 | 직접 작성한 설계표. Microsoft Azure 변경은 미실행 |
| 포털 읽기 권한도 있음 | 추가로 3단계의 **자기 소유 자산 1개** 관찰 | 조회 시각·필터·읽기 범위를 기록 |

편집기에서 `practice/governance/exercise.py`만 고칩니다. `test_exercise.py`·허용 사용자 목록·`data/exercises/` 원본은 그대로 둡니다. 폴더가 이미 있다면 다른 `--output` 경로를 정하고 검사 명령의 경로도 함께 바꿉니다.

## 실행

### 1. 직접 고치기: 캐시에 있어도 권한을 확인하는가?

<div class="practice-block" markdown="1">

**직접 해보기:** 아래 과제는 실습 환경의 합성 문자열만 사용합니다. A는 제한 견적을 볼 수 있고 B는 볼 수 없습니다. 공용 정책은 둘 다 볼 수 있습니다. Microsoft Azure 역할·실제 문서 ACL을 바꾸는 과제가 아닙니다.

```bash
python samples/prepare_practice.py governance --output practice/governance
python -m unittest discover -s practice/governance -p "test_exercise.py" -v
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `prepare_practice.py governance` | 동봉된 결함 예제를 새 `practice/governance` 폴더로 복사합니다. 기존 폴더는 덮어쓰지 않습니다. | 로컬 파일만 생성. 외부 접속·권한 변경 없음. |
| 2. `unittest discover` | 복사본의 다섯 사례로 접근 허용·거절·캐시·권한 회수를 확인합니다. | 처음에는 **5개 중 2개 실패**가 의도한 결과입니다. 저장소 전체 검사의 실패가 아닙니다. |

</div>

실패 이름은 `test_denied_user_after_cache`, `test_revocation_after_cache`입니다. `practice/governance/exercise.py`에서 **캐시 반환이 권한 확인보다 앞서는 순서**를 찾습니다. A가 읽은 뒤 B가 읽거나 A의 권한을 회수했을 때 어떤 줄이 검사를 건너뛰는지 설명하세요.

**직관적으로 따라가기:** A가 제한 견적을 읽어 캐시가 생깁니다 → B가 같은 문서를 요청합니다 → 잘못된 코드는 권한을 보기 전에 캐시를 돌려줍니다. 수정 뒤에는 캐시가 있어도 B를 거절해야 합니다. A의 권한을 회수한 경우에도 같은 원칙입니다. 캐시를 비워 우연히 통과시키는 것이 아니라 **매 요청의 현재 권한 확인**이 핵심입니다.

**한 가지 바꾸기:** 권한 검사를 캐시 조회보다 앞에 놓습니다. 테스트나 `grants`의 허용 사용자를 바꾸지 않습니다. 같은 검사 명령을 다시 실행해 다섯 사례 모두 통과하는지 확인합니다.

<details markdown="1">
<summary>수정 예와 해설 — 먼저 자신의 수정 결과를 확인한 뒤 펼치기</summary>

<!-- solution:governance -->
```python
DOCUMENTS = {
    "public-policy": "Contoso synthetic policy: drafts require human approval.",
    "restricted-quote": "Contoso synthetic restricted quote: training data only.",
}

def read_document(user: str, document_id: str, grants: dict[str, set[str]], cache: dict) -> str:
    if user not in grants[document_id]:
        raise PermissionError("Access denied")
    if document_id not in cache:
        cache[document_id] = DOCUMENTS[document_id]
    return cache[document_id]
```

캐시는 인증·권한 검사를 대체하지 않습니다. 이 예제는 매번 현재 권한표를 확인하므로 회수 후 캐시가 남아 있어도 거절합니다. 실제 서비스에는 인증된 사용자 연결, 원본 ACL, 캐시 격리·만료가 추가로 필요합니다.

</details>

**결과 설명하기:** `A 첫 읽기 / B의 같은 문서 읽기 / A 권한 회수 후 읽기 / 공용 정책 읽기`의 수정 전·후를 적습니다. 이어 아래 identity 표의 어느 계층이 이 검사를 집행해야 하는지 표시합니다. **로컬 테스트 통과를 Azure RBAC·네트워크·문서 ACL 검증으로 기록하지 않습니다.**

</div>

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 고칠 캐시 코드와 Azure RBAC의 차이 — 읽기용</summary>

<a id="l21-로컬-코드와-azure-포털-경계"></a>

#### 로컬 코드와 Microsoft Azure 포털 경계

이 연습의 `exercise.py`는 가짜 문서와 가짜 권한표만 사용합니다. 결함은 캐시 반환이 권한 검사보다 앞에 있는 순서입니다.

```python
def read_document(user, document_id, grants, cache):
    if document_id in cache:
        return cache[document_id]
    if user not in grants[document_id]:
        raise PermissionError("Access denied")
    cache[document_id] = DOCUMENTS[document_id]
    return cache[document_id]
```

| 이번 연습 | 무엇을 조작하는지 |
| --- | --- |
| `prepare_practice.py governance` | 결함 예제를 새 `practice/governance` 폴더로 복사 |
| `exercise.py` 수정 + `test_exercise.py` | 로컬 캐시/가짜 grant에서 B와 회수 후 A가 거절되는지 확인 |
| Azure portal / Azure RBAC | 이 테스트에서는 변경하거나 검증하지 않음 |
| `infra/main.bicep`, `runtime_roles.py` | 설계 참고 자료. Microsoft Azure에 적용하지 않음 |

L01에서는 자신의 실제 역할을 준비했고 여기서는 **애플리케이션의 캐시/문서 권한 검사**를 학습합니다. 둘은 다른 검사입니다. 실제 ACL 시험에는 허용된 테스트 identity·별도 합성 제한 문서·접근 로그가 필요하며 로컬 통과로 대신하지 않습니다.

</details>

### 2. identity 네 가지를 분리하기

**작성 예 — L12의 공용 정책 Hosted 경로를 기준으로 한 설계이며 실제 역할 부여 기록은 아닙니다.**

| Identity | 허용할 작업·범위 | 허용하지 않을 것 | 내가 확인할 근거 |
| --- | --- | --- | --- |
| 내 로그인 identity | 소유 프로젝트의 agent 변경·조회 | 다른 팀 agent 수정, 무관한 범위 권한 확대 | 자원 IAM과 내 요청 결과 |
| 프로젝트 managed identity | L07 OpenAPI처럼 이 ID를 쓰는 연결의 Search 읽기 | runtime 역할의 자동 상속 | 연결 인증 방식과 Search IAM |
| agent runtime identity | 지정 모델·소유 Search 읽기 | index 변경, 임의 데이터 접근, 주문·결제 | L12 runtime ID·scoped 역할·실제 호출 |
| 앱 사용자 identity | 허용된 agent·본인에게 허용된 근거 | agent 편집, 타인 문서·대화 조회 | 앱 인증·ACL·허용/거절 로그 |

L12의 직접 Search 호출과 L07 연결의 호출 주체는 같다고 가정하지 않습니다. **Manage의 연결 인증 방식 → 해당 identity의 role assignment와 scope → 대상 서비스** 순으로 읽습니다. 권한 목록은 허용 가능성을 보여 줄 뿐 호출 성공 증거가 아니며, 실제 검사는 별도 승인된 읽기 요청으로 확인합니다.

### 3. Foundry Control Plane에서 fleet 확인하기

**Operate → Assets**에서 자신이 만든 agent/model/tool을 찾습니다. **Manage**는 현재 프로젝트/리소스 설정, **Operate**는 자산·운영 상태 관점입니다. 여러 프로젝트의 자산이 보이더라도 권한 범위 밖의 데이터를 실습 자료로 쓰지 않습니다.

실행 상태·비용·경보·평가·정책 정보를 비교합니다. 외부 agent 등록은 관찰 범위를 늘리는 기능이며, 등록했다고 그 agent에 Microsoft Foundry runtime guardrail이 자동 적용되지 않습니다.

자기 소유 자산 한 개에 대해 **자산 이름·프로젝트·소유자·마지막 관찰 시각·정책 적용 대상**을 적습니다. 목록이 비면 “자산 없음”으로 확정하지 말고 필터·현재 테넌트·읽기 범위를 먼저 확인합니다. 알 수 없는 다른 팀 자산을 열어 실습 자료로 쓰지 않습니다.

### 4. AI Gateway 선택 과제

APIM 기반 gateway가 필요한 이유를 하나 정합니다: 토큰 한도, rate limit, 허용 backend, 관측, 라우팅 등.

| 정책 | 반드시 확인할 것 |
| --- | --- |
| rate/token limit | 사용자/agent/project 식별 기준과 초과 응답 |
| backend routing/fallback | 허용 모델·지역만 사용하는가 |
| caching | 사용자/권한별 데이터가 섞이지 않는가 |
| logging | prompt·비밀·PII가 로그에 노출되지 않는가 |
| tool/API 관리 | 원본 서비스 권한과 gateway 정책이 모두 있는가 |

**계획 예:** 격리된 합성 테스트 주체에 60초당 2회 제한을 적용한다고 가정하고, 세 번째 요청을 거절하는 검사를 설계합니다. 적을 항목은 식별 키, 정책 scope, 거절 상태(예: 429), counter/trace 확인 위치, 최대 3회·재시도 0회, 중단 담당자입니다. 실제 한도 설정과 전송은 별도 승인 후에만 수행합니다. 분산 counter·이미 소비된 요청 때문에 결과가 다르면 해당 증거부터 확인하며 통과할 때까지 보내지 않습니다.

**quota는 청구 한도가 아니고, 예산 알림도 hard stop이 아닙니다.** Microsoft Foundry gateway UI와 APIM 자체의 상태도 구분합니다. 도구·문서 권한을 gateway에만 맡기지 않습니다.

### 5. 네트워크 설계 과제

세 경로를 그립니다: **사용자 → Microsoft Foundry**, **Microsoft Foundry → 도구/데이터**, **도구/데이터 → 외부**.

```text
가상 사용자 A/B
  -> 앱의 사용자 인증·허용 검사
  -> Foundry agent endpoint              [inbound 경로]
  -> runtime identity로 Search 읽기      [데이터 egress]
  -> 공용 합성 정책 index

주문·결제 API / 임의 외부 사이트           [연결하지 않음]
```

이 그림은 **원하는 경계의 설계**이지 동봉 IaC가 private network를 구축했다는 뜻이 아닙니다. private 요건이 있다면 각 화살표에 DNS·연결 경로·호출 identity·허용 대상을 적습니다. 아래 기능을 무조건 모두 생성하는 과제가 아닙니다.

| 구성 | 해결하는 것 | 해결하지 않는 것 |
| --- | --- | --- |
| Private endpoint | Microsoft Foundry로 들어오는 private 연결 | 모든 tool egress 차단 |
| VNet/managed network 설정 | 지원되는 outbound 경로 | 미지원 도구를 자동 지원 |
| Private DNS | 올바른 주소 해석 | RBAC·앱 인증 |
| Firewall/egress policy | 허용 목적지 통제 | 데이터 자체의 사용자 ACL |

private Search/Storage 등에는 각각 필요한 private endpoint를 준비합니다. Microsoft Foundry private endpoint 하나가 모든 연결 자원을 private로 만드는 것은 아닙니다.

| 확인할 것 | 어떻게 판단하나요? | 실패하면 다음 행동 |
| --- | --- | --- |
| 승인된 실행 위치에서 endpoint DNS | 요구한 private 경로로 해석돼야 함 | DNS/VNet/VPN 경로 담당자에게 전달. public access를 열지 않음 |
| runtime의 정책 읽기 | 지정 Search만 읽고 변경은 허용하지 않도록 설계 | 개발자 로그인 권한과 runtime 역할을 분리해 대조 |
| 사용자 B의 제한 자료 요청 | 본문뿐 아니라 제목·URL·cache도 반환하지 않아야 함 | 원본 ACL → 검색 필터/사용자 token → cache 분리 확인 |

마지막 행은 **ACL 설계 과제**입니다. 현재 공용 Contoso index로 제한 문서 격리를 실증할 수 없습니다. 실제 시험은 허용된 기존 테스트 계정·별도 합성 제한 문서·접근 로그를 갖춘 경우에만 별도 수행합니다.

**대표적인 제약:** Memory store의 VNet 미지원, Routines의 CMK 미지원, 일부 browser/computer/image 도구의 network isolation 미지원, public web/Bing/SharePoint 도구의 public 통신. Hosted Agent private ACR은 **2026-06-25 이후 생성된 프로젝트** 등 문서의 조건을 재확인합니다.

### 6. 정책·암호화·정보 보호 확인하기

Azure Policy로 허용 모델·배포 유형·네트워크 조건을 검토합니다. CMK는 지원 자원의 저장 데이터 보호이고 runtime의 유출 방지나 모든 기능 지원을 의미하지 않습니다.

Defender·Purview·Entra 통합은 각 제품의 구성·권한·라이선스가 필요할 수 있습니다. 대시보드 존재를 조직 compliance 인증으로 제시하지 않습니다. 진단 로그와 content provenance, 사용자에게 AI 사용을 알리는 방식도 운영 문서에 포함합니다.

## 성공 기준

- 로컬 과제에서 처음의 두 실패를 재현하고, 권한을 넓히지 않은 수정으로 5개 테스트가 통과하는 이유를 설명합니다.
- 주체별 허용/금지 작업표, 세 네트워크 경로, 거절 사례 한 개, 감사·회수 담당자를 작성했습니다.
- **설계 예시 / 읽기 관찰 / 실제 허용·거절 시험**을 따로 표시했고, 실제 시험은 양쪽 증거가 있을 때만 완료로 기록합니다.

## 막혔을 때

| 증상 | 먼저 확인할 것 |
| --- | --- |
| 403 | RBAC 문제로 단정하지 않습니다. endpoint DNS, public network 차단, VNet 경로와 identity를 분리합니다. |
| 기능 미지원 | 권한을 넓힌다고 해결되지 않습니다. |

## 정리

내가 실제 변경한 역할·정책·gateway·연결이 있다면 소유 기록에 남기고 허용된 범위에서 회수합니다. 설계만 했다면 Microsoft Azure 변경 없음으로 기록합니다. 공유 네트워크·운영 정책은 삭제하지 않습니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 수정한 `practice/governance/exercise.py`, 같은 5개 테스트의 결과·수정 이유, 주체/작업/범위/거절·네트워크 설계표. 실제 Microsoft Azure 검증과 구분합니다.

**다음:** 릴리스·복구를 선택하면 [L18](#l22), 선택 실습을 마쳤다면 [L19](#l12).

</div>
