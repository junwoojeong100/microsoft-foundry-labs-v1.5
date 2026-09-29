> **완성할 결과:** 지식·도구·품질·추적을 연결한 도우미와, 검증한 버전을 배포하는 절차.

## 목표

“데모에서 답했다”를 넘어 **사용자에게 제공할 버전을 선택하고, 실패하면 되돌리는 방법**을 확보합니다.

## 준비

L05–L10 결과가 필요합니다. Teams/Microsoft Copilot 실제 게시에는 별도의 publish 권한·Bot Service 자원 생성 권한·조직 정책 확인이 필요합니다. **게시하지 않아도 로컬/Foundry 통합 결과까지 기본 코스를 완료할 수 있습니다.**

## 실행

### 1. 최종 사용자 과제 수행하기

```bash
python samples/workshop.py capstone --live
```

질문: “노트북 2대의 구매 규정과 NB-14 재고를 확인하고 구매 요청 초안을 만들어줘.”

| 반드시 있어야 하는 결과 | 판정 근거 |
| --- | --- |
| 노트북 한 대 상한 150만 원, 부가세 포함 | 실제 정책 citation |
| NB-14 재고 8개, 단가 145만 원 | 실제 `get_stock` 호출 결과 |
| 총액 290만 원 | 도구 계산 결과 |
| 팀장·구매 담당자 승인 필요 | 정책과 `required_approvals` |
| 초안이며 주문되지 않음 | `draft_requires_human_approval`, `order_submitted=false` |

자연어 답변뿐 아니라 JSONL의 `tool_calls`, `citations`, `response_id`를 확인합니다. 재고 결과가 없는데 재고를 단정하면 실패입니다.

### 2. 릴리스 묶음 기록하기

모델 배포/버전, agent version, instructions 파일, 도구 schema, 정책 문서 버전, 평가 데이터 버전, 평가 결과를 하나의 기록으로 묶습니다. 이 가이드의 생성 SDK agent는 독립된 실험용이므로 **그대로 운영 배포로 간주하지 않습니다.**

### 3. 안정된 endpoint와 active version 선택하기

포털 agent의 **Details → Agent configuration → Active version**에서 특정 버전을 선택하는 흐름을 확인합니다. `Always use latest`는 새 버전이 자동으로 사용자에게 나갈 수 있으므로 실제 운영 정책 없이 선택하지 않습니다.

새 버전을 시험하고 이전 버전으로 다시 선택해 동일 질문을 보내 봅니다. URL이 유지되어도 행동과 버전은 바뀔 수 있습니다.

### 4. 조건부: Teams/Microsoft Copilot 게시하기

실제 함수가 필요한 agent는 먼저 **Hosted Agent 또는 서버에서 실행 가능한 도구**로 전환합니다. L06의 로컬 Python 프로세스는 Teams 사용자의 요청을 자동으로 실행해 주지 않습니다.

관리자는 다음을 확인합니다.

| 영역 | 확인 |
| --- | --- |
| Foundry | 실제 publishing 작업에 필요한 프로젝트/리소스 역할 |
| Bot Service | `botServices/write`, `channels/write` 등 별도 권한 |
| 조직 | 앱 허용 정책·사용 범위·관리자 승인 |
| 데이터 | M365/Teams로 흐르는 게시 metadata와 응답의 처리 조건 |
| 네트워크 | private 프로젝트의 별도 게시 경로 |

포털의 **Publish → Teams and Microsoft Copilot**에서 이름·설명·게시 버전을 입력합니다. 먼저 **Just you** 범위로 테스트합니다. **People in your organization**은 조직 관리자 승인과 정책에 따른 별도 배포입니다.

현재 공개 문서에서 `Foundry User`의 project 작업 권한과 publish용 관리 권한이 페이지에 따라 다르게 설명됩니다. 단순 역할 이름 하나만으로 충분하다고 가정하지 말고 **실행할 publishing 동작의 요구 permission과 Bot Service 권한을 모두 사전 확인**하세요.

public network access가 꺼진 프로젝트는 일반 포털 게시 흐름이 지원되지 않을 수 있습니다. 공식 REST 경로의 별도 Activity route와 인증 조건을 사용해야 합니다. private 설정을 끄는 것으로 우회하지 않습니다.

### 5. 사용자와 운영 관점으로 재확인하기

허용 사용자 1명·허용되지 않은 사용자 1명으로 접근을 구분합니다. 게시 성공, discoverability, 호출 권한, 도구 실행 성공은 서로 다른 검사입니다. 게시 완료 문구만으로 종료하지 않습니다.

## 성공 기준

최종 결과의 다섯 항목을 확인했고, release record와 rollback 대상 버전이 있습니다. 게시를 하지 않았다면 “게시 준비 완료 / 실제 게시 미실행”으로 구분해 기록합니다.

## 막혔을 때

Teams에 보이지만 응답하지 않으면 Bot 채널, agent endpoint 인증, active version, 서버 도구 실행 환경을 확인합니다. 앱이 보이지 않으면 게시 범위와 관리자 승인부터 봅니다.

## 정리

실험용 게시와 연결은 관리자 정책에 따라 회수합니다. 자원을 만든 모든 학습자는 **L12를 반드시 진행**합니다.
