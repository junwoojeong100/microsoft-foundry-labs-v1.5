> **완성할 결과:** 가상 영수증에서 구조화된 값을 추출하고, 지출 CSV를 계산하여 원본과 대조합니다.

## 목표

**Vision 모델의 설명, OCR/layout, Content Understanding의 schema 추출, Code Interpreter의 계산**을 목적에 맞게 구분합니다.

## 준비

`data/receipt.html`, `receipt.expected.json`, `monthly-spend.csv`를 사용합니다. 실제 영수증·계좌·신분증은 필요 없습니다. Content Understanding에는 해당 서비스·모델 배포·권한과 비용 승인이 추가로 필요합니다.

## 실행

### 1. 합성 영수증 준비하기

`data/receipt.html`을 브라우저로 열어 **인쇄 → PDF 저장**합니다. 파일은 실습용 합성 데이터임을 표시하며 실제 거래 효력이 없습니다.

### 2. Vision과 구조화 추출을 비교하기

지원되는 이미지 입력 모델에 영수증 이미지를 넣고 다음을 요청합니다.

```text
이 합성 영수증의 문서 번호, 날짜, 통화, 품목, 수량, 단가, 총액,
구매 승인 상태를 정리해줘. 보이지 않는 값은 null로 두고 추측하지 마.
```

정답은 문서 `CONTOSO-2026-0929`, 날짜 `2026-09-29`, 수량 2, 단가 89,000원, 합계 178,000원, **승인 대기**입니다. 인쇄된 문서를 이해했다고 실제 구매를 승인한 것은 아닙니다.

### 3. Content Understanding analyzer로 같은 문서 처리하기

[Content Understanding Studio quickstart](https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/content-understanding-studio)의 현재 진입점을 사용합니다. 새 Foundry 포털의 GA 목록에서 Content Understanding은 별도 경험이 필요한 항목이므로, 화면에 없다고 다른 기능으로 대체하지 않습니다.

지원되는 invoice/receipt 계열 prebuilt analyzer를 확인하거나 아래 필드를 갖는 custom analyzer를 만듭니다.

| 필드 | 타입 | 확인 |
| --- | --- | --- |
| document_id | string | CONTOSO-2026-0929 |
| date | date/string | 2026-09-29 |
| currency | string | KRW |
| quantity | integer | 2 |
| unit_price | number | 89000 |
| total | number | 178000 |
| approval_status | string | pending |

생산용 기본 API는 **`2025-11-01` GA**를 기준으로 검토합니다. **`2026-06-01-preview`**의 agentic mode, 일부 classification/metadata/signature 기능은 별도 실험입니다. 2026년 9월 CU Toolkit/CU CLI도 Preview입니다.

필드의 confidence와 source grounding, warnings를 함께 확인합니다. 높은 confidence가 업무 정확도나 승인 권한을 보증하지 않습니다. OCR·layout 중심 요구라면 Document Intelligence 계열 기능과의 적합성도 비교합니다.

### 4. Code Interpreter로 숫자 분석하기

지원 agent에 Code Interpreter를 연결하고 `monthly-spend.csv`만 업로드합니다.

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

9행이 사용됐는지, 생성 파일을 실제로 열 수 있는지 확인합니다. Code Interpreter는 코드 실행 샌드박스이며 회사 ERP의 신뢰된 계산 엔진이나 네트워크 게이트웨이가 아닙니다.

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
