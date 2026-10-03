> **완성할 결과:** 가상 영수증에서 구조화된 값을 추출하고, 지출 CSV를 계산하여 원본과 대조합니다.

## 목표

**Vision 모델의 설명, OCR/layout, Content Understanding의 schema 추출, Code Interpreter의 계산**을 목적에 맞게 구분합니다.

## 개념과 실습 지도

**경험할 기능:** 이미지/문서 이해, schema 기반 필드 추출, Code Interpreter의 CSV 계산입니다.

**무엇이며 왜 중요한가요?** Vision은 이미지 내용을 설명하고, OCR/layout은 글자와 위치를 추출하며, Content Understanding은 원하는 필드의 구조로 문서를 해석합니다. Code Interpreter는 제공한 데이터를 코드로 계산하는 별도 도구입니다. 영수증 총액을 자연어로 읽는 것과 각 행을 합산해 검증하는 것은 다르므로, 업무에서는 출력 형식과 원본 대조를 함께 설계해야 합니다.

**어떻게 사용하나요?** 동일한 합성 영수증을 자유 설명과 구조화 추출로 각각 처리해 빠진 값·추측·근거를 비교합니다. 이어 CSV의 9개 행을 계산하고 알려진 월별/전체 합계와 대조합니다. 보기 좋은 JSON이나 그래프보다 실제 값과 원본 행 수가 맞는지가 중요합니다.

**어디서 실행하나요?** [receipt.html](../data/receipt.html)을 브라우저에서 열고 [정답 파일](../data/receipt.expected.json), [지출 CSV](../data/monthly-spend.csv)를 함께 봅니다. 추론·analyzer·Code Interpreter는 각각 지원 포털/서비스와 비용 승인이 필요하며, 파일을 열어 보는 단계만으로 서비스 실행 완료가 되지는 않습니다.

## 준비

`data/receipt.html`, `receipt.expected.json`, `monthly-spend.csv`를 사용합니다. 실제 영수증·계좌·신분증은 필요 없습니다. Content Understanding에는 해당 서비스·모델 배포·권한과 비용 승인이 추가로 필요합니다.

| 경로 | 실행 전에 준비할 것 | 남길 결과 |
| --- | --- | --- |
| Vision | 이미지 입력을 지원하는 승인된 배포와 읽을 수 있는 PNG | 원본 이미지와 추출 답변 |
| Content Understanding | 관리자 제공 Foundry 리소스와 analyzer용 기본 모델 연결 | 필드별 값·원본 위치·제공되는 confidence/warning |
| Code Interpreter | 해당 도구를 지원하는 agent와 파일 업로드 권한 | 실제 실행 기록·9행 집계·열리는 차트 파일 |

세 경로의 실행 여부를 따로 기록합니다. 조건이 없는 경로는 아래 예제로 판독을 연습하되 **서비스 미실행**으로 남깁니다. 모델 답변만으로 analyzer나 코드 실행까지 완료한 것으로 합산하지 않습니다.

## 실행

### 1. 합성 영수증 준비하기

`data/receipt.html`을 브라우저로 열어 **인쇄 → PDF 저장**합니다. 문서 번호·품목 행·합계·승인 대기가 잘리지 않았는지 저장한 파일을 다시 엽니다. 이 PDF는 CU 입력입니다. Vision용으로는 같은 문서 영역을 캡처하거나 뷰어에서 PNG로 내보내고 글자가 읽히는지 확인합니다. 이미지 전용 입력에 PDF를 넣지 않습니다. 파일은 합성 데이터이며 실제 거래 효력이 없습니다.

### 2. Vision과 구조화 추출을 비교하기

L03의 모델 Playground에서 이미지 입력을 지원하는 **자신의 배포**를 선택합니다. 첨부 입력에 준비한 PNG를 넣고 미리보기를 확인한 뒤 아래 질문을 한 번 전송합니다. 파일 첨부가 없거나 형식이 거절되면 모델·입력 지원부터 확인하며 `.env`의 기본 모델을 무작정 변경하지 않습니다.

```text
이 합성 영수증의 문서 번호, 날짜, 통화, 품목, 수량, 단가, 총액,
구매 승인 상태를 정리해줘. 보이지 않는 값은 null로 두고 추측하지 마.
```

정답은 문서 `CONTOSO-2026-0929`, 날짜 `2026-09-29`, 수량 2, 단가 89,000원, 합계 178,000원, **승인 대기**입니다. 인쇄된 문서를 이해했다고 실제 구매를 승인한 것은 아닙니다.

### 3. Content Understanding analyzer로 같은 문서 처리하기

[Content Understanding Studio quickstart](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/content-understanding-studio)의 진입점으로 이동합니다. **Settings에서 관리자 제공 리소스와 기본 모델 연결을 먼저 확인**합니다. 자동 모델 배포 옵션이 보이면 승인 없이 켜지 않습니다. 기존 L02 모델 하나만으로 모든 analyzer 조건이 충족된다고 가정하지 마세요.

[Custom analyzer 절차](https://learn.microsoft.com/azure/ai-services/content-understanding/how-to/customize-analyzer-content-understanding-studio)를 다음 순서로 적용합니다. Studio project는 L01의 Foundry project와 같은 객체가 아닙니다.

1. **Create project → Extract content and fields with a custom schema**를 선택하고 실습용 이름을 붙입니다. 관리자 제공 analyzer를 쓰는 경우에는 그 analyzer의 schema부터 확인합니다.
2. 저장한 합성 PDF를 올리고 문서/영수증에 맞는 템플릿을 고릅니다. 아래 필드와 설명을 검토하고 **Save**합니다. 제안된 필드를 전부 받아들이지 않습니다.
3. **Run analysis**를 한 번 실행합니다. 원문 문서와 결과를 나란히 열고 필드별 값·근거 위치를 대조합니다. schema만 저장한 상태는 분석 성공이 아닙니다.
4. 재사용할 analyzer가 필요한 경우에만 **Build analyzer**로 생성하고 이름·리소스·API 버전을 기록합니다. 화면의 키나 자동 생성 코드를 공유하지 않습니다.

| 필드 | 타입 | 확인 |
| --- | --- | --- |
| document_id | string | CONTOSO-2026-0929 |
| date | date/string | 2026-09-29 |
| currency | string | KRW |
| quantity | integer | 2 |
| unit_price | number | 89000 |
| total | number | 178000 |
| approval_status | string | 문서의 “승인 대기”를 `pending`으로 정규화; 실제 승인 수행 금지 |

생산용 기본 API는 **`2025-11-01` GA**를 기준으로 검토합니다. **`2026-06-01-preview`**의 agentic mode, 일부 classification/metadata/signature 기능은 별도 실험입니다. 2026년 9월 CU Toolkit/CU CLI도 Preview입니다.

이 단일 품목 예제의 `quantity`·`unit_price`는 정답 파일의 `items[0]`과 대조합니다. 여러 품목 문서라면 한 값을 대표값으로 쓰지 말고 배열 schema를 설계해야 합니다.

| 확인할 것 | 어떻게 판단하나요? | 실패하면 다음 행동 |
| --- | --- | --- |
| `total`과 문서 합계 위치 | 178,000이며 수량 2 × 단가 89,000과 같음 | 금액 행이 잘렸는지, 단가를 총액으로 읽었는지 먼저 확인 |
| `approval_status`와 원문 | 승인 대기이지 승인 완료가 아님 | 필드 설명의 추출/정규화 규칙을 확인. 정답 숫자를 넣어 결과를 보충하지 않음 |
| confidence·source grounding·warnings | 제공된 근거가 해당 필드를 지지함 | 값이 틀리면 높은 confidence라도 실패. 미제공 confidence는 0이 아니라 미제공으로 기록 |
| null 또는 필드 누락 | 원문에 없으면 유보, 보이는데 빠졌으면 추출 실패 | 원문 가독성 → 필드 이름/타입/설명 → analyzer 설정 순으로 확인 |

단순 OCR·layout만 필요하다면 Document Intelligence와 비교합니다. 이번 한 문서에서 맞았다는 사실은 다른 양식이나 실제 업무 승인에 대한 품질 보장이 아닙니다.

### 4. Code Interpreter로 숫자 분석하기

실습용 agent의 **Tools**에서 Code Interpreter 또는 이를 담은 Toolbox를 연결하고 버전을 저장합니다. 기존 File search에 CSV를 올리는 것과 다릅니다. 새 대화의 파일 입력에서 `monthly-spend.csv`를 첨부하고 파일 이름을 확인합니다. 이 UI가 제공되지 않으면 [공식 Code Interpreter 문서](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/code-interpreter)의 지원 경로를 관리자와 확인하며, 샘플 끝의 삭제 코드를 승인 없이 실행하지 않습니다.

```text
CSV의 월별 지출 합계를 계산하고 막대그래프를 만들어줘.
원본 행 수, 월별 합계, 전체 합계를 함께 제시해줘.
CSV에 없는 데이터는 추가하지 마.
```

대조할 정답:

| 월 | 합계(KRW) |
| --- | ---: |
| 2026-07 | 3,718,000 |
| 2026-08 | 2,677,000 |
| 2026-09 | 4,759,000 |
| 전체 | 11,154,000 |

응답의 도구 실행 상세에서 CSV 읽기와 집계 코드를 확인합니다. 헤더를 제외한 **9행**, 월별 3개 그룹, 전체 합계가 모두 맞아야 합니다. 직접 도구라면 Code Interpreter 실행 항목, Toolbox 경로라면 실제 도구 결과를 확인합니다. “Python으로 계산했습니다”라는 문장만으로는 부족합니다.

차트 링크를 내려받아 열고 축의 월·KRW 단위가 표와 같은지 봅니다. 합계가 틀리면 CSV의 열 이름·숫자 파싱·누락/중복 행을, 파일 링크가 안 열리면 생성 파일 식별자와 세션 수명을 먼저 확인합니다. 코드 실행 기록이 없으면 Code Interpreter 실습은 미확인입니다. 추가 세션에는 모델 토큰 외 비용이 있을 수 있습니다.

### 5. 이미지·비디오·브라우저 도구는 구분해서 추가하기

| 기능 | 선택 과제 | 경계 |
| --- | --- | --- |
| Image generation | 저작권 문제가 없는 가상 제품의 설명 이미지 | 모델/도구별 상태 확인; 사실 증거로 쓰지 않음 |
| Video playground / 영상 이해 | 합성 짧은 장면의 시간대별 요약 | 생성·이해는 별개, Preview 여부 확인 |
| Web search / Bing grounding | 공개 제품 사양을 날짜·출처와 비교 | 외부 데이터 전송·검색 약관 확인 |
| Browser automation / Computer use | 승인된 테스트 화면의 읽기 작업 | Preview, 자격 증명·구매·전송·운영 UI 제외 |

메뉴에 있는 모든 도구를 동시에 켜는 과제가 아닙니다. 필요한 도구 한 개와 실패 시나리오 한 개를 정하고 선택적으로 진행합니다.

## 성공 기준

원본과 추출 필드가 맞고, 합성 CSV 합계가 표와 일치합니다. confidence·warning·source 위치를 함께 기록합니다. 실행하지 않은 선택 도구는 설계/참고로 표시합니다.

## 막혔을 때

지원 파일 형식·이미지 해상도·analyzer 모델 배포·역할·지역·API 버전을 확인합니다. JSON 형태가 맞아도 값이 틀리면 실패입니다.

## 정리

업로드 파일·생성 파일·샌드박스 세션·analyzer와 추가 모델 배포의 유지 필요성을 확인합니다.
