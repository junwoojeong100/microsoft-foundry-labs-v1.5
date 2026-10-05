> **이 모듈에서 만드는 것:** CI 결과, 에이전트 릴리스 명세, 롤백 판단표, 모델·비용 점검표. 실제 배포 없이도 작성할 수 있으며 실행 증거와 설계를 구분합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · 로컬 CI 실패→수정과 릴리스·복구 설계가 기본입니다.

**먼저 할 일:** 아래 빠른 경로를 고르고, 2단계의 합성 후보 선택 과제에서 세 실패를 재현합니다. 실제 배포·게시 없이 시작할 수 있습니다.

**확인할 결과:** CI 판독표·릴리스 명세·롤백 결정·비용 담당자를 기록합니다. 이 장 때문에 Hosted를 배포할 필요는 없습니다.

</div>

## 목표

**소스 검사가 통과한 것, Azure 배포가 된 것, 사용자가 써도 되는 것은 서로 다릅니다.** 세 판단을 분리하고 무엇이 실패하면 배포를 보류하거나 이전 버전으로 돌아갈지 정합니다.

**무엇을 더 배우나요?** 배포·운영 자동화가 필요할 때 실패한 후보의 승격을 막고 복구 대상을 정하는 연습입니다. 참여자 역할에 따른 분기가 아니라 기능 선택이며, 문서 빌드나 Teams 게시 자체가 기본 완주 조건은 아닙니다.

## 개념과 실습 지도

**경험할 기능:** 실패한 후보를 내보내지 않는 로컬 검사와 복구 계획을 만듭니다.

**무엇이며 왜 중요한가요?** CI는 변경을 자동 검사하고 CD는 검토한 변경을 배포합니다. Rollback은 이전 승인 버전으로 되돌리기입니다. 실행 완료만으로 품질까지 통과한 것은 아닙니다.

**어떻게 사용하나요?** 세 실패를 재현하고 후보 선택 조건을 고칩니다. 기존 결과로 릴리스 명세·롤백 판단표를 작성합니다. 새 Hosted 배포는 필요 없습니다.

**어디서 실행하나요?** 내 PC에서 진행합니다. **받은 소스의 `.github/workflows/`**에서 [로컬 검사](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/validate.yml)와 [별도 승인 실행](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/azure-validation.yml)의 조건을 읽습니다.

## 준비

L01의 환경과 저장소 소스가 필요합니다. **Search·Hosted·Optimizer가 없어도 기본 과제를 진행**할 수 있습니다. 실제 릴리스 명세를 작성할 때는 L06 또는 L12 결과를 사용하고, 없으면 아래 표를 설계로 작성합니다.

### 먼저 경로 정하기

| 목표 | 따라갈 순서 | 완료로 기록할 범위 |
| --- | --- | --- |
| CI가 잘못된 승격을 막는 이유 이해 | 1단계 workflow 읽기 → 2단계 실패 3건 → 함수 수정 → 같은 테스트 5개 통과 | 로컬 코드 실습 |
| 운영 전환 준비 | 위 과제 → 3단계 명세 → 4단계 복구 판단 → 5단계 담당자 | 릴리스 설계. 실제 배포·게시는 미실행 |
| 승인된 실제 게시 | 위 준비 + 4-1의 권한·protocol·시험 범위를 모두 충족 | 실제 수행한 버전 전환·게시·호출만 별도 기록 |

출발 파일은 `practice/delivery/exercise.py`, 수정하면 안 되는 파일은 같은 폴더의 `test_exercise.py`입니다. 폴더가 이미 있다면 지우거나 덮어쓰지 말고 다른 `--output` 경로를 정해 이후 테스트 경로도 똑같이 바꿉니다.

## 실행

### 1. 무엇이 자동 실행되는지 먼저 읽기

편집기로 `validate.yml`의 `on`, `jobs`, `needs`, `if`를 찾습니다. 아래 구분을 실제 YAML과 대조하세요.

| 확인할 것 | 어떻게 판단하나요? | 실패하면 다음 행동 |
| --- | --- | --- |
| `push` / `pull_request` → `offline`, `sdk` | 문서·데이터·코드와 SDK 계약 검사. Azure 배포 아님 | 실패 job의 **첫 오류와 실행 명령** 확인. 마지막 “failed” 문구만 읽지 않음 |
| `azure`의 `needs: [offline, sdk]` | 두 선행 검사를 통과해야 유료 경로에 진입 가능 | 실패/건너뜀을 배포 성공으로 표시하지 않음 |
| `workflow_dispatch`, `acknowledge_cost`, `repository_id` | 명시적 opt-in과 이 저장소 조건. fork에 같은 권한이 생기지 않음 | 기본 false 유지. 실습을 위해 repository ID나 승인 조건을 제거하지 않음 |
| `azure-validation.yml`의 `environment`, `id-token: write` | OIDC는 workflow identity 인증이며 별도의 Azure 역할·환경 승인이 필요 | branch/environment/tenant/project 불일치를 고치도록 담당자에게 전달. 장기 secret으로 임의 우회하지 않음 |

GitHub를 사용할 수 있으면 **Actions → 해당 실행 → job → 실패 step**을 열어 같은 항목을 찾습니다. 없으면 소스만 읽고 “workflow 실행 미확인”으로 남깁니다. 기본 과제는 새 push나 유료 workflow dispatch를 요구하지 않습니다.

<details class="optional-path" markdown="1">
<summary>참고: 저장소 전체 검사·문서 빌드 — 핵심 과제는 다음 2단계입니다</summary>

아래 저장소 전체 검사는 참고입니다. 먼저 이어지는 **실패→수정 실습**으로 CI가 무엇을 막는지 직접 확인할 수 있습니다. 기존 평가 기준이나 업무 코드를 일부러 망가뜨리지 않습니다.

첫 줄은 문서 의존성이 아직 없는 경우에만 필요합니다. L01의 기본 의존성은 이미 설치되어 있어야 합니다.

```bash
python -m pip install -r requirements-docs.txt
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `pip install -r requirements-docs.txt` | 현재 가상환경에 선언된 Markdown 생성 의존성을 준비합니다. 이미 있으면 생략합니다. | 패키지 다운로드·로컬 설치. Azure 호출 없음. |
| 2. `build_guide.py` | 두 언어의 원본·메타데이터로 HTML/Markdown을 생성합니다. | 로컬 파일 변경. 생성물을 손으로 수정하지 않습니다. |
| 3. `FOUNDRY_LAB_LANGUAGE=ko ... unittest ... -q` | 공유 테스트를 한국어 기본값과 별도의 영어 검사로 실행합니다. | 로컬 계약 검사이며 Azure나 모델 품질 검사가 아닙니다. |
| 4. `check_guide.py` | 20개 모듈과 5개 참고 절, 명령 해설, 링크, 그림 파일을 확인합니다. | 문서 검사 결과를 `results/documentation/`에 저장합니다. |

</div>

통과하면 **코드/문서 검사 통과**로만 기록합니다. import 오류는 가상환경과 requirements, 생성물 차이는 `docs/`·`content/` 원본, 업무 assertion 실패는 관련 함수·정책 계약부터 확인합니다. assertion이나 평가 기준을 낮춰 통과시키지 않습니다.

PDF·ZIP이 필요하면 README의 생성 경로를 이어 사용합니다. `downloads/`의 전달물과 루트 웹 진입점은 **에이전트 배포물과 별개**입니다. 문서 빌드는 이 장의 보조 과제이지 CD 성공 증거가 아닙니다.

</details>

### 2. 직접 고치기: 실행 완료만으로 후보를 내보내지 않기

<div class="practice-block" markdown="1">

**직접 해보기:** 다음은 가짜 버전 이름을 반환하는 순수 함수입니다. 실제 endpoint나 Active version을 바꾸지 않습니다.

```bash
python samples/prepare_practice.py delivery --output practice/delivery
python -m unittest discover -s practice/delivery -p "test_exercise.py" -v
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `prepare_practice.py delivery` | 결함 함수·테스트·선택형 workflow 템플릿을 새 폴더에 복사합니다. | 로컬 파일만 생성. GitHub push나 Azure 배포 없음. |
| 2. `unittest discover` | 정상 후보·실행 실패·품질 실패·critical 실패·행 누락을 구분합니다. | 처음에는 **5개 중 3개 실패**가 정상입니다. 이 실패를 숨기지 않습니다. |

</div>

`practice/delivery/exercise.py`는 `status=completed`만 보고 `candidate-2`를 선택합니다. 하지만 실행은 끝났어도 품질 실패·안전 실패·누락이 있으면 `approved-1`을 유지해야 합니다.

**한 가지 바꾸기:** 후보 선택 조건을 네 조건의 AND로 고칩니다. 완료 상태, `quality_passed is True`, critical 실패 0, 누락 0입니다. 테스트·원본 릴리스 게이트는 바꾸지 않습니다. 같은 검사로 5개 모두 통과하는지 확인합니다.

<details markdown="1">
<summary>수정 예 — 실제 운영 게이트 전체가 아닌 로컬 결정 연습</summary>

<!-- solution:delivery -->
```python
def choose_version(previous: str, candidate: str, checks: dict) -> str:
    if (
        checks["status"] == "completed"
        and checks["quality_passed"] is True
        and checks["critical_failures"] == 0
        and checks["missing_rows"] == 0
    ):
        return candidate
    return previous
```

</details>

**결과 설명하기:** 실패한 세 테스트가 어떤 잘못된 승격을 막았는지 적고, `이전 버전 / 후보 / 실패 근거 / 유지할 버전` 표를 완성합니다. 이 함수에는 실제 배포·상태 이관이 없으므로 원격 롤백 완료라고 쓰지 않습니다.

**선택: GitHub에서 같은 실패→수정 보기.** 승인된 개인 실습 저장소의 새 브랜치에서만 진행합니다. 복사된 `workflow.yml`을 `.github/workflows/contoso-practice.yml`로 두고 `practice/delivery` 코드·테스트를 함께 관리합니다. 초기 결함 상태로 Actions의 **Contoso local delivery practice → Run workflow**를 실행하면 실패하고, `exercise.py`만 고친 커밋으로 다시 실행하면 통과해야 합니다. 템플릿은 수동 실행·읽기 권한·Python 검사만 사용하며 Azure 로그인·secret·배포 단계가 없습니다. 이 저장소의 기존 `validate.yml`을 대체하거나 `acknowledge_cost`를 켜지 않습니다.

</div>

### 3. 에이전트 릴리스 명세 작성하기

아래는 **Contoso 작성 예시**입니다. 실제 식별자/결과가 없는 칸에는 “미실행”을 쓰며 과거 결과를 현재 후보의 증거로 복사하지 않습니다.

| 명세 항목 | 무엇을 연결하나요? | 비어 있거나 다르면 |
| --- | --- | --- |
| 소스 | 자신의 commit, 변경 파일, 지침 v2의 실제 해시 | 검증에 사용한 소스와 후보를 구분할 수 없으므로 승격 보류 |
| 실행 대상 | 언어·프로젝트, 모델 ID/버전/배포 이름 | 같은 이름의 배포라도 모델 버전이 다르면 별도 후보 |
| agent | name, 서비스 발급 숫자 version, Prompt/Hosted와 protocol | 지침 v2를 서비스 version 2라고 가정하지 않음 |
| 데이터·도구 | 정책·schema·의존성 hash, 연결 대상 | 검색/함수 변경을 프롬프트 변경에 숨기지 않음 |
| 근거 | 같은 대상의 response/trace, 실제 도구 결과, 적용한 평가와 실패/누락 | L08의 도구 없는 12문항 비교만으로 통합 업무 출시 승인 불가 |
| 복구 | 이전 승인 버전·설정 묶음, 전환 담당자, 데이터 호환 여부 | 돌아갈 대상이나 상태 호환성이 없으면 배포 보류 |

L06의 기본 구매 과제라면 **재고 8개·단가 145만 원·총액 290만 원·두 승인 역할·미주문**을 실제 도구/근거와 연결합니다. L12 Hosted는 같은 버전의 package/runtime contract와 응답·도구·인용도 대조합니다.

**게시·버전 관리가 CI/CD에 포함되는 이유:** 배포는 새 실행 버전을 만드는 일, 승격은 검증된 버전을 사용자에게 선택해 주는 일, 게시는 Teams 같은 사용자 채널에 노출하는 일입니다. 롤백은 그 선택을 이전 승인 버전으로 되돌립니다.

| 혼동하기 쉬운 값 | 무엇의 버전인가요? | 확인할 곳 |
| --- | --- | --- |
| `agent-v2.txt` | 저장소 지침 파일 | 실제 파일과 해시 |
| 서비스가 발급한 숫자 agent version | 실행할 에이전트 정의·코드 | agent Details / L12의 `show` |
| **Active version** | stable endpoint가 사용자에게 제공할 실행 버전 | Details → Agent configuration |
| **Publish version** (예: `1.0.0`) | Teams/M365 앱 패키지 metadata | 게시 대화상자·앱 `manifest.json` |

버전 번호가 같아 보인다고 서로 같은 뜻은 아닙니다. active version만 바꾸면 stable endpoint URL은 유지되며, 앱 이름·설명 등 표시 metadata 변경과는 별도입니다.

### 4. 실패 가정으로 롤백 연습하기

**설명용 합성 상황:** 기존 승인 버전이 있고, 후보가 구매 초안을 “주문 완료”로 답했다고 가정합니다. 아래는 실제 배포 기록이 아닙니다.

| 순서 | 결정·행동 | 확인할 증거 |
| --- | --- | --- |
| 발견 | 후보 승격 중단; 제한 시험 중이었다면 확대 중지 | 실패 입력·응답·후보 version·실제 도구 기록 |
| 원인 분리 | 함수 결과는 미주문인데 답만 잘못됐다면 답변 합성/지침부터 조사 | 함수 JSON과 최종 응답의 차이 |
| 복구 준비 | 이전 승인 agent version과 모델·연결·설정을 한 묶음으로 선택 | 이전 버전의 존재와 현재 데이터/schema 호환성 |
| 승인된 복구 | 아래 Active version 또는 해당 Hosted 소비자의 **버전 바인딩**을 이전 대상으로 전환 | 같은 endpoint 이름만 보지 말고 실제 호출 버전 확인 |
| 복구 확인 | 승인된 범위의 동일 구매 질문으로 근거·도구·미주문 확인 | 새 실행의 response/trace와 결과. 예전 성공 로그로 대체 불가 |

기본 과제에서는 “어디를 되돌릴 것인가”까지만 작성합니다. 실제 전환·재호출은 별도 승인 대상입니다. 데이터 이관이 호환되지 않으면 agent 버전만 되돌려도 복구되지 않습니다. 실패 원본과 기존 버전을 지우지 않습니다.

### 4-1. 선택: 승인된 버전 전환과 Teams 게시

**기본 과제는 위의 설계에서 끝납니다.** 다음 표의 조건이 준비되지 않았다면 게시 버튼을 누르지 않고 “설계 완료 / 게시 미실행”으로 기록합니다.

| 준비할 것 | 값·조건을 확인할 곳 |
| --- | --- |
| 게시할 agent와 검증한 숫자 version | 자신의 프로젝트 → Build → Agents → 대상 Details. L05의 File search Prompt Agent는 정책 안내 범위로 사용 가능 |
| 서버에서 실행되는 도구·지원 protocol | L06의 로컬 함수는 원격 사용자 요청을 처리하지 않음. L12의 기본 Invocations 배포만으로 Teams의 `activity` 경로까지 검증됐다고 가정하지 않음 |
| 게시와 자원 생성 권한 | 프로젝트의 실제 publish permission과 Bot Service `botServices/write`, `channels/write`. 단일 역할 이름으로 모두 충족한다고 가정하지 않음 |
| 사용자·데이터 처리 승인 | 시험 사용자·게시 범위·M365/Teams로 흐르는 metadata와 응답·비용을 조직 담당자와 확인 |
| 복구 대상 | 이전 승인 버전과 설정. 없으면 임의 버전을 승인된 것으로 만들지 말고 운영 출시 보류 |

<details class="optional-path" markdown="1">
<summary>실제 변경 승인과 위 조건이 모두 있는 경우에만: 포털 단계</summary>

1. 자신의 agent **Details → Agent configuration → Active version → Edit**에서 검증한 **특정 버전**을 선택합니다. `Always use latest`는 새 버전이 자동 노출될 수 있으므로 교육용 기본 선택으로 쓰지 않습니다. 변경 전 버전·endpoint와 변경 후 선택값을 기록합니다.
2. **Publish → Teams and Microsoft Copilot**을 엽니다. 생성되거나 재사용될 Bot Service의 범위를 확인하고, Name·Publish version·설명·Developer를 작성합니다. 표시 정보에는 비밀을 넣지 않습니다.
3. **Next: Publish options → Direct publish → Just you**를 선택합니다. 최종 **Publish**는 별도 허용된 실제 게시입니다. **People in your organization**은 추가 조직 권한·배포 승인이 필요한 범위이며 실습을 위해 확대하지 않습니다.
4. 내 계정으로 **정책 질문 1건**, 재시도 0회로 결과를 확인합니다. 다른 사용자에 대한 접근 시험은 허용된 기존 테스트 identity가 있을 때만 별도 1건 수행합니다. 새 계정을 만들거나 계정 정보·권한을 임의로 바꾸지 않습니다. 부정 접근 시험을 하지 않았다면 미실행으로 기록합니다.
5. 응답의 정책 인용·실제 실행 버전을 확인합니다. 잘못된 후보라면 승격을 멈추고, **별도 복구 승인 후** 이전 승인 버전으로 전환합니다. endpoint 이름이 같다는 이유로 복구 성공을 판정하지 않습니다.

L05 정책 agent를 게시했다면 재고 조회·구매 초안까지 제공한다고 설명하지 않습니다. 구매 에이전트 전체를 게시하려면 서버에서 실행되는 업무 도구와 지원 protocol을 별도로 준비해야 합니다.

private 프로젝트는 일반 포털 게시 경로가 지원되지 않을 수 있습니다. public access를 켜지 말고 공식 private-network 게시 조건을 확인합니다. 앱이 안 보이면 내 게시 범위·조직 정책을, 응답하지 않으면 채널·인증·active version·서버 도구를 확인합니다.

</details>

### 5. 모델 수명주기와 비용 대응하기

![운영 모니터 화면. 요청·오류·사용량과 실제 품질 판정을 구분합니다.](../assets/portal/07-monitor.png)

| 신호·확인할 것 | 판단 | 다음 행동 |
| --- | --- | --- |
| L02 모델 배포의 현재 버전·자동 업데이트 정책·종료 예정일 | 배포 이름이 같아도 동작 조건은 바뀔 수 있음 | 담당자와 종료 전 비교 일정을 정하고, 기존 서비스 버전/문맥/기준을 기록 |
| 대체 모델 후보 | Responses·도구·출력 schema·리전·처리 위치가 모두 맞아야 함 | 별도 승인 후 같은 dev 입력으로 비교. 기존 holdout을 임의 재사용하거나 게이트를 완화하지 않음 |
| 429·지연 증가 | quota/동시성/입출력 토큰과 장애를 구분 | 호출을 줄이고 제한된 복구 계획 수립. 승인되지 않은 모델/리전으로 fallback 금지 |
| 요청이 없는데 비용 증가 | Search·저장소·로그·Hosted 세션의 비용 원인 확인 | L19의 자원별 중지/보존 담당자와 재확인 시점 기록. 빈 비용 행을 0으로 해석하지 않음 |

복구 설계에는 **RTO(서비스 복구 목표 시간)**와 **RPO(허용 가능한 데이터 손실 구간)**도 적습니다. 예를 들어 “읽기 전용 정책 안내를 30분 안에 복구, 승인 기록 손실 허용 없음”은 **요구사항 예시**이지 실측 보장이나 현재 키트의 기능이 아닙니다. 담당자·복구 경로·연습 결과가 없으면 달성했다고 표시하지 않습니다.

#### 로컬 승격 코드와 포털 Publish의 차이

`practice/delivery/exercise.py`의 `choose_version()`은 **로컬 후보 선택 함수**입니다. 위의 수정 예처럼 네 조건이 모두 참일 때만 candidate를 반환합니다. 이 함수는 Foundry agent version을 바꾸거나 Publish를 실행하지 않습니다.

| 실습에서 보는 것 | 실제로 하는 일 |
| --- | --- |
| `choose_version(previous, candidate, checks)` | 로컬 fixture에서 이전 버전 유지/후보 선택만 반환 |
| `test_exercise.py` | 완료·quality·critical failures·missing rows 조합을 로컬에서 확인 |
| Foundry Portal의 version/Publish | 정확한 숫자 agent version을 선택·게시하는 별도 승인 운영 작업 |
| `azure-validation.yml` | 별도 manual 승인 경로. 로컬 fixture 테스트가 Azure workflow를 실행하지 않음 |

따라서 로컬 테스트 통과와 Portal의 실제 Publish는 서로 다른 결과 기록입니다. 기본 과제는 첫 두 줄만 실행하고, 실제 버전 전환·게시를 완료한 것으로 쓰지 않습니다.

## 성공 기준

로컬 실패 3건을 재현하고 함수만 고쳐 5개 테스트를 통과시켰으며, GitHub 경로를 선택했다면 서로 다른 커밋의 실패·성공 실행을 구분합니다.
**CI 판독표, 릴리스 명세, 실패 시 롤백 결정, 모델/비용 재확인 담당자**가 있습니다. 로컬 통과·설계 완료·Azure 미실행을 구분하고, 같은 후보의 품질 근거가 없으면 승격 보류라고 판단할 수 있습니다.
게시를 선택했다면 agent 실행 버전과 앱 Publish version, 대상 사용자·호출 결과를 구분해 남깁니다. 게시 성공만으로 업무 출시 승인이나 전체 권한 검증 완료를 주장하지 않습니다.

## 막혔을 때

`azure`가 skipped라면 먼저 opt-in 조건을 읽습니다. 기본 push에서 건너뛴 것은 오류가 아닙니다. workflow 성공인데 응답이 틀렸다면 어떤 검사가 실제로 실행됐는지 확인합니다. 배포/롤백 오류는 agent version·protocol·runtime identity·모델/연결을 순서대로 대조하며 무조건 재배포하지 않습니다.

## 정리

개인 설정·원시 응답·receipt는 패키지에 넣지 않습니다. 작성한 CI 판독표·릴리스 명세·복구 판단표를 함께 보관합니다. 실제 유료 실행·권한 변경·Azure 삭제는 각각 별도 승인이 필요하며, 남은 자원과 비용은 L19에서 확인합니다.
