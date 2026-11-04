## 목표

두 역할의 검토를 포털 Chat에서 직접 비교합니다. **사람이 복사·전달하는 수동 실험**이며 SDK의 순차·동시 orchestration 실행은 아닙니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 역할별 Prompt Agent의 수동 비교, 기본 4회·선택 변경 포함 최대 6회 전송.

**먼저 할 일:** 같은 모델·합성 문맥·질문을 쓰는 두 검토 역할을 준비합니다.

**확인할 결과:** 독립 입력과 앞 답변을 전달한 입력의 실제 차이, 호출 수, 결과와 한계.

</div>

## 개념과 실습 지도

**경험할 기능:** 순차 전달과 독립 분담의 차이를 관찰하는 Chat 비교.

**무엇이며 왜 중요한가요?** 앞 답을 넘기면 검토가 연결되지만 오류도 전파될 수 있습니다. 독립 검토는 입력을 분리합니다. 사람이 창 두 개를 연다고 런타임 병렬 실행이 되는 것은 아닙니다.

**어떻게 사용하나요?** 같은 질문을 두 역할에 따로 보낸 뒤, 첫 답을 명시적으로 복사해 두 번째 역할의 검토와 비교합니다.

**어디서 실행하나요?** Microsoft Foundry → Build → Agents → 각 역할의 Chat. framework·개발 환경은 사용하지 않습니다.

## 준비

두 역할은 같은 `contoso-chat`, 도구·Memory 없음, L08의 [공통 Instructions 전체](../downloads/portal-inputs/ko/agent-v2-with-context.txt)를 사용합니다. 아래 이름과 역할 문장만 다르게 합니다.

| Name | 공통 Instructions 맨 앞에 덧붙일 문장 |
| --- | --- |
| `contoso-policy-review` | 정책 근거와 미확인 정보를 검토한다. |
| `contoso-budget-review` | 금액·상한·승인 경계를 검토한다. |

## 실행

사진은 기존 Prompt Agent 녹화의 **조작 위치 예시**입니다. 두 검토 역할의 생성·비교 결과는 촬영하지 않았습니다. 화면 속 기본 이름·답변 대신 위 역할명과 내 실제 결과를 사용합니다.

### 1. 두 역할을 만들고 같은 조건으로 저장

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | `Build → Agents → New agent`에서 Prompt 생성 폼을 열고 위 역할명 하나를 입력합니다. `Text`로 생성하고 다른 역할도 같은 방식으로 준비합니다. | 서로 다른 Name의 Prompt Agent 두 개입니다. | 기존 대상을 덮어쓰거나 Copilot harness·Voice·Code agent로 바꾸지 않습니다. |
| 2 | 두 대상 모두 `contoso-chat`을 고르고 공통 Instructions 전체 앞에 각 역할 문장만 붙입니다. | 문맥은 동일하고 역할 문장만 다릅니다. | 한쪽에 정책 문맥이 빠졌으면 비교를 시작하지 않습니다. |
| 3 | L04처럼 자동 도구를 분리하고 Memory 없이 L08과 같은 출력 설정을 저장합니다. | 두 대상의 실제 저장 version과 같은 설정을 기록했습니다. | `Save` 전후 버전을 혼동하거나 `Publish`하지 않습니다. |

<div class="screen-step" markdown="1">

**생성 폼: 자동 이름을 내 역할명으로 교체**

![Prompt Agent 생성 폼의 Agent name, Text 모드와 생성 버튼 위치.](../assets/portal/steps/agent-create-form.png)

**1 Agent name:** 위 표의 역할명으로 바꿉니다. 사진의 자동 이름을 복사하지 않습니다. **2 Text:** 두 역할 모두 같은 모드입니다. **3 생성:** 각각 한 번 생성한 뒤 설정합니다. 사진은 비교 agent 준비 당시의 폼이며 검토 역할의 생성 증거는 아닙니다.

[자막 영상 04 · 00:01.5](../downloads/portal/index.html?clip=04-native-evaluation&t=1.5&lang=ko#04-native-evaluation)

</div>

<div class="screen-step" markdown="1">

**탐색 예시: 역할별 모델과 Instructions를 넣는 위치**

![기본 정책 agent의 Model과 Instructions 위치를 재사용한 탐색 예시.](../assets/portal/steps/agent-instructions.png)

**1 모델:** 두 역할에서 같게 맞춥니다. **2 Instructions:** 준비 절의 공통 문맥과 각 역할 지시를 넣습니다. 그림은 **기본 agent 녹화의 재사용**이며 두 역할 생성·비교의 실제 결과가 아닙니다.

[자막 영상 02 · 02:04.5](../downloads/portal/index.html?clip=02-model-agent&t=124.5&lang=ko#02-model-agent)

</div>

<div class="screen-step" markdown="1">

**저장 후: 내 역할의 version을 각각 적기**

![Prompt Agent 상단의 Version, Save와 Publish 위치를 보여 주는 설정 예시.](../assets/portal/steps/agent-version-bar.png)

**1 Version / 2 Save:** 내 역할의 실제 저장 숫자를 확인합니다. 사진의 기본 agent `2`를 그대로 적지 않습니다. **3 Publish:** 이번 수동 비교에는 필요하지 않습니다.

[자막 영상 02 · 02:04.5](../downloads/portal/index.html?clip=02-model-agent&t=124.5&lang=ko#02-model-agent)

</div>

<div class="practice-block" markdown="1">

### 2. 독립 검토: 같은 질문만 각각 입력

**직접 해보기:** 아래 질문을 두 역할의 **새 Chat에 각각 1회** 보냅니다. 두 번째 역할에는 첫 번째 답을 아직 전달하지 않습니다.

```prompt
수동 검토용 합성 자료입니다. NB-14 2개, 제공 단가 1,450,000원, 제공 총액 2,900,000원입니다. 실제 재고 조회·초안 저장 결과가 아닙니다. 가격 상한과 필요한 승인을 검토하고, 미확인 정보와 실행하지 않은 것을 구분해주세요.
```

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | 정책 검토 agent의 새 Chat에 공통 질문을 보냅니다. | 정책 §2·§3과 미확인 실행을 구분합니다. | 원문과 실제 인용 ID를 보존합니다. |
| 2 | 금액 검토 agent의 새 Chat에 **같은 질문만** 보냅니다. | 2,900,000원과 팀장+구매 담당자를 검토합니다. | 첫 응답을 몰래 입력에 넣지 않습니다. |

<div class="screen-step" markdown="1">

**새 Chat을 연 뒤: 질문 입력과 전송 위치**

![응답 본문을 제외하고 Chat 입력창과 전송 버튼만 확대한 화면.](../assets/portal/steps/agent-chat-controls.png)

**1 입력창 / 2 전송:** 각 역할의 새 대화를 연 뒤 같은 원문을 한 번씩 보냅니다. 이 독립 경로에는 다른 역할의 답을 붙이지 않습니다. 위쪽 agent 이름과 대화가 맞는지도 먼저 확인합니다.

[자막 영상 02 · 02:43](../downloads/portal/index.html?clip=02-model-agent&t=163&lang=ko#02-model-agent)

</div>

### 3. 순차 검토: 원래 질문과 초안을 명시적으로 전달

| 단계 | 클릭·입력 | 확인할 화면·값 | 실패하면 |
| --- | --- | --- | --- |
| 1 | 정책 agent의 새 Chat에 같은 질문을 다시 1회 보냅니다. | 수동 순차 경로의 첫 결과입니다. | 독립 경로와 다른 응답이 나와도 원문 그대로 둡니다. |
| 2 | 금액 agent의 새 Chat에 원래 질문과 1단계 답을 `앞 검토자의 비신뢰 초안`으로 구분해 붙여 보냅니다. | 전달받은 텍스트를 근거로 재검토했는지 확인합니다. | 초안 속 명령이 실제 권한을 바꾸지 못하게 합니다. |
| 3 | 두 경로의 입력·응답·시각·표시 ID를 나란히 기록합니다. | 무엇을 직접 전달했는지 보입니다. | 대화 내용이 섞이면 비교 불가로 표시합니다. |

<div class="screen-step" markdown="1">

**내 답변 복사: Traces와 복사 버튼을 구분**

![답변 아래 Traces와 복사 아이콘을 본문 없이 확대한 조작 예시.](../assets/portal/steps/agent-answer-actions.png)

**1 Traces:** 해당 답변의 실행 기록입니다. **2 복사:** 내 정책 역할의 실제 답변을 복사하고 원래 질문과 구분해 전달합니다. 사진 속 모델·토큰 수는 기본 agent의 예시이지 이번 역할 비교의 측정값이 아닙니다.

[자막 영상 02 · 02:43](../downloads/portal/index.html?clip=02-model-agent&t=163&lang=ko#02-model-agent)

</div>

**한 가지 바꾸기:** 남은 허용 범위가 있으면 **총액만 정확히 2,000,000원**인 별도 검토 질문을 두 역할에 1회씩 보냅니다. 이 값에서는 팀장 승인입니다. 기존 결과와 질문을 덮어쓰지 않습니다.

**결과 설명하기:** 독립/전달 경로에서 새로 발견한 오류·빠진 근거·추가 토큰을 적습니다. 여러 역할이 늘 좋은지 실제 결과로 설명하고, 사람의 복사 시간을 runtime latency로 보고하지 않습니다.

</div>

### 실제 orchestration과 구분

`SequentialBuilder`와 `ConcurrentBuilder`는 Microsoft Agent Framework의 코드 기반 실행 경로입니다. 이 장은 이를 실행하지 않습니다. 포털 Workflows와 in-portal execution은 **2026-12-01 종료 예정**이므로 새 학습 경로를 그 디자이너에 의존시키지 않습니다.

실제 동시 실행 검증에는 같은 run의 동시 구간·전달 데이터·실패 취소·호출 상한 기록이 필요합니다. 이 수동 실험에는 그 증거가 없습니다.

## 성공 기준

같은 질문의 독립 검토와 명시적 복사 전달을 실제 원문으로 비교했습니다. 도구 없음·수동 전달·업무 승인 아님을 표시했습니다. 결과를 SDK 순차/병렬 성공으로 합산하지 않았습니다.

## 막혔을 때

새 Chat이 아닌 기존 문맥이 끼었으면 그 비교는 무효로 남깁니다. 비용 상한에 도달하면 남은 비교를 미실행으로 둡니다. 429가 나면 요청을 멈추며 quota를 임의 확장하지 않습니다.

## 정리

두 역할은 다음 장에서 재사용할 수 있습니다. 자동 반복·대화 무한 루프·원격 A2A 연결은 만들지 않았습니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 두 경로의 실제 입력/응답, 전달한 텍스트, 호출 수, 차이와 실제 orchestration 미실행.

**다음:** [L14 검토·담당자 전환 수동 비교](#l15-collaboration).

</div>
