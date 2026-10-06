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

**경험할 기능:** 정책 요약을 한 번 예약하고 실행·중지 상태를 확인합니다.

**무엇이며 왜 중요한가요?** Routine은 에이전트 실행 예약입니다. Trigger는 “언제”, action은 “무엇을” 정합니다. 브라우저를 닫아도 실행될 수 있으므로 생성뿐 아니라 실행 결과·중지 상태까지 확인합니다.

**어떻게 사용하나요?** 수동 호출과 예약 실행을 별도 기록합니다. 예약 이후의 실제 응답을 찾고 `enabled=false`를 다시 확인합니다. 빈 목록만 보고 재실행하지 않습니다.

**어디서 실행하나요?** 포털 **Agents → Routines**와 [routine_lab.py](../samples/routine_lab.py)를 사용합니다. Autopilot 계정·업무 전송·장기 실행은 별도 설계 과제입니다.

## 준비

서버에서 실행되는 Prompt Agent가 먼저 필요합니다. L05의 File search agent를 사용하세요.
L13·L14의 Agent Framework 역할은 로컬 코드에서 실행되므로 예약 대상이 아닙니다. 로컬 client-side 함수 agent를 예약해도 로컬 함수는 실행되지 않습니다.
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

SDK 기본 환경을 사용합니다. azd나 Routine 확장이 없다면 [L12의 azd 준비 절](#l12-azd)만 따라 설치·인증을 확인하고, 필요한 경우 `azd extension install azure.ai.routines`로 확장을 설치합니다. 설치된 확장의 `azd ai routine --help`를 기준으로 명령을 확인하며 강제 업데이트하지 않습니다. Hosted 배포 자체는 필요 없습니다.
`results/azure-environment.json`의 프로젝트와 App Insights만 조회합니다.
CLI 확장/전역 설정을 자동 업그레이드하거나 다른 환경의 리소스를 이용하지 않습니다.

### 먼저 경로 정하기

| 필요한 값 | 어디서 가져오나요? | 확인할 관계 |
| --- | --- | --- |
| `실제-agent-name` | L05의 자기 프로젝트 → Build → Agents의 실제 이름, 또는 그 SDK 실행의 소유 receipt | File search가 서버에서 실행됨. L06의 로컬 함수 agent 이름을 넣지 않음 |
| 프로젝트·App Insights | 내가 L01에서 만든 `results/azure-environment.json`과 로그 연결 | `.env` 프로젝트와 일치하고 action trace를 읽을 수 있음 |
| 두 `--receipt` 경로 | 아래 수동용·예약용 **서로 다른 새 파일** | 기존 기록·다른 언어 기록을 덮어쓰지 않음 |

**수동 1회 → 예약 1회 → 둘 다 중지 확인** 순서입니다. Azure 승인이 없으면 첫 `create` 계획까지만 읽습니다. 로그 권한·응답 수집 조건이 준비되지 않았다면 예약을 만들기 전에 멈춥니다. 실행 후 trace가 없다는 이유로 다시 예약하지 않습니다.

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

<details class="optional-path" markdown="1">
<summary>왜 CLI 실행 이력 대신 trace를 확인하나요?</summary>

**CLI run history의 빈 배열/null을 미실행으로 해석하지 마세요.**
[현재 공식 문서](https://learn.microsoft.com/azure/foundry/agents/how-to/use-routines#view-run-history)는
azd의 history 조회를 지원하지 않는다고 명시합니다. 확인한 확장은 서비스의
`data`/`next_link` 대신 `value`/`nextPageToken`을 디코딩해 실행이 있어도
`{"value":null,"next_page_token":""}`를 출력할 수 있습니다.
Routine 생성·조회·중지는 계속 azd로 수행하며, 스크립트가 Routine REST/SDK로 우회하지는 않습니다.
실행 증거는 소유 App Insights의 제한된 KQL로 별도 확보합니다.
trace를 읽을 수 없다면 **실행 미확인**으로 종료하며 성공이나 미실행을 추측하지 않습니다.

</details>

`Evidence:` 원본과 receipt를 나란히 열어 **같은 agent → `trigger_at` 이후 → 같은 `marker`가 포함된 입력 → 완료 response/trace**를 연결합니다. 수동 receipt의 결과를 예약 receipt의 성공으로 복사하지 않습니다.

### 3. 중지 상태 재확인

![중지된 예약 목록 예시. Build → Agents → Routines에 Paused 상태와 대상 agent·trigger 시각·마지막 실행 열이 보인다.](../assets/portal/12-routines.png)

**화면 따라 읽기:** **Agents → Routines**에서 자기 예약 이름과 대상 agent를 먼저 찾습니다. UI의 중지 표시는 **Paused**, CLI/API에서 확인할 값은 `enabled=false`입니다. **Last run**을 앞 단계의 trace/response와 연결해 업무 출력도 확인합니다.

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

| 남길 기록 | 수동 실행 | 예약 실행 |
| --- | --- | --- |
| 대상 | 수동 receipt의 이름·agent | 예약 receipt의 이름·agent·`trigger_at` |
| 실행 근거 | 수동 요청 후 실제 response/trace | 예약 시각 이후 같은 입력의 실제 response/trace |
| 종료 근거 | 해당 이름의 `enabled=false` | 해당 이름의 `enabled=false` |

`dispatch`와 `scheduled-test`는 종료 시 중지를 시도하지만, 오류가 있었으면 **그때 사용한 receipt**로 3단계의 `stop`·`status`를 수행합니다. 수동 실행 오류에 예약용 경로를 복사하지 않습니다.

### 4. identity와 복구 경계

routine creator, agent runtime identity, 도구 connection identity를 구분합니다.
사용자가 이벤트를 만들었다고 모든 하위 호출이 그 사람으로 실행되는 것은 아닙니다.
재시도·중복 호출이 있어도 이 실습은 읽기/초안만 수행합니다.
실제 주문에는 별도 승인과 durable idempotency가 필요하므로 연결하지 않습니다.

장기 실행의 checkpoint·재연결·승인 만료와 Autopilot의 manager·Entra agent user·
메일/Teams 권한은 **설계 과제**입니다. timer 실습이 Autopilot 계정 생성을 뜻하지 않습니다.
지속 평가를 선택했다면 해당 스케줄도 별도로 중지합니다.

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 1회 예약과 에이전트 입력을 정의하는 manifest — 읽기용</summary>

#### 포털 Routines와 실제 생성 manifest

포털 **Agents → Routines**는 예약된 시각·agent·활성 상태를 보여 줍니다. 동봉 Python은 반복 일정을 추측해 만들지 않고, 고유한 receipt와 함께 timer trigger 한 건과 agent action 한 건을 manifest로 씁니다.

```python
manifest = {
    "triggers": {
        "default": {"type": "timer", "at": fire_at.strftime("%Y-%m-%dT%H:%M:%SZ")}
    },
    "action": {
        "type": "invoke_agent_responses_api",
        "agent_name": args.agent,
        "input": state["input"],
    },
}
write_new(manifest_path, manifest)
created = azd(
    endpoint, evidence, "create", name,
    "--file", str(manifest_path),
    "--enabled=false",
)
```

| Portal Routines view | 코드/receipt에서 대조할 값 |
| --- | --- |
| Routine name | `name`과 receipt의 `state["name"]` |
| Trigger time | `triggers.default.at`와 `state["trigger_at"]` |
| Target agent / input | `action.agent_name` / `action.input` |
| Enabled / Paused | `azd show`의 `enabled`; timer 생성 후 `stop_verified(...)` |
| Last run | 별도 App Insights trace와 response ID; receipt만으로 실행을 주장하지 않음 |

`fire_at`은 UTC 예약 시각, `manifest_path`는 `results/`의 새 JSON 파일입니다. 동봉 Python은 azd CLI를 호출하며 포털 UI를 자동 조작하지 않습니다. 포털의 대상·시각·Paused 상태를 코드 입력과 대조하고 live 작업은 해당 소유 기록·`--live`·승인 범위로 실행합니다.

</details>

## 성공 기준

실제 예약 시점 이후의 action 실행, 완료된 업무 응답, disabled 상태를 확인했습니다.
예약 생성만 됐거나 수동 dispatch만 했다면 그 범위까지만 실행 완료로 기록합니다.
상태 조회가 실패했다면 “아마 중지됐을 것”이라고 쓰지 않습니다.
run ID를 읽지 못했다면 response/trace ID와 구분해 `null`로 남깁니다.
사람의 내용 검토는 선택 안내이며, 실행하지 않은 검토를 완료했다고 표시하지 않습니다.

## 막혔을 때

CLI JSON decode 오류는 서비스 작업이 이미 성공한 뒤 발생할 수도 있습니다.
새 이름으로 무조건 재생성하지 말고 receipt 이름의 show/list를 먼저 확인합니다.
권한·protocol·model quota·도구 인증 오류는 실제 action trace와 원본 오류에서 구분합니다. 빈 CLI run history로 원인을 단정하지 않습니다.

## 정리

routine은 disabled로 보존합니다. 예약되지 않은 1회 timer라도 상태를 확인합니다.
Hosted를 대상으로 사용했다면 agent session compute도 별도로 stop해야 합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 수동용·예약용 receipt 각각의 이름·실제 응답/trace·`enabled=false` 확인. 상태가 미확인이면 해당 receipt로 중지·조회를 확인하고 떠납니다.

**다음:** 통제 설계를 선택하면 [L17](#l21), 선택 실습을 마쳤다면 [L19](#l12). 활성 예약을 남긴 채 종료하지 않습니다.

</div>
