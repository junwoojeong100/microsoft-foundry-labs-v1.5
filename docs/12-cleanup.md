> **완성할 결과:** 실습 자원·반복 실행·유휴 컴퓨트·데이터 보존을 확인하고, 공유 자원은 건드리지 않고 종료합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 모든 참여자의 필수 마무리 · 자신이 만든 자원만 확인합니다.

**먼저 할 일:** 로컬만 했는지, 포털 또는 SDK로 Azure 자원을 만들었는지 아래 표에서 고릅니다.

**확인할 결과:** 남은 자원의 상태·담당자·다음 비용 확인 시각을 적습니다. 삭제는 정확한 대상의 별도 승인이 있을 때만 합니다.

</div>

## 목표

**브라우저를 닫는 것은 과금 중지가 아닙니다.** agent 삭제만으로 Search·로그·업로드 파일·PTU·게시 채널이 모두 사라지는 것도 아닙니다.

## 개념과 실습 지도

**경험할 기능:** 내가 만든 자원을 확인하고 종료·보존 담당자를 정합니다.

**무엇이며 왜 중요한가요?** 브라우저를 닫아도 예약·저장소·로그 비용은 남을 수 있습니다. Receipt는 실습이 만든 자원의 이름·ID를 적은 **소유 기록 파일**입니다. 결제 영수증이나 삭제 허가가 아닙니다.

**어떻게 사용하나요?** 자신이 한 실습의 행만 따라갑니다. 실행 상태·공유 여부·담당자를 확인하고 승인된 대상만 삭제합니다. 비용은 반영 지연을 고려해 다시 확인합니다.

**어디서 실행하나요?** 로컬만 했다면 PC의 서버를 끕니다. Azure 자원을 만들었다면 포털과 소유 기록을 대조합니다. [세션 중지 코드](../scripts/stop_sessions.py)는 심화용이며 `--live` 없이도 동작합니다.

## 준비

생성한 자원 목록과 `results/contoso-lab-....json` receipt를 모읍니다. 강사/다른 학습자와 공유한 자원을 표시합니다.

## 실행

### 먼저: 자신이 실제로 진행한 경로만 정리하기

| 내가 한 실습 | 지금 할 일 |
| --- | --- |
| 읽기·로컬 데이터·함수만 | L07 서버를 켰다면 해당 터미널에서 Ctrl+C. Azure 자원을 만들지 않았다면 Azure 삭제 명령은 실행하지 않음 |
| 포털에서 에이전트·파일 생성 | 만든 이름을 모아 아래 3단계의 목록과 대조. 공유 여부와 담당자·보존 기한 확인 |
| SDK로 L04/L05/L06 실행 | 마지막 `Cleanup:` 명령의 `--receipt` 경로를 찾고 아래 2단계 확인 |
| Hosted·Routine·Voice 등 심화 실행 | 아래 1단계에서 그 실습의 기록된 세션·예약만 중지하고 상태 재확인 |

**보존과 삭제 중 무엇을 할지 확인하기 전에는 삭제하지 않습니다.** 비용이 남을 수 있으므로 “보존”이라고만 쓰지 말고 담당자와 다음 확인 시각까지 적습니다.

### 1. 반복·장기 실행부터 멈추기

활성 routine, voice session, hosted agent의 실행/세션, 지속 평가, 학습 작업을 먼저 확인합니다. 삭제를 시작하기 전에 새로운 실행이 발생하지 않게 합니다.

기본 코스에서 만들지 않은 작업은 해당 없음으로 기록합니다. 다음은 **심화/관리자 경로**이며, 다섯 명령을 모두 복사해 실행하는 공통 종료 절차가 아닙니다.

<details class="operator-only" markdown="1">
<summary>심화·관리자만: 소유 receipt가 있는 작업의 중지·상태·비용 확인</summary>

```bash
python scripts/stop_sessions.py
python samples/routine_lab.py stop --live
python scripts/azure_environment.py status --live
python scripts/operations_status.py
python scripts/cost_status.py
```

<div class="command-explanation" markdown="1">

**명령 해설 — 실행한 실습의 소유 receipt가 있는 관리자 경로입니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `stop_sessions.py` | 기록된 Hosted client 세션에 실제 stop을 보내고 같은 ID를 다시 조회합니다. 이 스크립트에는 `--live` 안전 스위치가 없습니다. | 세션 compute 상태를 변경합니다. agent/RG/receipt 삭제는 하지 않으며 미확인 중지는 오류입니다. |
| 2. `routine_lab.py stop --live` | 기본 `results/routine.json`에 기록된 예약을 disable합니다. 다른 receipt를 썼다면 L17처럼 `--receipt`를 명시합니다. | 실제 예약 상태 변경. 다른 예약이나 RG를 삭제하지 않습니다. |
| 3. `azure_environment.py status --live` | 소유 receipt의 Azure 환경 상태를 읽어 확인합니다. | Azure 읽기 요청 및 상태 기록. 모델 추론은 하지 않습니다. |
| 4. `operations_status.py` | 소유 환경의 세션·optimizer·평가 schedule·routine을 읽습니다. `--live` 없이 실행되며 남은 작업은 실패 상태로 알립니다. | 승인된 읽기 범위에서 실행하고 비공개 `results/operations-status.json`에 저장합니다. 보존된 공개 검증 원본을 덮어쓰지 않습니다. |
| 5. `cost_status.py` | 소유 RG의 생성 시각부터 현재까지 ActualCost를 서비스별로 조회합니다. `--live` 없이 실제 청구 API를 읽습니다. | 승인된 비용 조회 후 개인 `results/cost-status.json`에 저장합니다. 공개 검증 원본은 바꾸지 않습니다. 빈 청구 행은 비용 0의 증거가 아닙니다. |

</div>

각 명령은 해당 실습을 실행해 receipt가 있는 경우에 사용합니다.
마지막 두 명령은 **소유 receipt로 범위를 제한한 읽기 전용 Azure 조회**입니다.
`operations_status.py`는 세션·optimizer job·활성 평가 schedule·routine을 확인하며,
`cost_status.py`는 새 RG에 반영된 실제 비용만 조회합니다. 빈 비용 행을 0달러로 표시하지 않습니다.
**이번 제작 검증은 생성한 Azure 자원을 삭제하지 않고 보존**합니다.
routine은 disable, Hosted는 compute stop만 수행합니다. `cleanup --live`, `azd down`,
resource group 삭제를 자동 실행하지 않습니다. 아래 삭제 경로는 별도 승인이 있는 학습자를 위한 설명입니다.

</details>

### 2. SDK 실습 자원만 정확히 삭제하기

각 Azure 샘플의 마지막 줄에 **자신의 run ID가 들어 있는 cleanup 명령**이 출력됩니다.
자원 보존/삭제 승인을 먼저 확인한 경우에만 해당 명령을 사용하세요.

```text
python samples/workshop.py cleanup
  --receipt results/contoso-lab-실제ID.json
  --confirm contoso-lab-실제ID
  --live
```

위 블록은 자리표시자 설명용입니다. 실제로는 샘플이 출력한 **한 줄짜리 명령**을 사용합니다. `--live`가 없으면 삭제하지 않습니다. receipt의 프로젝트와 `.env`의 프로젝트가 다르면 중단합니다.

**옵션 해설:** `cleanup`은 삭제 경로, `--receipt`는 본인이 만든 정확한 소유 기록 파일, `--confirm`은 그 기록의 run ID를 사람이 대조했다는 확인값입니다. `--live`는 실제 삭제를 허용합니다. 다른 사람의 receipt·스크린샷의 예시 ID를 복사해서 실행하지 마세요. 이 설명을 읽는 것만으로 삭제 승인이 주어지는 것은 아닙니다.

cleanup은 기록된 conversation → 실습 전용 agent → vector store → file 순서로 처리합니다. 이미 없어진 항목은 `already_absent`로 기록합니다. 권한 오류 등 다른 오류를 삭제 성공으로 숨기지 않습니다.

### 3. 포털에서 만든 자원을 별도로 확인하기

| 자원 | 종료 동작 |
| --- | --- |
| Prompt agent·버전·conversation | 불필요한 실습 객체 삭제 |
| File search | vector store와 원본 uploaded file 각각 확인 |
| Toolbox·connections·memory | 사용 여부 확인 후 실습용 객체만 삭제 |
| Hosted runtime·세션 | 실행 상태와 비용 항목 확인 |
| AI Search·Storage·로그 | 공유 여부·보존 정책 확인 후 담당자가 정리 |
| 모델 배포·PTU·GPU | 사용량/예약/유휴 비용 구분; 별도 계약·예약 확인 |
| 게시된 채널·Bot·앱 | 사용자 접근 회수와 자원 정리를 각각 확인 |
| Fine-tuned deployment·model | 배포 삭제와 학습된 모델 삭제를 구분 |

vector store의 만료만으로 원본 파일이 정리된다고 생각하지 않습니다. 에이전트·프로젝트·연결된 Azure 자원은 서로 수명주기가 다를 수 있습니다.

### 4. 마지막 비용·데이터 확인하기

Cost Management에서 비용 반영 지연을 고려하여 다음 날 다시 확인할 담당자를 정합니다. 예산 알림을 껐다고 과금이 중단되는 것은 아닙니다.

결과 기록은 학습에 필요한 최소 범위만 남기고 실제 PII·토큰·연결 비밀을 제거합니다. 그룹 삭제는 **전용 실습 그룹임을 소유자가 확인한 경우에만** Azure 포털에서 범위를 검토한 뒤 수행합니다. 이 가이드는 광범위한 `az group delete` 명령을 제공하지 않습니다.

## 성공 기준

생성 자원마다 **상태(삭제 / 공유 유지 / 보존)**와 **담당자·다음 확인 시각**을 함께 기록합니다. 보존한다면 기한도 적습니다. routine·지속 평가·voice session의 무의도 실행이 남아 있지 않은지 확인합니다.

| 자원 이름 | 상태와 확인 근거 | 담당자 | 보존 기한·다음 비용 확인 |
| --- | --- | --- | --- |
| 내가 만든 자원별로 기록 | 실제 확인한 값. 조회하지 못했으면 미확인 | 직접 지정 | 직접 지정 |

Azure 자원을 만들지 않았다면 **“로컬 실습만 수행 / Azure 생성 없음”**으로 적습니다. L07 서버를 켰다면 해당 터미널에서 종료한 것도 확인합니다.

삭제 금지 환경은 “명시적 삭제 승인까지 보존”으로 기록합니다.
Search Basic·로그·저장소는 요청이 없어도 비용이 남을 수 있습니다.
다음 확인은 검증 종료 후 24시간 이내를 권장하며, 확인 담당자 없이 “비용 0”이라고 결론내리지 않습니다.

<details class="provenance-note" markdown="1">
<summary>참고: 제작 당시의 보존 기록 — 자신의 종료 상태와 구분</summary>

이번 검증의 Azure 인프라와 agent/store는 보존했습니다. Memory 수명주기 검증의 **합성 item 1개**
삭제와 Azure store/RG 삭제는 구분하여 기록했습니다. 검증용 vector store의 자동 만료도 해제하여
보존하므로, 이후 승인된 정리 전까지 저장 비용 가능성이 남습니다.

</details>

## 막혔을 때

삭제 오류를 숨기지 마세요. 자원 ID, 오류 코드, 담당자를 기록하고 남은 비용 가능성을 알립니다. timeout으로 서버에서 생성 여부가 불분명한 경우 receipt뿐 아니라 포털의 실습 이름과 생성 시간도 확인합니다.

## 정리

기본 코스가 끝났습니다. 다음 기능은 필요할 때만 추가합니다. 진행 표시를 초기화해도 Azure 자원은 삭제되지 않습니다.
