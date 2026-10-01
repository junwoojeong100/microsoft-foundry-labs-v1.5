> **이 모듈에서 만드는 것:** 지침 개선과 모델 학습을 구분하고, v1→v2 비교에서 확인한 원인에 맞는 다음 방법을 선택합니다.

## 목표

**새로운 사실은 RAG, 답변 절차와 누락은 지침 개선, 반복적으로 배울 행동은 fine-tuning**부터 검토합니다.
이 실습의 개선 지침은 [v2](../data/prompts/agent-v2.txt) 하나입니다. 수정할 때마다 v3·v4 파일이나 검증 실행 번호를 만들지 않습니다.

## 개념과 실습 지도

**경험할 기능:** 지침 개선, 같은 입력의 비교, 선택적인 Agent Optimizer, SFT 데이터 준비입니다.

**무엇이며 왜 중요한가요?** 지침 개선은 모델이 주어진 정보로 답하는 절차를 바꿉니다. Fine-tuning은 예시로 행동을 학습시킵니다.
둘 다 없는 계약·환율·권한을 사실로 만들어 주지 않습니다.

**어떻게 사용하나요?** L08에서 한 번 비교한 실제 답을 읽고 원인을 분류합니다.
동점이나 하락도 그대로 해석하며, 높은 점수를 얻기 위한 반복 실행은 실습의 목표가 아닙니다.

**어디서 실행하나요?** [지침 비교](../samples/instruction_lab.py), [선택적 Optimizer 코드](../samples/optimizer_lab.py),
[학습 데이터 준비](../samples/prepare_tuning.py)를 사용합니다. 포털은 Optimize/Fine-tune의 입력·제한·결과를 이해할 때 활용합니다.

## 준비

L08의 v1/v2 원문과 고정 체크리스트가 있으면 됩니다. 이미 비교했다면 다시 호출하지 않습니다.
Optimizer와 실제 training job은 별도 승인·지원 모델·권한이 필요하며 기본 코스의 완료 조건이 아닙니다.

## 실행

### 1. 어떤 개선이 필요한지 구분하기

| 관찰한 문제 | 먼저 적용할 방법 |
| --- | --- |
| 새 정책을 모름 | 검색·문서·최신성·접근 범위 확인 |
| 일부 하위 질문이나 근거 누락 | v2의 질문 분리·주장별 근거·최종 확인 절차 |
| 잘못된 도구 입력이나 과도한 실행 | 함수 schema와 서버 권한·수량 검사 |
| 반복되는 형식·스타일 문제 | 충분한 예시를 준비한 뒤 fine-tuning 검토 |

v1을 일부러 약하게 고치거나 질문별 정답을 v2에 붙이지 않습니다. 두 지침에 같은 문맥·모델·질문·기준을 적용합니다.

### 2. 선택: Agent Optimizer의 역할 이해하기

Agent Optimizer는 Limited preview이며, 사용 가능 여부와 모델 지원 범위를 별도로 확인합니다.
기본 실습은 L08의 단일 비교로 충분합니다. Optimizer를 계속 제출하거나 후보를 자동 승격할 필요가 없습니다.

```bash
python samples/optimizer_lab.py --agent ACTUAL_RESPONSES_AGENT --version ACTUAL_NUMERIC_VERSION --optimizer-deployment APPROVED_OPTIMIZER_DEPLOYMENT --prompt-file data/prompts/agent-v2.txt
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `optimizer_lab.py` | 실제 Responses agent/version·reflection 배포·현재 v2 지침의 제출 계획을 확인합니다. placeholder는 본인 환경의 값으로 바꿉니다. | `--live`가 없어 Azure 요청은 없습니다. 과거 배포 번호나 예전 검증을 새 v2의 증거로 사용하지 않습니다. |

</div>

실제 실행을 따로 승인할 때만 배포된 지침과 입력 데이터·평가 기준을 일치시킵니다.
기존 고급 도구의 동결 검사·dev-only 입력·후보 최대 2개·stall 1회·시간 제한·취소·소유 세션 정리 보호는 유지됩니다.
현재 수정본과 일치하지 않는 과거 동결이나 이미 소비한 시험지를 우회해서는 안 됩니다.
서비스의 `succeeded`와 후보 개선은 다릅니다. 누락·오류·실패를 확인하고 개선이 없으면 그대로 기록합니다.
이 고급 경로를 준비하는 작업은 v1→v2 학습 비교의 필수 단계가 아닙니다.

### 3. 로컬 SFT 데이터 형식 익히기

```bash
python samples/prepare_tuning.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `prepare_tuning.py` | 체크인된 합성 예시로 training/validation JSONL을 준비합니다. | 로컬 파일만 만듭니다. Azure 업로드·학습·배포를 실행하지 않습니다. |

</div>

이 예시는 형식을 익히는 작은 seed이지 충분한 학습 효과를 보장하는 데이터가 아닙니다.
평가용 정답이나 holdout을 학습 데이터로 복사하지 않습니다.

### 4. 학습 방식을 선택하기

| 방식 | 데이터 | 주의점 |
| --- | --- | --- |
| SFT | 입력과 바람직한 출력 | 틀린 응답을 모방하지 않기 |
| DPO | 선호 응답과 비선호 응답 | 선호 기준의 일관성 |
| RFT | 문제와 검증 가능한 grader | 보상 편법과 grader 오류 |

![Fine-tuning 화면. 제품 예시와 실제 실습 job을 구분합니다.](../assets/portal/14-fine-tuning.png)

실제 학습은 지원 모델·지역·데이터 처리·비용을 확인하고 별도 승인 후 수행합니다.
학습 job 완료, 모델 배포, 평가 개선은 각각 다른 상태입니다. 자동 배포·승격을 기본값으로 삼지 않습니다.

## 성공 기준

v2의 개선 의도와 실제 답의 차이를 설명하고, 검색·지침·도구 제약·학습 중 적절한 방법을 선택할 수 있습니다.
학습 파일을 만들었다고 모델 학습이나 점수 향상을 완료했다고 쓰지 않습니다.
[현재 비교](../validation/current/report.json)는 국문·영문 모두 실제 측정했지만 v1/v2 점수는 동점입니다. 이번에는 Optimizer job과 holdout을 새로 실행하지 않았습니다. [이전 Optimizer 원본](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/validation/english/automated-v5/optimizer.json)의 실제 실행·실패 판정은 보존하며 현재 비교로 바꾸지 않습니다.

## 막혔을 때

모델 지원 범위, Preview 접근, 실제 배포 지침, dev 입력과 평가 오류를 구분합니다.
조건이 준비되지 않으면 미실행으로 남기고 L08의 한 번 비교만으로 학습을 마칩니다.

## 정리

로컬 데이터 준비만 했다면 cloud job은 없습니다. 별도 승인으로 job을 실행했다면 해당 소유 job·세션의 종료를 확인합니다.
리소스 삭제나 권한 변경은 별도 승인 없이 수행하지 않습니다.
