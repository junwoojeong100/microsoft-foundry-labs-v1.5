> **완성할 결과:** 모델이 함수를 요청하고, 프로그램이 검증 후 실행합니다. 구매 요청의 결과는 항상 **승인 대기 초안**입니다.

## 목표

Function calling의 실행 책임을 이해합니다. **모델은 “어떤 함수에 어떤 인수를 줄지” 제안하고, 실제 실행과 권한 판단은 애플리케이션이 담당**합니다.

## 준비

로컬 실습은 Python만 필요합니다. Azure 통합은 L01–L05 준비가 필요합니다. `samples/workshop.py`에는 주문·결제·메일 발송 함수가 없습니다.

## 실행

### 1. 먼저 AI 없이 도구를 검증하기

```bash
python samples/workshop.py tools
```

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
