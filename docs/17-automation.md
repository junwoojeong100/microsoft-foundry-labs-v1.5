> **완성할 결과:** Contoso 정책 요약의 실제 예약 실행을 응답/trace로 검증하고 disabled 상태를 확인합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · 서버에서 실행 가능한 에이전트와 로그 읽기 권한이 필요합니다.

**먼저 할 일:** 사용할 L05 에이전트와 수동 실행·1회 예약의 차이를 확인합니다.

**확인할 결과:** 예약 시각 뒤 실제 응답과 `enabled=false`를 확인합니다. 생성 완료나 수동 실행을 예약 성공으로 세지 않습니다.

</div>

## 목표

**Routine은 언제 실행할지, orchestration은 어떻게 처리할지, Autopilot은 어떤 조직 주체로 행동할지**를 정합니다.
예약 객체 생성과 업무 성공은 별개입니다.

## 개념과 실습 지도

**경험할 기능:** Routine의 trigger·action·enabled 상태, 수동 dispatch와 실제 timer 실행 확인입니다.

**무엇이며 왜 중요한가요?** Routine은 정해진 시각이나 이벤트에 agent 실행을 요청하는 예약입니다. Trigger는 “언제”, action은 “무엇을 실행할지”를 정합니다. 생성 요청 접수·실행 시작·업무 응답 완료는 서로 다른 상태입니다. 예약을 만든 뒤 브라우저를 닫아도 나중에 실행될 수 있으므로 반복 여부와 중지 확인이 중요합니다.

**어떻게 사용하나요?** 수동 호출을 시험하는 경로와 1회 timer를 시험하는 경로를 구분하고 새 receipt를 사용합니다. 같은 agent·입력 표식·예약 시각의 trace와 완료 응답을 찾아 연결한 뒤 disabled를 재확인합니다. 실행 기록이 비어 보이면 관찰 도구의 제한인지도 확인하며 무조건 재호출하지 않습니다.

**어디서 실행하나요?** 포털 Agents의 Routines에서 상태를 관찰하고 [routine_lab.py](../samples/routine_lab.py)로 제한된 실행을 재현합니다. 장기 orchestration·Autopilot 계정·업무 전송은 이 timer 실습과 다른 설계 과제입니다.

## 준비

서버에서 실행되는 Prompt Agent가 먼저 필요합니다. L05의 File search agent 또는
L15의 정책 worker를 사용하세요. 로컬 client-side 함수 agent를 예약해도 로컬 함수는 실행되지 않습니다.
서비스 Routines의 GA와 azd 확장의 Beta 상태를 구분하고, CMK 제한 등 현재 조건을 확인합니다.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd version
AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd extension list
AZURE_DEV_USER_AGENT=microsoft_foundry_skill azd ai routine --help
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `azd version` | 현재 azd 버전을 확인합니다. 앞의 `AZURE_DEV_USER_AGENT=...`는 이 명령 프로세스의 식별용 환경 변수입니다. | 로컬 버전 출력. skill 설치·로그인·권한 부여를 뜻하지 않습니다. |
| 2. `azd extension list` | 설치된 확장과 버전을 나열합니다. | 목록 조회만 하며 자동 설치/업그레이드하지 않습니다. |
| 3. `azd ai routine --help` | 설치된 확장의 실제 하위 명령과 옵션을 읽습니다. | 도움말 확인이며 예약 생성·추론은 하지 않습니다. |

</div>

SDK 기본 환경과 azd `azure.ai.routines` 확장을 준비합니다. 토큰을 파일에 저장하지 않습니다.
`results/azure-environment.json`의 프로젝트와 App Insights만 조회합니다.
CLI 확장/전역 설정을 자동 업그레이드하거나 다른 환경의 리소스를 이용하지 않습니다.

## 실행

### 1. 먼저 비활성 routine의 수동 호출

```bash
python samples/routine_lab.py create --agent 실제-agent-name --receipt results/routine-v2-manual.json
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py create --agent 실제-agent-name --receipt results/routine-v2-manual.json --live
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py dispatch --receipt results/routine-v2-manual.json --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `create --agent ... --receipt ...` | 실제 agent 이름과 새 소유 기록 경로를 지정하고 생성 계획만 읽습니다. `--receipt`는 실행 결과·대상을 추적할 파일입니다. | Azure 요청 없음. 로컬 함수만 있는 agent가 아닌 서버 실행 가능한 대상을 선택합니다. |
| 2. `create ... --live` | 비활성 1회 timer를 생성하고 지정한 receipt에 기록합니다. 환경 변수는 하위 azd에도 전달됩니다. | 실제 예약 객체 생성. 이 상태만으로 예약 실행 성공은 아닙니다. |
| 3. `dispatch ... --live` | 같은 receipt의 비활성 routine을 수동으로 한 번 실행 요청합니다. 사전 시도 파일로 중복 요청을 제한합니다. | 모델·agent 호출 비용 가능. 수동 접수/실행을 자동 예약 성공으로 표시하지 않습니다. |

</div>

고유 이름의 1회 timer를 **disabled**로 만들고 수동 dispatch합니다.
manifest는 trigger 1개·action 1개이며 input은 “Contoso 정책 요약, 외부 발송·주문·승인 금지”입니다.
`action.input`을 파일로 전달하고 존재하지 않는 create `--input` 옵션을 사용하지 않습니다.
기존 receipt를 덮어쓰지 않습니다. 새 실험은 `--receipt`로 별도 경로를 지정합니다.
dispatch 전에 별도 `.dispatch.json` 시도 기록을 독점 생성하므로 timeout이 나도 같은
receipt를 자동 재호출하지 않습니다. 수동 접수 ID만으로 실행 성공을 판정하지 않습니다.

### 2. 실제 예약 실행 확인

새 receipt에서 아래 경로를 선택하면 2분 뒤의 **1회 timer**를 생성합니다.
수동 dispatch를 예약 성공으로 대신 표시하지 않습니다.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py scheduled-test --agent 실제-agent-name --receipt results/routine-v2-scheduled.json --delay-seconds 120 --wait-seconds 360 --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `scheduled-test` | `--delay-seconds 120`은 2분 뒤 1회 예약, `--wait-seconds 360`은 최대 6분 증거 확인입니다. `--receipt`는 수동 실험과 다른 새 파일로 지정합니다. | 실제 예약·모델·로그 조회 비용 가능. 고유 입력과 완료 trace를 확인하고 종료 시 disable합니다. 6분은 비용 금액 상한이 아닙니다. |

</div>

최대 6분 동안 실제 action trace를 확인하고 `finally`에서 disable합니다.
입력에 고유 검증 표식을 넣고 같은 agent·예약 시각 이후·정확히 같은 사용자 입력의
`invoke_agent` span만 찾습니다. 성공 span, 실제 response ID, assistant의
`finish_reason=stop`, 비어 있지 않은 출력이 모두 있어야 검증됩니다.
가려진 출력, 진행 중/실패 기록, 다른 입력의 응답은 성공 증거가 아닙니다.

**CLI run history의 빈 배열/null을 미실행으로 해석하지 마세요.**
[현재 공식 문서](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines#view-run-history)는
azd의 history 조회를 지원하지 않는다고 명시합니다. 확인한 확장은 서비스의
`data`/`next_link` 대신 `value`/`nextPageToken`을 디코딩해 실행이 있어도
`{"value":null,"next_page_token":""}`를 출력할 수 있습니다.
Routine 생성·조회·중지는 계속 azd로 수행하며, 스크립트가 Routine REST/SDK로 우회하지는 않습니다.
실행 증거는 소유 App Insights의 제한된 KQL로 별도 확보합니다.
trace를 읽을 수 없다면 **실행 미확인**으로 종료하며 성공이나 미실행을 추측하지 않습니다.

### 3. 중지 상태 재확인

![실제 Build → Agents → Routines 목록. 두 Contoso 정책 timer가 Paused로 표시되고 대상 agent·trigger 시각·마지막 실행 열이 보인다.](../assets/portal/12-routines.png)

**화면 따라 읽기:** **Agents → Routines**에서 자기 예약 이름과 대상 agent를 먼저 찾습니다. 촬영 UI의 중지 표시는 **Paused**, CLI/API에서 확인할 값은 `enabled=false`입니다. **Last run**이 있다는 것만으로 업무 출력이 정상이라고 판단하지 말고 앞 단계의 trace/response와 연결합니다. 사진은 보존된 중지 예약을 관찰한 것이며 새 예약·dispatch·상태 변경은 하지 않았습니다.

```bash
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py stop --receipt results/routine-v2-scheduled.json --live
AZURE_DEV_USER_AGENT=microsoft_foundry_skill python samples/routine_lab.py status --receipt results/routine-v2-scheduled.json --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `stop --receipt ... --live` | 지정한 소유 예약의 enabled 상태를 false로 바꿉니다. | 실제 예약 중지 요청. routine 자체나 RG는 삭제하지 않습니다. |
| 2. `status --receipt ... --live` | 같은 예약의 현재 상태를 다시 읽습니다. | 원격 조회에서 `enabled=false`를 확인합니다. 중지 요청을 보냈다는 사실만으로 완료하지 않습니다. |

</div>

receipt의 이름·endpoint만 대상으로 삼습니다. 반복 cron을 자동 활성화하지 않으며,
예외나 중단 뒤에도 이 중지 명령을 실행합니다. 이 스크립트는 routine이나 RG를 삭제하지 않습니다.
원래 `results/routine.json`은 `status`/`stop`으로 계속 읽을 수 있으며 덮어쓰거나 재dispatch하지 않습니다.
disable 호출이 timeout/디코딩 오류로 끝나도 `show`를 다시 수행해 **같은 이름의 `enabled=false`**를 확인합니다.

### 4. identity와 복구 경계

routine creator, agent runtime identity, 도구 connection identity를 구분합니다.
사용자가 이벤트를 만들었다고 모든 하위 호출이 그 사람으로 실행되는 것은 아닙니다.
재시도·중복 호출이 있어도 이 실습은 읽기/초안만 수행합니다.
실제 주문에는 별도 승인과 durable idempotency가 필요하므로 연결하지 않습니다.

장기 실행의 checkpoint·재연결·승인 만료와 Autopilot의 manager·Entra agent user·
메일/Teams 권한은 **설계 과제**입니다. timer 실습이 Autopilot 계정 생성을 뜻하지 않습니다.
L19 Voice와 지속 평가를 선택했다면 해당 세션·스케줄도 별도로 중지합니다.

## 성공 기준

실제 예약 시점 이후의 action 실행, 완료된 업무 응답, disabled 상태를 확인했습니다.
예약 생성만 됐거나 수동 dispatch만 했다면 그 범위까지만 실행 완료로 기록합니다.
상태 조회가 실패했다면 “아마 중지됐을 것”이라고 쓰지 않습니다.
run ID를 읽지 못했다면 response/trace ID와 구분해 `null`로 남깁니다.
사람의 내용 검토는 선택 안내이며, 실행하지 않은 검토를 완료했다고 표시하지 않습니다.

<details markdown="1">
<summary>제작 당시의 관찰·복구 기록 — 학습자 자신의 새 실행 결과와 구분해서 읽기</summary>

기존 실험에서 저장한 “CLI history가 비었다”는 실패/관측 기록은 그대로 보존합니다.
후속 조사에서 같은 정책 worker의 예약 시각 `2026-09-29T22:38:35Z`와 수동 dispatch 시각
`22:44:59Z`에 성공한 action span과 실제 정책 요약 출력(`finish_reason=stop`)을 찾았습니다.
예약 시각의 trace는 `8bf878b65509efa39d9643632629f506`,
response는 `resp_07018918263947dc006abc3deaaf34819787a318905a8318ad`입니다.
직접 response 조회의 404도 보존했으며, 조회 불가를 응답 부재로 바꾸지 않았습니다.
이 증거는 다른 File search·Hosted·A2A 실행의 성공으로 대체한 것이 아닙니다.

수정한 runner의 별도 v2 검증에서는 `contoso-policy-timer-v2-9a3154d0`을 한 번만 예약했습니다.
`2026-09-30T01:58:35Z`의 trace `ebd60144b61d68788cb939b085f6c308`과
response `resp_0a4cb48ea4632934006abc6cca6314819390ca3283c545e1c2`에서
고유 표식이 일치하는 완료 출력을 확인했습니다. 수동 dispatch는 하지 않았고 `enabled=false`를 재확인했습니다.
원본은 `results/contoso-routine-04519d0f6e86.jsonl`과 `results/routine-v2-scheduled.json`에 보존합니다.

</details>

## 막혔을 때

CLI JSON decode 오류는 서비스 작업이 이미 성공한 뒤 발생할 수도 있습니다.
새 이름으로 무조건 재생성하지 말고 receipt 이름의 show/list를 먼저 확인합니다.
권한·protocol·model quota·도구 인증 오류를 run history에서 구분합니다.

## 정리

routine은 disabled로 보존합니다. 예약되지 않은 1회 timer라도 상태를 확인합니다.
Hosted를 대상으로 사용했다면 agent session compute도 별도로 stop해야 합니다.
