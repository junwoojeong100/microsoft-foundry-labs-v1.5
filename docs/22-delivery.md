## 목표

포털의 실제 평가·agent version·공유 범위를 묶어 배포 판단표를 만듭니다. 기본 경로에서는 **Publish·Active version 변경·외부 채널 배포를 하지 않습니다.**

<div class="lab-brief" markdown="1">

**진행 방식:** 읽기 전용 배포 점검과 gate 실패 결정 실습. CI 실행·SDK 배포·Hosted 선행 설치가 없습니다.

**먼저 할 일:** L08의 실제 run과 평가 대상 version을 찾습니다.

**확인할 결과:** 평가 대상/후보 version 일치, gate·안전·보존·복구 증거와 보류 사유.

</div>

## 개념과 실습 지도

**경험할 기능:** Evaluation 결과·Versions·공유/게시 경계 관찰.

**무엇이며 왜 중요한가요?** 잘 나온 Chat 하나는 release gate가 아닙니다. 평가한 version과 게시할 version이 다르면 결과를 그대로 적용할 수 없습니다.

**어떻게 사용하나요?** 실행 결과·대상·권한·복구 계획을 한 표에 모아 `보류/별도 승인 필요`를 결정합니다.

**어디서 실행하나요?** Microsoft Foundry의 Evaluations·Agents Details/Versions·게시 정보. 외부 게시 버튼은 누르지 않습니다.

## 준비

L08의 고정 12문항 v1/v2 결과를 사용합니다. 도구 없는 Prompt Agent 비교는 L12 Hosted 배포가 필요 없습니다. 기존 SDK 수집 결과는 별도 과거 증거입니다. 새 포털 run과 합쳐 새 SDK 검증으로 표시하지 않습니다.

## 실행

### 1. 기존 run의 대상·분모·전체 행 확인

새 평가를 만들거나 다시 제출하지 않습니다. 아래는 `contoso-compare-v2`의 실제 run입니다. 이름의 `v2`는 지시문 변형 이름이며 저장된 숫자 version `2`와 구분합니다.

<div class="practice-block" markdown="1">

**직접 해보기:** 아래 포털 관찰을 수행하고 점검표에 실제 값 또는 `미검증`을 적습니다.

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Evaluations → L08 실제 run`을 엽니다. | dataset 12행·대상 agent/version·모델·상태입니다. | Partial/Failed·누락·중복·오류를 제외해 성공률을 만들지 않습니다. |
| 2 | 전체 12행의 checklist와 안전/access 실패를 읽습니다. | 품질 ≥90%, 안전/access 실패 0 기준은 그대로입니다. | gate를 낮추거나 질문·요구사항을 사후 수정하지 않습니다. |

<div class="screen-step" markdown="1">

**Run details: 실제 평가 대상 링크 읽기**

![실제 v2 run의 Agent ID contoso-compare-v2:2와 Download results.](../assets/portal/steps/eval-run-target.png)

**1 Agent ID:** `contoso-compare-v2:2`의 마지막 숫자를 후보와 대조합니다. **2 Download results:** 누락·오류·null을 포함한 원본을 읽습니다. `Make recurring`·`Delete`는 누르지 않습니다.

[자막 영상 04 · 04:06](../downloads/portal/index.html?clip=04-native-evaluation&t=246&lang=ko#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**실제 보류 예시: 100%라도 분모가 11/11**

![실제 v2 평가의 Completed와 Relevance 100퍼센트 11/11.](../assets/portal/steps/eval-v2-result.png)

**1 Completed / 2 Relevance:** 상태와 백분율만으로 통과하지 않습니다. **3 Download results:** 누락된 judge의 오류·null을 포함해 읽습니다. 이번 비교는 미완료이며 게시·활성 전환·rollback은 미실행입니다.

[자막 영상 04 · 04:06](../downloads/portal/index.html?clip=04-native-evaluation&t=246&lang=ko#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**상세 행: 현재 페이지와 전체 데이터 수를 구분**

![실제 Detailed metrics result 마지막 페이지의 Index 10과 11 및 query.](../assets/portal/steps/eval-detail-rows.png)

**1 Index / 2 query:** 0부터 센 `10`·`11`은 마지막 두 행입니다. 이 페이지만 보고 전체가 두 문항이라고 적지 않습니다. 전체 12행과 evaluator별 오류를 내보낸 원본까지 대조합니다. 사진에는 오류 상세가 표시되지 않습니다.

[자막 영상 04 · 04:15](../downloads/portal/index.html?clip=04-native-evaluation&t=255&lang=ko#04-native-evaluation)

</div>

### 2. 같은 후보의 저장 설정과 게시 경계 읽기

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Build → Agents → 후보 → Versions/Details`를 엽니다. | 평가 대상과 후보의 model·Instructions·tools·version이 일치합니다. | 불일치는 재평가 필요/배포 보류입니다. |
| 2 | 게시 UI가 있으면 `Publish version`·`Active version`·audience 정보를 **읽기만** 합니다. | 게시와 활성 대상 전환이 별개임을 확인합니다. | 버튼을 누르거나 새 audience·권한을 만들지 않습니다. |
| 3 | 현재 sharing이 `Just you` 등 무엇인지 기록합니다. | 내 Chat 동작은 Teams·업무 채널 배포 증거가 아닙니다. | 채널 권한·consent를 추가하지 않습니다. |

<div class="screen-step" markdown="1">

**후보 설정: 같은 v2 agent의 모델·도구·숫자 version**

![실제 contoso-compare-v2의 Version 2, contoso-chat과 빈 Tools 영역.](../assets/portal/steps/eval-v2-candidate.png)

**1 Version / 2 모델 / 3 Tools:** 위 run의 정확한 후보인지 확인합니다. 화면에 일부만 보이는 Instructions는 전체 원문과 대조합니다. 상단 `Publish`는 누르지 않습니다. 이 장면에는 Active version·공유 audience가 없으므로 해당 값은 미확인입니다.

[자막 영상 04 · 00:53](../downloads/portal/index.html?clip=04-native-evaluation&t=53&lang=ko#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**목록 대조: v1과 v2의 숫자 버전은 모두 2**

![비교 agent v1과 v2의 실제 Version 2와 Prompt Type.](../assets/portal/steps/agents-type-list.png)

**1 Version / 2 Type:** 이름이 다른 두 후보를 혼동하지 않습니다. **3 New agent:** 이 장은 기존 대상만 읽으므로 새로 만들지 않습니다. 목록의 Running은 게시·업무 채널 배포의 증거가 아닙니다.

[자막 영상 05 · 02:23](../downloads/portal/index.html?clip=05-inspection-retention&t=143&lang=ko#05-inspection-retention)

</div>

### 3. 증거를 모아 보류 판단

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | L10 traces·L17 경계 점검·L19 비용/보존을 연결합니다. | 실제로 확보한 증거만 묶입니다. | 없는 item CRUD·ACL·HITL·실주문을 완료로 적지 않습니다. |
| 2 | 아래 한 가지 실패 조건으로 배포 판단을 해봅니다. | 기준 미달이면 보류합니다. | UI 평균 점수로 안전 실패를 상쇄하지 않습니다. |

| 점검 | 필요한 증거 | 이번 결과 |
| --- | --- | --- |
| 대상 고정 | 평가와 후보의 정확한 version·model·tools | 실제 값/미검증 |
| 품질·안전 | 품질 ≥90%, 안전/access 실패 0, 누락/오류 보존 | 실제 값/미검증 |
| 평가 한계 | 고정 12문항, **holdout 없음**, 행동 요구사항·수동 review | 학습 비교이며 production release 증명 아님 |
| 실행 경계 | 도구 호출·실제 인용·draft 저장·인간 승인별 증거 | 수행한 것만 |
| 비용·자원 | 전용 scope·요청 상한·잔여 자원·보존 책임 | 실제 값/미검증 |
| 복구 | 이전 실제 version·되돌릴 대상·RTO/RPO·담당자 | 계획/실제 복구 시험을 구분 |

**한 가지 바꾸기:** “안전/access 실패 1개”라는 **가상의 판단 조건**을 적용합니다. 실제 run 결과는 수정하지 않습니다. 평균 품질이 100%라도 gate 실패이므로 게시를 보류합니다.

**결과 설명하기:** `Publish version` 저장, `Active version` 전환, 호출자가 실제 사용한 version은 서로 다릅니다. 버전을 읽은 것만으로 배포·rollback·RTO/RPO 시험을 통과했다고 말할 수 없습니다.

</div>

### 이번 경로 밖의 delivery

GitHub Actions·OIDC·CI/CD는 참고입니다. 이 장에서는 workflow 실행·권한 부여·브랜치 병합·게시를 하지 않습니다. 기존 자동화의 `repository_id`, 비용 동의 `acknowledge_cost`, ownership receipt·요청 상한을 지우거나 우회하지 않습니다.

기존 [로컬 검증 workflow](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/validate.yml)와 [Microsoft Azure 검증 workflow](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/azure-validation.yml)는 **읽기 전용 참고**입니다. 열람을 실행·배포 증거로 기록하지 않습니다.

Teams/Microsoft 365 채널은 별도 게시 권한·동의·`botServices/write`·`channels/write`와 실제 사용 경로 검증이 필요할 수 있습니다. Chat이 성공했다는 이유로 해당 배포를 했다고 쓰지 않습니다.

## 성공 기준

평가 대상과 후보 version을 확인하고 미검증·불일치·안전 실패에 보류 판단을 했습니다. 고정 평가·수동 checklist를 production 또는 과거 SDK gate와 같다고 주장하지 않았습니다.

## 막혔을 때

version ID가 보이지 않으면 후보 고정을 입증할 수 없다고 남깁니다. 실제 run이 없으면 release 점수는 만들지 않습니다. 기존의 통과 결과를 복사하거나 gate를 낮추지 않습니다.

## 정리

읽기 전용으로 끝냈습니다. 실제 게시·활성 전환·rollback은 별도 범위·권한·비용·복구 승인이 필요합니다. 새 GitHub release·Pages 게시·main 병합도 이 실습에 포함되지 않습니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 실제 version·run 연결과 gate/미검증/복구 계획, 게시·전환·rollback 미실행.

**다음:** [L19 비용·보존·승인된 정리](#l12).

</div>
