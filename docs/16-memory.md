> **완성할 결과:** 실제 Memory item을 저장·검색하고, 사용자 격리 및 승인된 item 삭제 후 부재를 확인합니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · Memory Preview와 두 종류의 모델 지원이 필요합니다.

**먼저 할 일:** 가상 사용자 A의 표 형식 선호 한 항목만 저장할 계획과 사용자 범위를 확인합니다.

**확인할 결과:** 같은 항목이 A에게만 검색되는지 확인합니다. 삭제는 승인받은 항목 하나에 한하며 수행하지 않았다면 미실행으로 적습니다.

</div>

## 목표

**Conversation은 대화 기록, Memory는 대화 사이 맥락, IQ는 조직 지식**입니다.
표 형식으로 답했다는 자연어만 보고 기억 성공을 판정하지 않습니다.

## 개념과 실습 지도

**경험할 기능:** 가상 사용자 A의 답변 형식 선호 하나를 저장하고 검색합니다.

**무엇이며 왜 중요한가요?** Memory는 대화가 끝난 뒤에도 다시 찾을 사용자 맥락입니다. Store는 보관소, item은 한 항목, scope는 사용자 범위, TTL은 보존 시간입니다. A의 기억을 B에게 보여 주면 안 됩니다.

**어떻게 사용하나요?** 저장한 항목 ID를 A와 B로 각각 검색합니다. 삭제 승인 후에는 같은 항목의 부재를 확인합니다. “잊었습니다”라는 답만으로는 부족합니다.

**어디서 실행하나요?** 터미널의 [memory_lab.py](../samples/memory_lab.py)와 포털 **Memory**를 사용합니다. 자동 기억 추출 전체가 아닌 한 항목의 저장·검색·격리·삭제 실습입니다.

## 준비

Memory는 **Preview**이며 지원 지역, chat·embedding 배포, 프로젝트 역할이 필요합니다.
현재 VNet 통합 제한이 있으므로 private 환경의 보안 설정을 바꾸어 실습하지 않습니다.
Python 기본 SDK 환경과 `.env`의 `FOUNDRY_EMBEDDING_DEPLOYMENT_NAME`을 준비합니다.

허용 내용은 가상 사용자 A의 “표 형식 답변 선호”뿐입니다.
실제 개인정보·급여·비밀번호·직원 정보는 저장하지 않습니다.

### 먼저 경로 정하기

| 준비할 것 | 어디서 확인하나요? | 없으면 |
| --- | --- | --- |
| 프로젝트·chat·embedding 배포 이름 | L01·L02에서 준비한 자기 `.env`와 모델 배포 목록 | 이름·지역·권한 확인 전 `create` 계획만 읽기 |
| 새 실습인지 여부 | 자기 폴더의 `results/memory.json` 존재 여부 | 기존 기록이 있으면 새 `create`를 반복하지 않기 |
| 실제 항목 삭제 승인 | 관리자에게 정확한 `memory_id`의 삭제 범위 확인 | 1–3단계 저장·격리까지만, 4단계는 미실행 |

흐름은 **store 생성 → item 1개 저장 → A/B 검색 비교 → 승인된 경우만 item 삭제**입니다. Search나 Hosted는 필요하지 않습니다. 편집기로 `results/memory.json`을 열어 값을 읽으며 원본을 수정하지 않습니다.

## 실행

### 1. 전용 store 만들기

![실제 Memory store의 Details 화면. chat·embedding 모델, 기본 TTL 3600초, User profile 활성과 Chat summary·Procedural memory 비활성이 표시된다.](../assets/portal/10-memory.png)

**화면 따라 읽기:** **Build → Memory → 자신의 store → Details**에서 모델·TTL·기억 종류를 확인합니다. **Memories**는 저장 항목을 확인하는 별도 탭입니다. 촬영한 store는 profile만 사용하며, **Save**가 비활성인 상태를 그대로 관찰했습니다. 새 item을 저장·검색·삭제하지 않았으므로 이 화면만으로 사용자 격리나 삭제 성공을 주장하지 않습니다.

```bash
python samples/memory_lab.py create
python samples/memory_lab.py create --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `memory_lab.py create` | 생성할 Memory store의 계획을 출력합니다. | Azure 요청 없음. 지원 모델·지역을 먼저 확인합니다. |
| 2. `create --live` | 고유 store와 A/B scope를 준비하고 기본 TTL 3600초 등을 설정합니다. | 원격 store 및 `results/memory.json` 생성. 저장·모델/embedding 이용 조건과 비용을 확인합니다. |

</div>

고유 store 이름과 A/B scope는 `results/memory.json`에 기록합니다.
profile만 켜고 summary/procedural 추출은 끕니다. 새 item의 기본 TTL은 **3,600초**입니다.
기존 receipt는 덮어쓰지 않습니다.

생성 후 receipt의 `name`, `endpoint`, `scope_a`, `scope_b`, `ttl_seconds`를 확인합니다. `memory_id`는 **다음 remember 성공 뒤**에 추가됩니다. store 이름과 item ID를 혼동해 `--confirm`에 넣지 않습니다.

### 2. 저장하고 실제 검색하기

```bash
python samples/memory_lab.py remember --live
python samples/memory_lab.py verify --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `remember --live` | receipt의 A scope에 “표 형식 답변 선호” 합성 item을 실제 생성하고 ID를 기록합니다. | 원격 데이터 쓰기입니다. 개인 정보나 새로운 사용자 scope를 임의로 넣지 않습니다. |
| 2. `verify --live` | A/B scope로 실제 Memory 검색을 수행하고 저장한 ID의 존재·격리를 검사합니다. | 서비스 조회·검색 비용 가능. 로컬 사전(dict) 조회가 아니며 A에는 있음, B에는 없음이 필요합니다. |

</div>

저수준 `create_memory`를 사용하므로 저장 작업과 item ID가 명확합니다.
검색은 실제 Memory API이며, 결과의 `memory_id`가 저장한 ID와 일치해야 합니다.
eventual consistency는 최대 6회/3초 간격으로만 기다립니다.
이 직접 CRUD 경로는 대화에서 자동 기억 추출까지 검증한 것은 아닙니다.

### 3. 격리 검사 읽기

앞의 `remember`는 저장 후 검색까지 수행하며, `verify`는 같은 항목을 새 요청으로 재확인합니다. **여기서는 그 출력의 `Evidence:` 파일을 읽습니다.** 새 검색 명령을 추가할 필요는 없습니다.
A에는 해당 item이 있고, B는 비어 있어야 합니다. 결과 원문을 각각 보존합니다.
scope는 receipt에서만 가져오며 임의 사용자 입력으로 바꾸지 않습니다.
실제 서비스에서는 인증된 주체로부터 서버가 scope를 결정해야 합니다.

| 원본의 이벤트·값 | 저장 후 기대하는 관계 |
| --- | --- |
| `memory_created`의 ID / receipt의 `memory_id` | 같은 실제 항목 |
| `memory_search`의 `scope_label=scope_a` | 그 항목 ID가 검색됨 |
| `memory_search`의 `scope_label=scope_b` | 결과가 비어 있음 |
| `verified` | 저장·격리 판정. 삭제하지 않았다면 `deleted_item_absent`를 삭제 성공으로 읽지 않음 |

### 4. item 하나만 삭제하고 다시 검색하기

관리자가 **실습 item 삭제를 승인한 경우에만** 실행합니다.
Azure store/RG 삭제와 item 삭제는 별개입니다. 이번 환경에 삭제 금지 정책이 있으면
이 단계는 미실행으로 기록하고 저장·격리 결과만 보고합니다.

```bash
python samples/memory_lab.py forget --confirm 실제-memory-id --live
python samples/memory_lab.py verify --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — item 삭제를 별도로 승인받은 경우에만 수행합니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `forget --confirm ... --live` | `--confirm`에 receipt와 일치하는 실제 item ID를 넣습니다. endpoint·store 소유 정보·scope를 대조한 뒤 그 item만 삭제합니다. | 원격 데이터 삭제. store/RG 삭제는 아니며 비용 허용과 삭제 승인은 서로 다릅니다. |
| 2. `verify --live` | 삭제가 기록된 상태에서 새로운 API 검색으로 해당 item의 부재와 scope 경계를 확인합니다. | 실제 조회. 이전 검색 결과나 자연어 답변을 재사용하지 않습니다. |

</div>

endpoint·store 소유 metadata·item scope를 확인한 후 해당 item만 삭제합니다.
삭제 후 새로운 API 검색에서 ID가 반환되지 않아야 성공입니다.
“잊었습니다”라는 답변, 기존 conversation, TTL 설정만으로 삭제 성공을 주장하지 않습니다.

## 성공 기준

store/item ID, A 검색 결과, B 격리 결과가 있고, 삭제를 수행했다면 삭제 후 검색까지 확인했습니다.
삭제가 허용되지 않았다면 **구현 완료 / 저장·격리 실행 완료 / 삭제 미실행**으로 분리합니다.
자동 remember/forget prompt, procedural memory 등 실행하지 않은 기능은 별도로 표시합니다.

## 막혔을 때

모델/embedding 지원, store 설정, 사용자 scope, API Preview 접근을 확인합니다.
API가 실패하면 원본 오류를 보존하고 로컬 dict로 대체한 것을 Azure Memory 성공으로 표시하지 않습니다.
`memory.json`이 있는데 생성이 실패했다면 원격 store의 생성 여부를 담당자와 먼저 대조합니다. 기록을 지워 `create`를 다시 실행하거나 확인하지 않은 소유 정보를 수정하지 않습니다. 1시간 TTL 이후 항목이 사라진 것은 승인된 삭제 실행의 증거가 아니며, 새 실습은 별도의 승인·소유 기록으로 준비합니다.

## 정리

기본값은 store 보존입니다. TTL은 item 수명이며 store·trace·conversation 전체 삭제를 뜻하지 않습니다.
보존 정책과 확인 시점을 기록하고, 자원 삭제는 별도 승인을 받습니다.
