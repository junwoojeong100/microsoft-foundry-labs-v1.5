## 목표

대화 문맥과 서버 Memory를 구분합니다. 실제 `Memory stores`·생성 폼·runtime 권한 경고를 관찰하고 **Create 없이 취소**합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 기본은 관찰. 이번 녹화는 store 0개·Memory 쓰기/회상 0회입니다. 별도 승인된 기존 연결의 조건부 Chat 비교도 CRUD·격리·삭제 검증은 아닙니다.

**먼저 할 일:** `Build → Memory`의 `Memory stores (0)`와 `Setup incomplete`를 읽습니다.

**확인할 결과:** 확인 가능한 설정, 새 대화의 실제 결과, 포털에서 입증하지 못한 항목.

</div>

## 개념과 실습 지도

**경험할 기능:** Memory Preview의 연결·보존·대화 간 회상 구분.

**무엇이며 왜 중요한가요?** Conversation 안의 문맥은 장기 Memory와 다릅니다. 자연어로 “기억했다”고 답한 것만으로 저장 성공·사용자 격리를 증명할 수 없습니다.

**어떻게 사용하나요?** 포털에 노출된 store·도구·scope·TTL을 읽고, 별도 승인된 경우만 합성 선호를 새 Chat에서 비교합니다.

**어디서 실행하나요?** Microsoft Foundry의 내 프로젝트 → Build → Memory와 내 agent Details/Tools. 조건부 비교만 Chat을 사용하며 코드·직접 API는 사용하지 않습니다.

## 준비

서버 Memory는 chat·embedding 배포와 **프로젝트 managed identity**의 권한이 필요합니다. 녹화에서는 `Setup incomplete`가 프로젝트의 **Foundry User** 역할을 요구했고, 역할 부여에는 Owner 또는 User Access Administrator가 필요하다고 안내했습니다. 개인의 Contributor 권한과 runtime identity의 권한은 다릅니다. **Resolve를 누르거나 역할을 추가하지 않습니다.**

L00의 수동 모델 2개 범위에는 새 embedding·Memory 생성이 없습니다. 목록에 이미 보인 자동 `text-embedding-ada-002` 배포는 새로 만든 Memory나 회상 성공의 증거가 아닙니다. 실제 생성 폼과 TTL 필드는 아래처럼 관찰할 수 있지만 저장·item CRUD·격리 검증은 별개입니다.

## 실행

### 1. 개수와 runtime 권한 경고 읽기

<div class="screen-step" markdown="1">

**Memory 목록: 0개와 runtime 경고를 따로 읽기**

![Memory stores 0개와 프로젝트 managed identity 권한의 Setup incomplete 경고.](../assets/portal/steps/memory-warning.png)

**1 개수:** `Memory stores (0)`. **2 경고:** 내 로그인 권한과 프로젝트 runtime 권한은 다릅니다. 이 경고를 보고 `Resolve`나 역할 부여를 누르지 않습니다.

[자막 영상 05 · 01:58](../downloads/portal/index.html?clip=05-inspection-retention&t=118&lang=ko#05-inspection-retention)

</div>

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Build → Memory`를 엽니다. | Preview의 `Memory stores` 목록과 실제 개수입니다. 녹화는 `Memory stores (0)`였습니다. | 메뉴가 없으면 미지원으로 기록하고 CLI로 우회하지 않습니다. |
| 2 | `Setup incomplete`가 있으면 runtime identity·요구 역할을 읽습니다. | 프로젝트 managed identity의 Foundry User 요구입니다. | `Resolve`·역할 부여·개인 token 우회를 하지 않습니다. |

### 2. 기본 모델과 보존 폼 관찰

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Create memory store`를 열되 제출하지 않습니다. | Name·Chat completions model·Embedding model·Description입니다. | 모델 선택을 새 배포 승인으로 해석하지 않습니다. |
| 2 | 기존 모델만 읽고 `Advanced settings`를 펼칩니다. | Chat Summary·Procedural Memory·User Profile의 Enabled 설정, User profile details, **Default time-to-live (seconds)**입니다. | 실제 표시가 다르면 그 값을 적습니다. 임의 TTL·설정을 저장하지 않습니다. |

<div class="screen-step" markdown="1">

**기본 폼: Chat과 embedding은 서로 다른 의존성**

![Memory 생성 폼의 Chat completions model, Embedding model과 Cancel.](../assets/portal/steps/memory-form.png)

**1 Chat 모델 / 2 Embedding 모델:** 녹화에는 기존 `contoso-chat`과 `text-embedding-ada-002`가 보입니다. 이름이 보여도 store가 생긴 것은 아닙니다. Name·Description도 읽기만 합니다. **3 Cancel:** 생성 버튼이 아니라 취소로 마칩니다.

[자막 영상 05 · 02:05](../downloads/portal/index.html?clip=05-inspection-retention&t=125&lang=ko#05-inspection-retention)

</div>

<div class="screen-step" markdown="1">

**Advanced settings: 보존 필드를 읽은 뒤 Cancel**

![Memory 생성 폼의 Advanced settings, Default time-to-live seconds와 Cancel.](../assets/portal/steps/memory-ttl.png)

**1 펼치기:** 기본 활성 기능과 User profile도 읽습니다. **2 TTL:** 녹화의 입력 전 값은 `0`입니다. 저장·만료·삭제 성공으로 해석하지 않습니다. **3 Cancel:** Create 없이 나갑니다. 쓰기·회상은 0회입니다.

[자막 영상 05 · 02:10.4](../downloads/portal/index.html?clip=05-inspection-retention&t=130.4&lang=ko#05-inspection-retention)

</div>

### 3. 취소 후 agent 연결 확인

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Create`를 누르지 말고 `Cancel`을 누릅니다. | store 0개·쓰기/회상 0회가 유지됩니다. | 폼 관찰을 Memory 생성·TTL 만료 성공으로 쓰지 않습니다. |
| 2 | `Build → Agents → 내 agent → Details/Tools`의 연결을 읽습니다. | 현재 정책 agent는 File search만 있으며 Memory는 없습니다. | File search·같은 대화의 문맥을 Memory로 부르지 않습니다. |

<div class="screen-step" markdown="1">

**agent로 돌아오기: File search와 Memory를 구분**

![실제 정책 agent에 연결된 File search와 별도의 Memory 영역.](../assets/portal/steps/policy-final.png)

**1 모델 / 2 File search:** 저장된 정책 검색 구성입니다. 아래 `Memory` 영역과 별개이며 store 생성·연결·회상의 증거가 아닙니다. 관찰을 마치면 기본 경로는 여기서 끝납니다.

[자막 영상 05 · 01:36](../downloads/portal/index.html?clip=05-inspection-retention&t=96&lang=ko#05-inspection-retention)

</div>

### 4. 별도 승인 후: 같은 사용자 새 Chat 비교 — 미실행

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | 별도 승인된 기존 store·연결·허용 쓰기·시험 UI가 모두 있을 때만 아래 비교를 합니다. | 합성 데이터, 최대 4회 전송입니다. | 하나라도 없으면 Chat 비교는 미실행입니다. |
| 2 | 설정 관찰·자연어 회상·item 확인·격리 검증을 구분해 적습니다. | scope·update delay·항목 등 보이지 않은 필드는 `포털 미노출/미검증`입니다. | 회상 답변을 item CRUD·A/B 격리 성공으로 올리지 않습니다. |

기존 store가 준비되어 있고 **Memory 쓰기가 별도 승인됐을 때만** 내 agent의 새 Chat에 다음 합성 선호를 1회 보냅니다.

```prompt
Contoso 실습 가상 사용자 A의 데모 선호입니다. 이 실습에서는 키보드 색상을 파란색으로 선호한다고 기억해주세요. 실제 사람의 선호나 구매 승인이 아닙니다.
```

설정된 update delay가 지나고 새 Chat을 연 뒤 “실습 가상 사용자 A의 키보드 색상 선호가 무엇인가요?”를 1회 묻습니다. 같은 모델·Instructions의 **Memory 없는 별도 agent**에도 위 두 질문을 각기 새 Chat으로 1회씩 보내 비교합니다. 새 Chat에서 첫 선호를 다시 붙이지 않습니다.

회상 여부와 실제 Memory tool/item 표시가 있는지 따로 적습니다. 두 agent에 다른 Instructions나 정책 문맥이 있으면 이 비교는 통제되지 않았습니다. 다른 사용자 계정으로 로그인하거나 임의 scope를 바꿔 교차 접근을 시도하지 않습니다.

<div class="screen-step" markdown="1">

**조건부 입력 위치: 선호와 회상 질문은 서로 다른 새 Chat**

![Memory 없는 기본 agent의 Chat 입력창과 전송 버튼 위치.](../assets/portal/steps/agent-chat-controls.png)

**1 입력 / 2 전송:** 별도 승인이 있을 때만 사용합니다. 회상 질문의 새 Chat에 앞 선호를 다시 붙이지 않습니다. 이 그림은 입력 위치이며 Memory 쓰기·회상 결과가 아닙니다. 녹화의 Memory 호출은 0회입니다.

[자막 영상 02 · 02:43](../downloads/portal/index.html?clip=02-model-agent&t=163&lang=ko#02-model-agent)

</div>

## 성공 기준

Memory 없는 같은 대화·새 대화·서버 store를 구분했습니다. 포털에서 직접 확인하지 못한 저장·update·list·delete·A/B 사용자 격리·TTL 만료는 미검증으로 남겼습니다.

## 막혔을 때

연결 없음, 미지원 UI, embedding 없음, scope 미노출, runtime 권한 부족을 나눠 기록합니다. `Setup incomplete`는 권한 변경을 자동 승인하지 않습니다. Key·개인 token·shared scope로 우회하지 않습니다. Recall 실패를 성공할 때까지 반복하지 않습니다.

## 정리

합성 선호가 저장됐다면 store·시각·보존 조건을 L19에 적습니다. “잊어줘”도 실제 삭제를 유발할 수 있으므로 승인 없이 보내지 않습니다. TTL 설정은 즉시 삭제 증거가 아니며, 변경·삭제에는 별도 승인이 필요합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 관찰 가능한 Memory 설정, 조건부 회상 결과, item CRUD·격리·삭제 미검증과 보존 상태.

**다음:** [L16 Routines 실행 전 점검](#l17).

</div>
