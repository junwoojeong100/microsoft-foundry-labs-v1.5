> **완성할 결과:** 실제 Memory item을 저장·검색하고, 사용자 격리 및 승인된 item 삭제 후 부재를 확인합니다.

## 목표

**Conversation은 대화 기록, Memory는 대화 사이 맥락, IQ는 조직 지식**입니다.
표 형식으로 답했다는 자연어만 보고 기억 성공을 판정하지 않습니다.

## 준비

Memory는 **Preview**이며 지원 지역, chat·embedding 배포, 프로젝트 역할이 필요합니다.
현재 VNet 통합 제한이 있으므로 private 환경의 보안 설정을 바꾸어 실습하지 않습니다.
Python 기본 SDK 환경과 `.env`의 `FOUNDRY_EMBEDDING_DEPLOYMENT_NAME`을 준비합니다.

허용 내용은 가상 사용자 A의 “표 형식 답변 선호”뿐입니다.
실제 개인정보·급여·비밀번호·직원 정보는 저장하지 않습니다.

## 실행

### 1. 전용 store 만들기

```bash
python samples/memory_lab.py create
python samples/memory_lab.py create --live
```

고유 store 이름과 A/B scope는 `results/memory.json`에 기록합니다.
profile만 켜고 summary/procedural 추출은 끕니다. 새 item의 기본 TTL은 **3,600초**입니다.
기존 receipt는 덮어쓰지 않습니다.

### 2. 저장하고 실제 검색하기

```bash
python samples/memory_lab.py remember --live
python samples/memory_lab.py verify --live
```

저수준 `create_memory`를 사용하므로 저장 작업과 item ID가 명확합니다.
검색은 실제 Memory API이며, 결과의 `memory_id`가 저장한 ID와 일치해야 합니다.
eventual consistency는 최대 6회/3초 간격으로만 기다립니다.
이 직접 CRUD 경로는 대화에서 자동 기억 추출까지 검증한 것은 아닙니다.

### 3. 격리 검사 읽기

같은 검색을 A scope와 B scope로 실행합니다.
A에는 해당 item이 있고, B는 비어 있어야 합니다. 결과 원문을 각각 보존합니다.
scope는 receipt에서만 가져오며 임의 사용자 입력으로 바꾸지 않습니다.
실제 서비스에서는 인증된 주체로부터 서버가 scope를 결정해야 합니다.

### 4. item 하나만 삭제하고 다시 검색하기

관리자가 **실습 item 삭제를 승인한 경우에만** 실행합니다.
Azure store/RG 삭제와 item 삭제는 별개입니다. 이번 환경에 삭제 금지 정책이 있으면
이 단계는 미실행으로 기록하고 저장·격리 결과만 보고합니다.

```bash
python samples/memory_lab.py forget --confirm 실제-memory-id --live
python samples/memory_lab.py verify --live
```

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

## 정리

기본값은 store 보존입니다. TTL은 item 수명이며 store·trace·conversation 전체 삭제를 뜻하지 않습니다.
보존 정책과 확인 시점을 기록하고, 자원 삭제는 별도 승인을 받습니다.
