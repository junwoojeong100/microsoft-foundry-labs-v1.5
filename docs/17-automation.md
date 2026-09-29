> **완성할 결과:** 반복 실행을 한 번 검증하고 끄며, 장기 작업과 Autopilot의 책임 경계를 설명합니다.

## 목표

**Routine은 “언제 실행?”, orchestration은 “어떻게 수행?”, Autopilot은 “누구로서 행동?”**에 답합니다.

## 준비

서버에서 실행 가능한 Prompt/Hosted agent, 프로젝트 권한, 지원 지역이 필요합니다. Routines는 GA이지만 **CMK를 요구하는 작업에는 사용할 수 없습니다.** 장기 실행·복구·steering 등의 기능은 Preview 조건을 확인합니다.

## 실행

### 1. 안전한 routine 설계하기

공식 **Automate agents with routines**의 scheduled routine 생성 흐름을 사용합니다. 포털 또는 같은 페이지의 SDK 경로를 선택합니다.

| 필드 | 실습값 |
| --- | --- |
| 이름 | `hb-policy-summary` 등 고유 실습 이름 |
| Trigger | 최소 5분 이상의 반복 또는 미래의 1회 timer |
| Action | 테스트 agent 1개 호출 |
| Input | “제공 정책을 세 문장으로 요약. 외부 발송·주문 금지.” |
| Identity | 기본 agent identity; 이유 없는 creator 위임 금지 |
| 운영 상태 | 한 번 검증 후 disable |

한 routine은 **trigger 1개, action 1개**입니다. 복잡한 분기를 스케줄 안에 억지로 넣지 않습니다.

### 2. 기다리지 말고 수동 dispatch로 한 번 확인하기

생성한 routine을 수동 dispatch하고 run history에서 status, input, output, response/trace 링크를 확인합니다. 즉시 **disable**하여 추가 실행을 막습니다.

현재의 기본 downstream 처리에는 시도별 timeout과 재시도가 존재합니다. 따라서 동일 작업이 중복으로 시도되어도 문제가 없는 도구를 사용합니다. 실제 주문처럼 부작용이 있는 도구는 durable idempotency와 승인 검증 없이는 연결하지 않습니다.

### 3. identity를 별도 검사하기

creator identity는 **routine을 만든 principal**을 뜻합니다. agent 작성자·게시자·connection 생성자·나중 편집자와 동일하다고 가정하지 않습니다. dispatch identity는 생성 시 선택되며 변경하려면 재생성이 필요할 수 있습니다.

GitHub issue와 Teams message 이벤트는 별도 connector connection을 사용합니다. 이벤트 발생자와 dispatch identity가 자동으로 같은 사람으로 바뀌지 않습니다.

### 4. 장기 실행 복구 설계 과제

긴 문서 검토가 중간에 끊긴다고 가정하고 다음 표를 채웁니다.

| 상태 | 영속적으로 남길 것 | 재개 시 금지 |
| --- | --- | --- |
| 문서 처리 중 | 처리한 문서 ID와 checkpoint | 완료한 작업 중복 수행 |
| 사람 승인 대기 | 승인 요청 ID·내용·만료 | 이전 버전 승인 재사용 |
| 출력 스트리밍 중 | 재연결 cursor/실행 ID | 재연결을 새 작업으로 오인 |
| 도구 완료 직후 중단 | 외부 작업 ID와 결과 | 외부 행동 재실행 |

현재 공식 장기 실행 가이드의 state, recovery, reconnect, steering 기능을 이 표에 매핑합니다. runtime 복구 기능이 업무 시스템의 중복 실행 방지를 대신한다고 생각하지 않습니다.

### 5. Autopilot 설계 과제

Foundry Autopilot은 **agent identity + Entra agent user account**를 가진 조직의 지속적인 구성원입니다. 단순히 timer로 자동 실행되는 agent와 다릅니다.

현재 모델에서 **Hosted Agent blueprint**를 만들고 팀별 instance가 각각의 identity·manager·허용 데이터/도구 범위를 갖습니다. M365 계정·메일·Teams 존재감이 있다고 모든 문서나 발송 권한이 생기지 않습니다.

실습 기본 범위는 역할·manager·허용 업무·금지 행동·비활성화 절차를 설계하는 것입니다. 실제 계정 생성·권한 부여·메일 발송은 Entra/M365 관리자와 별도 승인·라이선스·접근 조건을 확인한 뒤 진행합니다.

## 성공 기준

실제 routine 경로를 선택했다면 run history 1건과 disabled 상태를 확인했습니다. 장기 작업의 재개·중복 방지·승인 경계를 정의하고, 자동화와 Autopilot을 구분할 수 있습니다.

## 막혔을 때

지원 지역, agent protocol, 도구의 delegated user 요구, connection 인증을 확인합니다. routine을 재시도할 때 기존 활성 스케줄이 남아 중복 생성되지 않았는지 봅니다.

## 정리

routine을 disable한 뒤 테스트 객체를 삭제합니다. agent-scheduled reminder 도구를 켰다면 해당 예약도 확인합니다. “한 번만 테스트”했다는 의도만으로 예약이 멈추지는 않습니다.
