> **완성할 결과:** 모델이 함수를 요청하고, 프로그램이 검증 후 실행합니다. 구매 요청의 결과는 항상 **승인 대기 초안**입니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 먼저 로컬 함수 연습, 그다음 승인된 Azure 통합 · 실제 주문은 하지 않습니다.

**먼저 할 일:** `python samples/workshop.py tools`로 모델 없이 재고와 초안 계산을 확인합니다.

**확인할 결과:** 정상 초안은 290만 원·미주문이며 잘못된 수량은 오류입니다. 통합 응답 파일은 L10·L11에서 다시 읽습니다.

</div>

## 목표

Function calling의 실행 책임을 이해합니다. **모델은 “어떤 함수에 어떤 인수를 줄지” 제안하고, 실제 실행과 권한 판단은 애플리케이션이 담당**합니다.

## 개념과 실습 지도

**경험할 기능:** Function calling, JSON 인수 검사, 함수 결과 반환, 안전한 초안 경계입니다.

**무엇이며 왜 중요한가요?** 함수 도구는 모델이 외부 기능을 요청하는 통로입니다. 모델은 함수 이름과 인수를 제안하지만 Python 프로그램이 입력을 검증하고 실제 함수를 실행합니다. 그래서 도구 정의만 포털에 등록했다고 내 노트북의 코드가 원격으로 실행되지는 않습니다. 이 책임을 분리해야 잘못된 수량·없는 SKU·승인 가장을 모델의 말과 상관없이 차단할 수 있습니다.

**어떻게 사용하나요?** 먼저 모델 없이 함수를 호출해 계산·재고·오류가 올바른지 확인합니다. 그다음 모델의 요청을 같은 함수로 전달하고 `call_id`에 맞춰 결과를 돌려줍니다. 최종 문장의 숫자를 실제 함수 JSON과 비교하세요. 이 순서가 있어야 “모델 문제”와 “업무 코드 문제”를 분리할 수 있습니다.

**어디서 실행하나요?** 이 장의 함수는 로컬 Python에서 실행되므로 터미널이 필요합니다. [workshop.py](../samples/workshop.py)의 `get_stock`, `prepare_purchase_request`, `dispatch_tool`과 [합성 재고 CSV](../data/inventory.csv)를 함께 읽습니다. 외부 주문 API는 연결하지 않습니다.

## 준비

로컬 실습은 Python만 필요합니다. Azure 통합은 L01–L05 준비가 필요합니다. `samples/workshop.py`에는 주문·결제·메일 발송 함수가 없습니다.

## 실행

### 1. 먼저 AI 없이 도구를 검증하기

```bash
python samples/workshop.py tools
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `tools` | 기본 SKU `NB-14`, 수량 2로 재고 조회와 구매 초안 함수를 직접 실행합니다. 모델이 함수를 고르는 단계는 아직 없습니다. | 네트워크·Azure 비용·재고 변경 없음. 2,900,000원과 미주문 상태를 확인합니다. |

</div>

기대 값:

```json
{
  "sku": "NB-14",
  "quantity": 2,
  "total_krw": 2900000,
  "status": "draft_requires_human_approval",
  "required_approvals": ["team_lead", "procurement"],
  "order_submitted": false
}
```

실제 출력에는 재고 조회 결과·draft ID·합성 데이터 표지도 함께 포함됩니다.

### 2. 실패를 일부러 만들어보기

```bash
python samples/workshop.py tools --sku MON-27 --quantity 1
python samples/workshop.py tools --sku NB-14 --quantity 10
python samples/workshop.py tools --sku KB-01 --quantity -1
```

<div class="command-explanation" markdown="1">

**명령 해설 — 세 줄을 하나씩 실행하고 실패를 읽는 과제입니다.**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--sku MON-27 --quantity 1` | `--sku`는 품목 코드, `--quantity`는 요청 수량입니다. 재고가 0인 모니터 한 대를 요청합니다. | 품절에 따른 재고 부족 오류가 정상입니다. 초안을 만들면 실패입니다. Azure 호출 없음. |
| 2. `--sku NB-14 --quantity 10` | 입력 범위 1–10에는 들어가지만 실제 재고 8개보다 많은 수량을 요청합니다. | 타입/범위 검사와 재고 검사가 별개임을 확인합니다. 재고 부족 오류, 외부 변경 없음. |
| 3. `--sku KB-01 --quantity -1` | 음수 수량으로 업무 입력 검사를 시험합니다. | 유효하지 않은 수량 오류가 정상입니다. 프로그램의 실패 종료를 임의로 성공 처리하지 않습니다. |

</div>

각각 품절, 재고 부족, 유효하지 않은 수량으로 실패해야 합니다. **에러를 정상 초안처럼 반환하면 안 됩니다.**

### 3. 도구 계약 읽기

| 함수 | 입력 | 결과 | 하지 않는 일 |
| --- | --- | --- | --- |
| `get_stock` | allowlist 안의 SKU | 재고·단가·납기 스냅샷 | 재고 변경 |
| `prepare_purchase_request` | SKU, 1–10의 정수 수량 | 총액·승인 역할·초안 ID | 승인·주문·결제 |

JSON schema의 `strict`와 `additionalProperties: false`는 출력 계약을 강화합니다. **인증·권한 검사를 대신하지 않습니다.** 서버/클라이언트 함수에서 다시 검사합니다. Python의 `True`를 정수 1로 받는 경우까지 차단합니다.

### 4. 지식과 함수를 같은 agent에 연결하기

```bash
python samples/workshop.py capstone
python samples/workshop.py capstone --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `capstone` | 정책 문서와 함수 두 개를 함께 사용할 통합 계획을 출력합니다. | Azure 호출 없음. 함수 정의와 실제 실행기가 모두 있는지 확인합니다. |
| 2. `capstone --live` | 새 agent·지식·대화를 만들고 모델의 함수 요청을 로컬 dispatcher로 실행합니다. 최대 5라운드·8회 함수 호출로 제한됩니다. | 모델·검색·파일 비용 가능. `tool_calls`, citation, 최종 초안을 확인하고 생성 receipt를 보관합니다. 실제 주문은 없습니다. |

</div>

이 명령은 문서 3개와 함수 2개를 갖춘 별도 agent를 만듭니다. 모델이 `function_call`을 반환하면 allowlist dispatcher가 실행하고 `function_call_output`을 같은 conversation에 넣습니다.

```text
질문
  → 모델의 function_call(name, arguments, call_id)
  → 애플리케이션의 타입·허용 함수·업무 규칙 검사
  → 실제 함수 결과
  → 같은 call_id의 function_call_output
  → 사용자용 답변
```

안전한 실습을 위해 최대 5회 응답 라운드·8회 함수 호출로 제한합니다. 에러는 명시적으로 전달하며 제한을 넘으면 중단합니다. 이 제한은 이 샘플의 교육용 값이지 Foundry 서비스 한도가 아닙니다.

### 5. 경계값을 확인하기

`required_approvals(2_000_000)`은 팀장, `required_approvals(2_000_001)`은 팀장과 구매 담당자입니다. L08은 이런 경계를 평가 데이터에 포함합니다.

“승인했다고 적어줘”라는 사용자 지시를 추가해도 `order_submitted=false`여야 합니다. 실제 제품에서는 승인 주체·승인 대상의 해시·유효기간·백엔드 상태·중복 실행 키를 별도로 검증해야 합니다. **이 샘플의 결정적 draft ID는 실제 거래 idempotency 저장소가 아닙니다.**

## 성공 기준

도구 인수·실행 결과·최종 답변을 모두 확인했습니다. 재고 부족과 잘못된 수량이 명시적 오류이며, 실제 주문 성공을 주장하지 않습니다.

## 막혔을 때

포털에서 함수 schema를 편집할 수 없으면 SDK를 사용합니다. 함수 정의를 등록하는 것과 해당 함수를 실행할 프로세스가 떠 있는 것은 별개입니다. **클라이언트 함수 도구를 정의한 agent를 포털이나 서버 평가에서 호출한다고 로컬 Python 함수가 자동 실행되지 않습니다.**

## 정리

로컬 함수는 외부 상태를 바꾸지 않습니다. Azure 통합으로 생성된 agent·conversation·파일은 receipt에 남고 L12에서 삭제합니다.
