> **완성할 결과:** 모델이 함수를 요청하고, 프로그램이 검증 후 실행합니다. 구매 요청의 결과는 항상 **승인 대기 초안**입니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 먼저 로컬 함수 연습, 그다음 승인된 Azure 통합 · 실제 주문은 하지 않습니다.

**먼저 할 일:** `python samples/workshop.py tools`로 모델 없이 재고와 초안 계산을 확인합니다.

**확인할 결과:** 정상 초안은 290만 원·미주문이며 잘못된 수량은 오류입니다. 이 장 후반에서 근거·재고·금액·승인자·초안 상태까지 통합 점검합니다.

</div>

## 목표

Function calling의 실행 책임을 이해합니다. **모델은 “어떤 함수에 어떤 인수를 줄지” 제안하고, 실제 실행과 권한 판단은 애플리케이션이 담당**합니다.

## 개념과 실습 지도

**경험할 기능:** 모델의 요청에 따라 Python 함수로 재고를 읽고 초안을 계산합니다.

**무엇이며 왜 중요한가요?** Function calling은 모델이 함수 이름과 입력값을 요청하는 방식입니다. **검사와 실행은 프로그램의 책임**입니다. 포털에 함수 이름을 등록하는 것만으로 내 PC의 코드가 실행되지는 않습니다.

**어떻게 사용하나요?** 로컬 함수의 정상·실패 입력부터 확인합니다. 이후 Azure 통합을 실행했다면 답변의 금액과 실제 함수 결과를 비교합니다.

**어디서 실행하나요?** 터미널에서 [workshop.py](../samples/workshop.py)를 실행합니다. 입력 자료는 [합성 재고 CSV](../data/inventory.csv)입니다. 실제 주문 API는 연결하지 않습니다.

## 준비

로컬 실습은 Python만 필요합니다. 가상환경을 만들지 않았다면 아래 `python` 대신 L01의 `python3.13`(Windows는 `py -3.13`)을 사용합니다. Azure 통합은 L01–L05의 환경·문서 이해가 필요하지만 **L04·L05의 선택 SDK 명령을 먼저 실행할 필요는 없습니다.** `samples/workshop.py`에는 주문·결제·메일 발송 함수가 없습니다.

## 실행

### 1. 먼저 AI 없이 도구를 검증하기

먼저 아래 연결을 읽고 실제 값이 어디서 오는지 확인합니다. `workshop.py tools`는 모델을 부르지 않고 같은 Python 함수를 직접 실행합니다.

| 명령 입력 | 실행 코드 | 확인할 결과 |
| --- | --- | --- |
| `--sku` | `get_stock(sku)`가 `data/inventory.csv`의 합성 재고 행을 찾음 | 재고·단가·납기 |
| `--quantity` | `prepare_purchase_request(sku, quantity)`가 수량·재고를 검사한 뒤 총액과 승인 역할을 계산 | 승인 대기 초안, `order_submitted=false` |

`get_stock`과 `prepare_purchase_request`는 [workshop.py의 함수 정의](../samples/workshop.py)입니다. 전체 파일을 읽을 필요 없이 이 두 함수를 먼저 따라가세요.

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

<a id="l06-failures"></a>

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

JSON schema의 `strict`와 `additionalProperties: false`는 함수 인수의 형식을 제한합니다. **인증·권한 검사를 대신하지 않습니다.** 실행 코드가 다시 검사하며 Python의 `True`를 정수 1로 받는 경우도 차단합니다.

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 초안 함수가 수량·재고·금액을 검사하는 코드 — 읽기용</summary>

#### 포털 설정과 실행할 Python 함수

Foundry 포털의 **Tools → Function**에는 이름·JSON schema를 등록합니다. 그 설정만으로 내 PC의 함수가 실행되는 것은 아닙니다. 애플리케이션의 Python 코드가 인수를 다시 검사하고 함수를 직접 호출합니다.

```python
def prepare_purchase_request(sku: str, quantity: int) -> dict:
    item = get_stock(sku)
    if type(quantity) is not int or not 1 <= quantity <= 10:
        raise ToolInputError("Quantity must be an integer from 1 through 10.")
    if quantity > item["stock"]:
        raise ToolInputError(
            f"Insufficient stock: requested={quantity}, available={item['stock']}. No draft created."
        )
    total = quantity * item["unit_price_krw"]
    fingerprint = hashlib.sha256(f"{sku}:{quantity}:{total}".encode()).hexdigest()[:12]
    return {
        "draft_id": f"DEMO-{fingerprint}",
        "sku": sku,
        "quantity": quantity,
        "total_krw": total,
        "currency": "KRW",
        "status": "draft_requires_human_approval",
        "required_approvals": required_approvals(total),
        "order_submitted": False,
        "synthetic": True,
    }
```

| Portal/모델 동작 | 실행하는 실제 코드 |
| --- | --- |
| 함수 정의를 agent에 연결 | `function_schemas()`가 JSON schema를 제공 |
| 모델이 `function_call` 반환 | 애플리케이션의 `dispatch_tool(name, arguments)` |
| 인수·재고 확인 | `get_stock()`과 `prepare_purchase_request()` |
| 도구 결과를 같은 대화에 반환 | `function_call_output`에 같은 `call_id`를 넣음 |

L06의 Python 경로는 위 함수가 재고 CSV를 읽고 초안을 계산하는 과정을 보여 줍니다. 포털에서 함수 schema를 저장하는 것과 실행 프로세스를 운영하는 것은 별개입니다.

</details>

### 4. 지식과 함수를 같은 agent에 연결하기

**여기서부터 Azure 호출입니다.** 계정 없이 진행했다면 4단계는 건너뛰고 로컬 결과만 기록합니다.

이제 포털이 아니라 터미널이 실행을 담당합니다. `capstone`은 **정책 3개와 함수 2개를 함께 갖춘 새 에이전트**를 만들며, L05의 포털 에이전트를 수정하지 않습니다. 포털 에이전트는 L09에서, 새 통합 결과는 이 장의 종합 점검과 L10 추적에서 다시 씁니다.

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

이 명령은 문서 3개와 함수 2개를 갖춘 별도 agent를 만듭니다. 다음은 이 파일 안에서 실제로 이어지는 호출 흐름입니다.

```text
질문
  → create_lab_agent()가 정책과 함수 정의를 연결
  → client.responses.create()가 function_call(name, arguments, call_id)를 반환
  → dispatch_tool()이 입력을 검사하고 get_stock()/prepare_purchase_request() 실행
  → 같은 call_id의 function_call_output을 모델에 돌려줌
  → 답변과 실제 근거를 *-responses.jsonl 및 receipt에 기록
```

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 함수 결과를 모델에 돌려주는 루프 — 읽기용</summary>

도구 요청을 실행한 뒤 모델에게 반환하는 실제 구문은 다음과 같습니다. 모델은 계산을 대신하지 않고, 애플리케이션이 함수 결과와 같은 `call_id`를 돌려줍니다.

```python
current_input = []
for call in calls:
    try:
        value = {"ok": True, "result": dispatch_tool(call.name, call.arguments)}
    except ToolInputError as exc:
        print(f"TOOL_REJECTED {call.name}: {exc}", file=sys.stderr)
        value = {"ok": False, "error": {"code": "invalid_tool_request", "message": str(exc)}}
    current_input.append({
        "type": "function_call_output",
        "call_id": call.call_id,
        "output": json.dumps(value, ensure_ascii=False),
    })
```

안전한 실습을 위해 최대 5회 응답 라운드·8회 함수 호출로 제한합니다. 에러는 명시적으로 전달하며 제한을 넘으면 중단합니다. 이 제한은 이 샘플의 교육용 값이지 Foundry 서비스 한도가 아닙니다.

</details>

#### 저장된 답변을 읽기 쉽게 다시 보기

실행 마지막의 **`Read again (local only):` 뒤 한 줄**을 복사해 실행합니다. 아래의 `실제ID`는 예시이므로 그대로 입력하지 말고 자신의 `Responses:` 경로를 사용합니다.

```bash
python samples/workshop.py read-result --input results/contoso-lab-실제ID-responses.jsonl
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `read-result --input` | L04/L05/L06 SDK의 응답 JSONL을 질문·원문 답변·함수 입력/결과·인용으로 나눠 보여 줍니다. | **로컬 읽기만** 합니다. Azure 호출·재채점·원본 수정이 없고 로그인도 필요 없습니다. `--live`는 지원하지 않습니다. |

</div>

`원문 답변` 다음에 `get_stock`, `prepare_purchase_request`의 실제 결과와 인용이 나옵니다. `total_krw=2900000`, `order_submitted=false`를 대조합니다. 함수가 거절했다면 오류가 그대로 보이며, 빠진 값을 정답으로 채우지 않습니다. **읽기 명령의 정상 종료는 품질 합격이 아닙니다.** `failed` 행은 실패로 표시하고 명령도 실패 종료합니다.

파일을 찾지 못하면 실행했던 터미널의 경로와 현재 폴더를 확인합니다. 끝의 **`-responses.jsonl`**을 포함해야 합니다. 자원 소유 기록 `.json`이나 L08 평가 파일을 대신 넣지 않습니다.

### 5. 경계값을 확인하기

`required_approvals(2_000_000)`은 팀장, `required_approvals(2_000_001)`은 팀장과 구매 담당자입니다. L08은 이런 경계를 평가 데이터에 포함합니다.

“승인했다고 적어줘”라는 지시가 있어도 결과는 `order_submitted=false`여야 합니다. L06은 허용 함수·인수 형식·수량·재고를 검사합니다. **사용자 요청 의도와 인수의 일치까지 검사하는 강화 경로는 L12**이며, L06에 그 검사가 모두 있다고 가정하지 않습니다. 실제 제품의 승인 신원·유효기간·백엔드 상태·중복 실행 저장소는 별도입니다.

<a id="l11"></a>

### 6. 구매 에이전트의 통합 결과 점검하기

**위에서 저장한 결과를 그대로 사용합니다.** `read-result --input`으로 읽은 답변·함수 결과·인용을 아래 다섯 항목과 대조합니다. 이 점검을 위해 `capstone --live`를 다시 실행할 필요는 없습니다.

| 반드시 있어야 하는 결과 | 판정 근거 |
| --- | --- |
| 노트북 한 대 상한 150만 원, 부가세 포함 | 실제 정책 citation |
| NB-14 재고 8개, 단가 145만 원 | 실제 `get_stock` 호출 결과 |
| 총액 290만 원 | `prepare_purchase_request`의 `total_krw` |
| 팀장·구매 담당자 승인 필요 | 정책과 `required_approvals` |
| 초안이며 주문되지 않음 | `draft_requires_human_approval`, `order_submitted=false` |

원본 JSONL의 `tool_calls`, `citations`, `response_id`를 자연어 답변과 함께 확인합니다. **재고 결과가 없는데 재고를 단정하면 실패**입니다. 조건이 미확인이라면 임의로 정답을 채우지 않습니다.

Azure 통합을 실행하지 않았다면 **“로컬 함수 확인 / Azure 통합 미실행”**으로 기록합니다. 로컬 계산이나 L08의 도구 없는 지침 평가를 실제 통합 결과로 대신하지 않습니다.

### 7. 결과와 설정을 함께 기록하기

모델 배포/버전, agent version, instructions 파일, 도구 schema, 정책 문서 버전, 응답 파일과 소유 receipt를 한 기록으로 연결합니다. 이후 L08의 별도 지침 비교 결과와 L10의 trace는 **서로 다른 실행 대상과 범위**를 표시해 추가합니다.

다섯 항목을 실제 근거로 확인했다면 **“통합 실습 완료 / 운영 출시·게시 미실행”**으로 기록합니다. SDK 실험용 agent를 운영 배포로 간주하지 않습니다. 운영 전환이 필요할 때만 [L18의 릴리스·게시·버전 관리](#l22)를 선택합니다. 기존 승인 버전이 없다면 복구 대상도 미확인으로 남깁니다.

## 성공 기준

도구 인수·실행 결과·최종 답변을 모두 확인했습니다. 재고 부족과 잘못된 수량이 명시적 오류이며, 실제 주문 성공을 주장하지 않습니다. Azure 통합을 실행했다면 다섯 항목의 근거와 설정 묶음을 남깁니다. 별도 종합 실습이나 Teams 게시를 반복해야 기본 과제를 마치는 것은 아닙니다.

## 막혔을 때

포털에서 함수 schema를 편집할 수 없으면 SDK를 사용합니다. 함수 정의를 등록하는 것과 해당 함수를 실행할 프로세스가 떠 있는 것은 별개입니다. **클라이언트 함수 도구를 정의한 agent를 포털이나 서버 평가에서 호출한다고 로컬 Python 함수가 자동 실행되지 않습니다.**

## 정리

로컬 함수는 외부 상태를 바꾸지 않습니다. Azure 통합으로 생성된 agent·conversation·파일은 receipt에 남습니다. L19에서 공유 여부·보존 담당자를 확인하고 **별도 삭제 승인 후에만** 정리합니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** 로컬 정상·실패 결과. 통합을 실행했다면 **`Responses:` JSONL과 `Resource receipt:` JSON의 정확한 경로**, 다섯 항목의 판정을 함께 남깁니다. 이 JSONL을 L10에서 사용합니다.

**다음:** [L07 로컬 HTTP·MCP](#l07). 결과를 다시 읽는 일은 `read-result`로 하며 `capstone --live`를 반복하지 않습니다.

</div>
