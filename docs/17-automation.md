> **완성할 결과:** Contoso 정책 요약을 실제 예약 실행하고 run history와 disabled 상태를 확인합니다.

## 목표

**Routine은 언제 실행할지, orchestration은 어떻게 처리할지, Autopilot은 어떤 조직 주체로 행동할지**를 정합니다.
예약 객체 생성과 업무 성공은 별개입니다.

## 준비

서버에서 실행되는 Prompt Agent가 먼저 필요합니다. L05의 File search agent 또는
L15의 정책 worker를 사용하세요. 로컬 client-side 함수 agent를 예약해도 로컬 함수는 실행되지 않습니다.
서비스 Routines의 GA와 azd 확장의 Beta 상태를 구분하고, CMK 제한 등 현재 조건을 확인합니다.

```bash
azd version
azd extension list
azd ai routine --help
```

SDK 기본 환경과 azd `azure.ai.routines` 확장을 준비합니다. 토큰을 파일에 저장하지 않습니다.

## 실행

### 1. 먼저 비활성 routine의 수동 호출

```bash
python samples/routine_lab.py create --agent 실제-agent-name
python samples/routine_lab.py create --agent 실제-agent-name --live
python samples/routine_lab.py dispatch --live
```

고유 이름의 1회 timer를 **disabled**로 만들고 수동 dispatch합니다.
manifest는 trigger 1개·action 1개이며 input은 “Contoso 정책 요약, 외부 발송·주문·승인 금지”입니다.
`action.input`을 파일로 전달하고 존재하지 않는 create `--input` 옵션을 사용하지 않습니다.
현재 receipt가 있으면 중복 생성하지 않습니다.

### 2. 실제 예약 실행 확인

새 실습 환경/receipt에서 아래 경로를 선택하면 3분 뒤의 **1회 timer**를 생성합니다.
수동 dispatch를 예약 성공으로 대신 표시하지 않습니다.

```bash
python samples/routine_lab.py scheduled-test --agent 실제-agent-name --live
```

최대 6분 동안 run history를 확인하고 `finally`에서 disable합니다.
결과가 생겼다는 사실만으로 성공 판정하지 않습니다. status·action output·
실제 response ID를 원문에서 확인합니다. 입력이 서비스에서 가려졌으면 추측해서 채우지 않습니다.

### 3. 중지 상태 재확인

```bash
python samples/routine_lab.py stop --live
python samples/routine_lab.py status --live
```

receipt의 이름·endpoint만 대상으로 삼습니다. 반복 cron을 자동 활성화하지 않으며,
예외나 중단 뒤에도 이 중지 명령을 실행합니다. 이 스크립트는 routine이나 RG를 삭제하지 않습니다.

### 4. identity와 복구 경계

routine creator, agent runtime identity, 도구 connection identity를 구분합니다.
사용자가 이벤트를 만들었다고 모든 하위 호출이 그 사람으로 실행되는 것은 아닙니다.
재시도·중복 호출이 있어도 이 실습은 읽기/초안만 수행합니다.
실제 주문에는 별도 승인과 durable idempotency가 필요하므로 연결하지 않습니다.

장기 실행의 checkpoint·재연결·승인 만료와 Autopilot의 manager·Entra agent user·
메일/Teams 권한은 **설계 과제**입니다. timer 실습이 Autopilot 계정 생성을 뜻하지 않습니다.
L19 Voice와 지속 평가를 선택했다면 해당 세션·스케줄도 별도로 중지합니다.

## 성공 기준

실제 예약 시점에 생성된 run, 업무 결과, disabled 상태를 확인했습니다.
예약 생성만 됐거나 수동 dispatch만 했다면 그 범위까지만 실행 완료로 기록합니다.
상태 조회가 실패했다면 “아마 중지됐을 것”이라고 쓰지 않습니다.

## 막혔을 때

CLI JSON decode 오류는 서비스 작업이 이미 성공한 뒤 발생할 수도 있습니다.
새 이름으로 무조건 재생성하지 말고 receipt 이름의 show/list를 먼저 확인합니다.
권한·protocol·model quota·도구 인증 오류를 run history에서 구분합니다.

## 정리

routine은 disabled로 보존합니다. 예약되지 않은 1회 timer라도 상태를 확인합니다.
Hosted를 대상으로 사용했다면 agent session compute도 별도로 stop해야 합니다.
