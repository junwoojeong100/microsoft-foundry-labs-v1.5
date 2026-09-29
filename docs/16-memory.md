> **완성할 결과:** 가상 사용자의 답변 형식 선호를 새 대화에서 기억하고, 삭제 후에는 기억하지 않는 것을 확인합니다.

## 목표

**Conversation은 현재 대화, Memory는 대화 사이의 지속 맥락, IQ는 관리된 조직 지식**입니다. Memory는 Preview입니다.

## 준비

Memory 지원 지역의 비운영 프로젝트, 호환 chat·embedding 배포, 관리 ID 권한과 Preview 허용이 필요합니다. **Memory store의 VNet 통합은 현재 지원되지 않습니다.** 이를 필수 private 환경에서 임의로 켜지 않습니다.

가상 사용자 `lab-user-a`, `lab-user-b`만 사용합니다. 실제 개인정보나 비밀번호, 직원 인사 정보를 넣지 않습니다.

## 실행

### 1. 현재 공식 SDK 예제 준비하기

[Create and use memory](https://learn.microsoft.com/azure/foundry/agents/how-to/memory-usage)의 Python 탭에서 **memory store 생성 + memory search tool 연결** 전체 예제를 별도 실습 파일로 준비합니다.

변경할 값은 아래에 제한합니다.

| 설정 | 값 |
| --- | --- |
| project endpoint | 자신의 비운영 프로젝트 |
| chat / embedding deployment | 지원되는 자신의 배포 이름 |
| store name | 다른 실습과 겹치지 않는 이름 |
| scope | 가상 사용자 A/B별 고유 값 |
| default TTL | 학습용으로 짧은 보존 시간, 예: 3,600초 |
| 추출 대상 | 비민감 답변 형식 선호만 |

Preview API/옵션은 변경될 수 있으므로 SDK 버전과 해당 문서의 옵션을 함께 확인합니다. 기본 TTL·기억 유형 중 생성 시에만 설정 가능한 옵션도 있습니다.

### 2. 기억시키고 새 대화에서 확인하기

사용자 A의 scope로 다음 입력을 보냅니다.

```text
이 실습에서는 답변을 표 형식으로 받는 것을 선호해요.
이 비민감 설정만 기억해줘.
```

설정된 업데이트 지연을 기다리거나, 지원되는 명시적 remember 경로를 사용합니다. **새 conversation**을 만들고 “노트북과 모니터 규정을 비교해줘”라고 요청합니다. 저장 item과 실제 검색 결과를 함께 확인하세요.

### 3. 다른 사용자에게 새지 않는지 확인하기

사용자 B의 별도 scope에서 같은 질문을 보냅니다. A의 기억 item이 반환되지 않아야 합니다. 우연히 표 형식으로 답했다는 사실만으로 기억이 공유됐다고 단정하지 말고 **memory retrieval 결과**를 확인합니다.

scope를 클라이언트 입력만으로 신뢰하지 않습니다. 실제 제품에서는 인증된 주체로부터 서버에서 scope를 결정합니다. 저수준 API는 scope를 명시하고, 도구의 `{{$userId}}` 자동 매핑은 해당 경로의 지원 조건을 따릅니다.

### 4. 기억을 삭제하고 재확인하기

지원되는 forget 명령 또는 item 삭제 API로 해당 선호를 제거합니다. 새로운 conversation에서 memory search를 다시 수행하여 삭제된 item이 반환되지 않는지 봅니다.

“잊었어요”라는 자연어 답변만으로 삭제 성공을 인정하지 않습니다. 기존 conversation 본문·trace에 같은 내용이 남는 문제와 memory item 삭제는 서로 다릅니다.

## 성공 기준

A scope의 item 생성·검색, B scope의 격리, item 삭제 후 새 검색 결과를 확인했습니다. TTL과 사용자별 삭제 경로를 설명할 수 있습니다.

## 막혔을 때

새 conversation인지, 같은 scope인지, 모델/embedding 지원과 업데이트 지연을 확인합니다. preview 접근이나 네트워크 제약이 있으면 **메모리 수명주기 설계 과제**로 대체하고 클라우드 미실행으로 기록합니다.

## 정리

실습 memory item·store를 명시적으로 삭제합니다. 모델/embedding 배포의 수명주기는 별도로 처리합니다.
