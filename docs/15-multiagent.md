> **완성할 결과:** 초안 작성자와 검토자가 역할을 나누되, 실제 승인은 모델이 대신하지 않는 2단계 흐름.

## 목표

**에이전트 수를 늘리는 것이 목적이 아닙니다.** 역할·도구·평가 기준이 실제로 분리될 때만 orchestration을 추가합니다.

**중요:** Foundry 포털 Workflows는 Preview이며 **2026-12-01 종료 예정**입니다. 이 모듈은 **Microsoft Agent Framework**로 새 구현을 진행합니다.

## 준비

L01의 프로젝트·모델·`.env`, 별도 Python 환경이 필요합니다. 기본 코스의 환경을 그대로 덮어쓰지 마세요.

2026-09-29 확인 기준 `agent-framework-foundry==1.13.1`은 `azure-ai-projects<2.7.0`을 요구합니다. 기본 코스는 2.7.0입니다. **각각 호환되는 환경을 분리**했습니다.

## 실행

### 1. 로컬 계획 확인하기

```bash
python samples/multi_agent.py
```

`drafter → reviewer` 계획만 출력하며 Azure를 호출하지 않습니다.

### 2. 심화 환경 설치하기

```bash
python3 -m venv .venv-advanced
.venv-advanced/bin/python -m pip install -r requirements-advanced.txt
.venv-advanced/bin/python -m pip check
```

Windows는 `.venv-advanced\Scripts\python.exe`를 사용합니다. 관리 정책에 맞는 패키지 저장소를 이용하세요.

### 3. 실제 두 agent 실행하기

```bash
.venv-advanced/bin/python samples/multi_agent.py --live
```

이 예제는 로컬에서 Microsoft Agent Framework를 실행하고 Foundry 모델을 호출합니다. **Hosted Agent를 배포하는 명령이 아닙니다.** 두 역할에는 동일한 합성 정책을 명시적으로 제공하며, 검색 품질을 평가하는 RAG 예제도 아닙니다.

| 역할 | 입력 | 결과 | 금지 |
| --- | --- | --- | --- |
| drafter | 요청과 정책 | 구매 안내 초안 | 사실 없는 주문 완료 |
| reviewer | 초안과 정책 | 경계값·승인 규칙 검토 후 최종 안내 | 실제 업무 승인 |

핵심 흐름은 다음과 같습니다.

```python
workflow = WorkflowBuilder(
    start_executor=drafter,
    output_from=[reviewer],
    max_iterations=4,
).add_edge(drafter, reviewer).build()
```

### 4. 단일 agent와 비교하기

같은 질문의 정확도·토큰·전체 지연을 기록합니다. 두 agent 결과가 더 길기만 하다면 단일 agent로 돌아갑니다. Reviewer라는 이름만으로 독립 검증이나 보안 경계가 생기지 않습니다.

<details markdown="1">
<summary>다른 orchestration 패턴 선택 기준</summary>

| 패턴 | 선택할 상황 | 비용/실패 주의 |
| --- | --- | --- |
| Sequential | 전 단계 결과를 다음 단계가 검토 | 전체 지연 누적 |
| Concurrent | 독립적인 조사·평가 | 병렬 토큰 비용·결과 충돌 |
| Handoff | 전문 담당자로 대화 제어 이전 | 권한·히스토리 범위 |
| Group/Magentic | 계획·역할 조정이 필요한 복합 업무 | 반복 제한·중단 조건 |
| 명시적 workflow graph | 조건 분기·체크포인트·사람 입력 | 실패/재개 상태의 관리 |

</details>

### 5. A2A와 사람 승인 설계하기

A2A는 다른 서비스·벤더의 agent를 호출하는 통합입니다. 먼저 테스트 agent의 agent card/skill 계약, 호출 identity, timeout, 재시도, 전달할 최소 데이터, 반환 schema를 합의합니다.

승인 단계에서는 **“승인합니다”라는 모델 문장** 대신 실제 승인 요청 ID와 사람의 결정을 저장하고, 승인된 내용이 변경되지 않았는지 검증합니다. L06 샘플에는 실제 업무 실행이 없으므로 승인 프로세스를 완료한 것으로 가장하지 않습니다.

## 성공 기준

두 단계가 실제로 실행되고 최종 출력이 reviewer의 결과임을 확인했습니다. 단일 agent 대비 추가 비용이 정당한지 설명할 수 있습니다. A2A/HITL를 설계만 했다면 실행 완료와 구분합니다.

## 막혔을 때

SDK import 오류는 환경 혼용부터 확인합니다. 이 샘플은 core `WorkflowBuilder`를 사용하며 별도의 `agent-framework-orchestrations` 패키지를 요구하지 않습니다. 문서의 다른 `SequentialBuilder` 예제에는 추가 패키지가 필요할 수 있습니다.

## 정리

모델 호출 비용을 기록합니다. 운영에 옮길 때는 L14의 hosted runtime과 L22의 릴리스 게이트를 사용합니다.
