> **완성할 결과:** 로컬 실행과 업무 데이터 통합의 선택지를 비교하고, 내 프로젝트에 필요한 확장만 고릅니다.

## 목표

**Foundry cloud, Foundry Local, Foundry Local on Azure Local은 동일한 배포 방식이 아닙니다.** Fabric IQ·Work IQ·Foundry IQ도 서로 다른 지식 맥락을 제공합니다.

## 개념과 실습 지도

**경험할 기능:** 장치 내 추론, Fabric의 업무 의미 계층, Microsoft 365 지식 연결의 차이를 비교합니다.

**무엇이며 왜 중요한가요?** Foundry Local은 장치에서 모델을 실행하는 runtime/SDK이고, Fabric IQ나 Work IQ는 각 업무 제품의 데이터·맥락과 연결하는 경로입니다. 클라우드 비용을 줄이기 위해 Local을 고르면 장치 메모리·모델 배포를 관리해야 하고, 업무 연결을 늘리면 원본 데이터 권한·라이선스를 관리해야 합니다. 같은 “IQ” 이름이나 “Foundry” 브랜드만으로 지원 환경이 같다고 생각하면 설계가 어긋납니다.

**어떻게 사용하나요?** 필요한 결과가 장치 내 짧은 추론인지, 분석 지표 조회인지, 권한 있는 업무 문서 검색인지 먼저 결정합니다. 자기 환경에서 허용된 한 갈래만 실제 실행하고, 나머지는 지원 조건과 선택 이유를 기록합니다. 추가 제품을 모두 설치하는 장이 아닙니다.

**어디서 실행하나요?** Local은 지원 장치와 공식 SDK, Fabric/M365는 해당 제품의 승인된 테스트 환경이 필요합니다. 이 리포의 [월별 합성 지출](../data/monthly-spend.csv)과 [구매 정책](../data/policies/procurement-policy.md)을 입력으로 사용하되, 별도 제품의 실행기가 모두 동봉되어 있다고 가정하지 않습니다.

## 준비

이 모듈은 **선택형 미니 실습**입니다. 보유 환경에 맞는 한 가지를 수행하고 나머지는 선택/설계 기록으로 남깁니다. 추가 라이선스·관리자 동의·모델 다운로드·하드웨어 요건을 미리 확인합니다.

**선택 예:** “월별 장비 지출의 정확한 합계”가 목적이면 합성 CSV를 가진 Fabric 경로를, “인터넷 없는 장치의 짧은 안내”면 Local을 고릅니다. “권한 있는 M365 문서 검색”은 Work IQ 경로입니다. 한 기능으로 다른 기능의 성공을 대신하지 않습니다.

선택한 경로에 **목적·준비된 실행기/자원·입력·기대 결과·미지원 조건·종료 동작**을 먼저 적습니다. 자원이 없으면 아래 작성 예를 이용한 설계가 결과물이며, 실제 실행으로 표시하지 않습니다.

## 실행

### 1. 선택 A: Foundry Local

[Foundry Local quickstart](https://learn.microsoft.com/azure/foundry-local/get-started)에서 장치와 언어에 맞는 **현재 SDK 샘플**을 선택합니다. 모델 목록 확인 → 지원 모델 다운로드 → 짧은 추론 → 모델 unload 순서로 진행합니다.

| 확인할 것 | 어떻게 판단하나요? | 실패하면 다음 행동 |
| --- | --- | --- |
| 공식 샘플의 지원 OS·SDK·장치 메모리 | 자신의 환경과 선택한 모델 요구가 맞음 | 맞지 않으면 중단/다른 지원 장치 선택. 클라우드 모델로 바꾸어 Local 성공이라고 쓰지 않음 |
| 모델 ID와 다운로드 완료 상태 | 실행할 모델이 실제 장치에 준비됨 | 다운로드 실패와 추론 실패를 분리. 승인된 저장 공간·네트워크 확인 |
| 샘플의 한 번 생성 호출과 아래 입력 | 초안은 요청 준비, 주문은 별도 승인·시스템 실행이라는 차이 | 응답 언어·잘림·모델 지원 확인. 업무 API 실행 여부와 혼동하지 않음 |
| 모델 unload 후 상태 | 메모리에 로드된 실행 모델 해제 | 프로세스/모델 상태를 확인. 캐시 삭제와 unload를 구분 |

```text
입력: "구매 요청 초안과 실제 주문의 차이를 한 문장으로 설명해줘."
```

첫 다운로드 시간과 이후 추론 시간을 구분하고, model/version·메모리 사용·hardware acceleration·응답을 기록합니다. 모델과 runtime을 준비한 후 승인된 오프라인 테스트 환경에서도 같은 추론이 가능한지 확인합니다.

현재 Foundry Local의 핵심은 앱 안에 포함하는 **runtime/SDK**입니다. 선택적 server/CLI도 있지만 “클라우드 Agent Service를 로컬에 설치한다”는 뜻이 아닙니다. 장치 내 추론에는 Azure 구독이나 cloud token 비용이 필요 없지만 초기 모델/component 다운로드와 라이선스·선택적 diagnostics 조건은 남습니다.

### 2. 선택 B: Fabric IQ

관리자가 승인된 workspace와 data agent/semantic model을 제공한 경로로 시작합니다. [Fabric IQ 연결 문서](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/fabric-iq)에서 그 항목의 지원과 호출 identity를 확인합니다. 준비되지 않았다면 모든 Fabric 구성 요소를 새로 만드는 대신 아래 명세를 작성합니다.

**Contoso 명세 예 — 실제 Fabric 실행 결과가 아닙니다.**

| 단계 | 입력·선택 | 판단할 결과 |
| --- | --- | --- |
| 원본 준비 | `monthly-spend.csv`, 헤더 제외 9행 | `month`, `category`, 숫자형 `amount_krw` |
| 집계 정의 | `month`별 `amount_krw` 합계, 필터 없음 | 7월 3,718,000 / 8월 2,677,000 / 9월 4,759,000 KRW |
| 원본 제품 확인 | Fabric에서 먼저 같은 집계 실행 | 전체 11,154,000과 9행 확인 후에만 Foundry 연결 단계로 이동 |
| 연결 | 지원되는 Fabric IQ 도구에 승인된 item과 읽기 주체 지정 | 연결된 item·identity가 원본 시험과 같음 |
| 질문 | “월별 장비 지출 합계와 전체 합계를 알려줘.” | 실제 도구 결과와 최종 답변이 원본 집계와 일치 |

합계가 다르면 **원본 타입/중복 → measure와 필터 → 연결 item/identity → 답변 합성** 순으로 확인합니다. 원본 집계부터 틀린 경우 프롬프트를 바꾸지 않습니다. 숫자만 맞고 도구 근거가 없으면 연결 성공은 미확인입니다.

### 3. 선택 C: Work IQ / SharePoint

승인된 테스트 테넌트와 **관리자가 제공한 테스트 계정 A/B**만 사용합니다. [Work IQ 연결 문서](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/work-iq)에서 위임·관리자 동의·라이선스 조건을 확인합니다. 계정이나 권한을 실습 중 임의 생성하지 않습니다.

합성 구매 정책 한 문서를 A에게 허용하고 B에게는 허용하지 않는 **승인된 시험 설정**을 준비합니다. 원본 SharePoint에서 A는 열 수 있고 B는 열 수 없는지 먼저 확인합니다. 다음에는 서로 다른 로그인·새 대화에서 같은 정책 질문을 보냅니다. 기대 결과는 A의 허용 문서 근거와, B에게 그 제한 문서의 본문·제목·URL이 노출되지 않는 것입니다. B가 별도 공용 사실에 답한다면 그 근거가 다른 허용 자료인지도 구분합니다.

B에게 제한 근거가 보이면 반복 질의 전에 원본 ACL·위임된 사용자·대화/캐시 혼용을 점검합니다. 한 계정의 두 대화만으로 사용자 격리를 시험했다고 쓰지 않습니다.

Work IQ Preview, remote SharePoint 검색, direct SharePoint tool, Foundry IQ의 knowledge source를 같은 기능이라고 혼용하지 않습니다. 검색 protocol과 원본 권한의 집행 위치를 기록하세요.

### 4. 제품 경계를 한 장에 정리하기

| 필요 | 선택지 | 기본 코스와 다른 조건 |
| --- | --- | --- |
| 앱 사용자의 장치 내 추론 | Foundry Local | 모델 크기·하드웨어·SDK |
| 기업 on-prem 인프라의 inference | Foundry Local on Azure Local | 별도 Preview 접근·Kubernetes/Arc·운영 인프라 |
| 조직 문서의 지식 검색 | Foundry IQ | Search·knowledge source·권한 |
| 분석/업무 의미 계층 | Fabric IQ | Fabric item·semantic context |
| M365 업무 맥락 | Work IQ | M365 권한·위임·라이선스 |
| Copilot Studio에서 사용 | Foundry agent/지식 연결 | 해당 connector의 지원·Preview 조건 |

### 5. 특수 모델·프레임워크 선택 과제

커뮤니티/Hugging Face, Fireworks 연계, healthcare 모델, 이미지·영상·audio 모델을 검토할 때 **이름보다 라이선스·책임 범위·지원 배포·평가 방법**을 기록합니다. 의료 특화 모델을 임상 판단이나 진단에 바로 쓰는 과제가 아닙니다.

LangGraph/LangChain 또는 Semantic Kernel을 이미 쓰는 팀은 전면 재작성보다 Foundry endpoint·Toolbox·tracing·hosted runtime과의 연결부터 검토합니다. 기존 코드를 가져온다고 state·retry·security 계약까지 자동 호환되지는 않습니다.

## 성공 기준

선택한 한 경로의 **입력·실행기/identity·기대값·실제값·실패 시 다음 행동·종료 상태**를 기록했습니다. 접근 불가라면 원인과 작성된 설계 명세를 남깁니다. 다른 경로는 미실행으로 표시하며 Local 추론을 Fabric/M365 권한 검증으로 합산하지 않습니다.

## 막혔을 때

추가 제품의 라이선스·권한·지역·하드웨어 조건은 Foundry 프로젝트 역할만으로 해결되지 않습니다. 필요한 preview 접근이 없으면 다른 테넌트의 정보를 사용해 우회하지 않습니다.

## 정리

로컬 모델은 unload하고 모델 캐시의 유지 여부를 결정합니다. 테스트 connections·권한·외부 source는 각 제품 담당자와 회수합니다.
