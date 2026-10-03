> **완성할 결과:** 로컬 실행과 업무 데이터 통합의 선택지를 비교하고, 내 프로젝트에 필요한 확장만 고릅니다.

<div class="lab-brief" markdown="1">

**진행 방식:** 선택 심화 · Local, Fabric, Work IQ 중 필요한 한 경로만 고릅니다.

**먼저 할 일:** 목표가 장치 내 답변인지, 지출 집계인지, 권한 있는 문서 검색인지 정합니다.

**확인할 결과:** 선택 이유·필요 조건·기대 결과·종료 방법을 적고, 실제 실행 여부는 따로 표시합니다.

</div>

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

[Foundry Local quickstart](https://learn.microsoft.com/azure/foundry-local/get-started)의 native SDK 흐름을 동봉 [local_lab.py](../samples/local_lab.py)로 수행합니다. 다른 샘플 저장소를 복제하지 않습니다. 기본 예시는 `qwen2.5-0.5b`이며 작은 모델의 한국어 품질이나 업무 정확도를 보장하지 않습니다.

<div class="practice-block" markdown="1">

**직접 해보기 — 먼저 계획:** 아래 명령은 SDK 초기화·모델 다운로드 없이 계획만 출력합니다.

```bash
python samples/local_lab.py chat
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `local_lab.py chat` | 기본 모델과 문장형 출력의 계획을 읽습니다. | `plan_only`, `sdk_initialized=false`, `azure_calls=0`. 설치나 모델 실행 없음. |

</div>

실제 장치 실습을 선택한 경우에만 별도 환경을 만듭니다. **Windows에서는 `.venv-local/bin/python` 대신 `.venv-local\Scripts\python.exe`**를 사용합니다. 첫 줄의 `python`은 L01에서 준비한 Python 3.13입니다. 영어 실습은 새 터미널마다 `FOUNDRY_LAB_LANGUAGE=en`을 유지합니다.

```bash
python -m venv .venv-local
.venv-local/bin/python -m pip install -r requirements-local.txt
.venv-local/bin/python samples/local_lab.py inspect --local
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `venv .venv-local` | 기본·MAF 환경과 분리된 로컬 모델용 환경을 만듭니다. | 내 PC의 폴더 생성. |
| 2. `pip install` | OS별 선언된 SDK를 설치합니다: 비 Windows 2.1.0, Windows WinML 1.2.4. | 승인된 패키지 저장소 접속·설치. Azure 배포 없음. |
| 3. `inspect --local` | SDK를 초기화하고 실제 선택 모델 ID·캐시·로드 상태를 확인합니다. | 카탈로그 메타데이터 조회가 네트워크를 사용할 수 있음. 모델 가중치를 자동 다운로드하거나 추론하지 않음. |

</div>

모델 사용 조건·디스크 공간·장치 지원을 확인한 뒤 **모델/실행 공급자 다운로드를 승인한 경우에만** 진행합니다.

```bash
.venv-local/bin/python samples/local_lab.py download --local --allow-download
.venv-local/bin/python samples/local_lab.py chat --style sentence --local
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `download --allow-download` | 모델 및 필요한 실행 공급자를 다운로드합니다. 모델 캐시는 `.build/local-model-cache/ko`에 둡니다. | 다운로드·디스크 사용. Azure 구독이나 모델 호출은 없음. |
| 2. `chat --style sentence --local` | 캐시된 모델을 로드해 합성 초안/주문 차이를 한 번 질문합니다. 최대 출력 256토큰입니다. | 실제 장치 추론. `load_seconds`, `inference_seconds`, `answer`, `unloaded=true`를 확인. 캐시가 없으면 자동 다운로드 대신 오류. |

</div>

`--local`은 이 파일의 **실제 장치 작업 허용**입니다. Azure 호출이 가능한 L14의 로컬 서버와 다른 경로입니다. 다운로드·로드·추론 시간을 구분하고, 오류나 잘린 답을 정상 응답으로 바꾸지 않습니다. 다운로드가 사내 정책으로 막히면 승인된 설치 경로를 사용하며 보안 설정을 우회하지 않습니다.

**한 가지 바꾸기:** 다음에는 같은 모델·질문에서 출력 형식만 문장→체크리스트로 바꿉니다. 이는 한 번의 추가 장치 추론입니다.

```bash
.venv-local/bin/python samples/local_lab.py chat --style checklist --local
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 세부 동작과 옵션 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `--style checklist` | 같은 합성 질문을 짧은 세 항목으로 답하도록 지시만 변경합니다. | 추가 로컬 추론·로드/해제. Azure 호출 없음. 모델의 실제 출력 형식을 사람이 확인합니다. |

</div>

**결과 설명하기:** `모델 ID / 형식 / 실제 항목 수 / 초안≠승인·주문 의미 보존 / 추론 시간 / 해제 상태`를 비교합니다. 형식 지시를 못 지켰다면 실패로 기록합니다. 더 긴 응답이나 더 빠른 한 번의 결과만으로 품질 우월성을 주장하지 않습니다. 예제는 클라우드로 자동 전환하지 않습니다.

</div>

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

**대표 경로를 하나로 고정합니다: CSV → Lakehouse 표 → Fabric data agent → Foundry Toolbox.** Ontology와 Power BI semantic model은 이번 경로에 추가하지 않습니다.

| 사전 확인 | 받아야 할 값 |
| --- | --- |
| Fabric | 승인된 paid F2 이상 또는 Fabric이 켜진 P1 이상 용량의 workspace, 같은 리전의 실습 Lakehouse |
| 접근 | 자기 테스트 사용자, 데이터·data agent 읽기 및 이 실습 항목의 작성 권한 |
| 연결 | 관리자가 준비한 **data agent용** Foundry 연결 이름/ID와 위임된 사용자 인증. API key 아님 |
| 비용·처리 범위 | 용량·AI 이용·지역 간 처리의 승인과 종료 담당자. 실습 중 구독/용량을 구매하지 않음 |

1. 실습 Lakehouse의 **Files**에 동봉 `monthly-spend.csv` 하나만 업로드합니다. 파일 메뉴 **Load to tables → New table**에서 이름 `contoso_spend`, 첫 행 Column header 선택, 구분자 `,`를 지정합니다. 기존 표에 Append/Overwrite하지 않습니다. [Load to tables 필드](https://learn.microsoft.com/fabric/data-engineering/load-to-tables)와 대조해 **9행, month/category/amount_krw**, 금액의 숫자형 해석을 확인합니다.
2. workspace의 **+ New item → Fabric data agent**에서 `contoso-spend-agent`를 만듭니다. OneLake catalog에서 해당 Lakehouse를 Add하고, Explorer에서 **`contoso_spend` 표만** 선택합니다. [Data agent 생성 절차](https://learn.microsoft.com/fabric/data-science/how-to-create-data-agent)를 이 한 표에 적용합니다.
3. Agent instructions에 “선택한 contoso_spend만 사용하고 month별 amount_krw의 합과 전체 합을 KRW로 답한다. 없는 행을 만들지 않는다”를 넣습니다. Fabric 내부 대화에서 아래 질문을 한 번 보내 원본 집계를 먼저 확인하고 Publish합니다.
4. 관리자는 **게시된 해당 data agent**의 workspace/item ID와 MCP endpoint가 Foundry 연결에 맞는지 확인합니다. 일반 endpoint 형태는 `https://api.fabric.microsoft.com/v1/mcp/workspaces/<workspaceId>/dataagents/<dataAgentId>/agent`입니다. 실제 값은 자기 항목에서 복사하며 private-link 환경의 별도 host는 담당자가 확인합니다.
5. Foundry Toolkit의 **My Resources → 자신의 project → Tools → Toolbox → Add tools → Configured → Fabric IQ (OneLake Catalog)**에서 준비된 연결을 선택하고 **Add Tools → Publish/Save Changes**합니다. 첫 Fabric IQ 연결 생성은 Toolkit에서 직접 지원되지 않으므로 관리자가 Foundry 포털에서 먼저 준비해야 합니다. 다른 Fabric 항목의 연결을 대신 고르지 않습니다.
6. 새 실습용 Text agent에 게시된 Toolbox의 정확한 버전을 연결하고 “이 도구로만 합성 지출을 조회하며 결과가 없으면 모른다고 답한다”는 지시를 넣습니다. 같은 집계 질문을 한 번 보내 아래 값과 **실제 도구 결과·연결 항목**을 대조합니다. 질문의 원본 제품 확인과 Foundry 확인은 별도 요청입니다.

**Contoso 명세 예 — 실제 Fabric 실행 결과가 아닙니다.**

| 단계 | 입력·선택 | 판단할 결과 |
| --- | --- | --- |
| 원본 준비 | `monthly-spend.csv`, 헤더 제외 9행 | `month`, `category`, 숫자형 `amount_krw` |
| 집계 정의 | `month`별 `amount_krw` 합계, 필터 없음 | 7월 3,718,000 / 8월 2,677,000 / 9월 4,759,000 KRW |
| 원본 제품 확인 | Fabric에서 먼저 같은 집계 실행 | 전체 11,154,000과 9행 확인 후에만 Foundry 연결 단계로 이동 |
| 연결 | 지원되는 Fabric IQ 도구에 승인된 item과 읽기 주체 지정 | 연결된 item·identity가 원본 시험과 같음 |
| 질문 | “월별 장비 지출 합계와 전체 합계를 알려줘.” | 실제 도구 결과와 최종 답변이 원본 집계와 일치 |

합계가 다르면 **원본 타입/중복 → measure와 필터 → 연결 item/identity → 답변 합성** 순으로 확인합니다. 원본 집계부터 틀린 경우 프롬프트를 바꾸지 않습니다. 숫자만 맞고 도구 근거가 없으면 연결 성공은 미확인입니다.

**한 가지 변경 과제:** 추가 질문을 승인받았다면 필터만 “2026-09”로 바꿉니다. 기대는 **3행·4,759,000 KRW**이며 전체 11,154,000을 반환하면 필터가 적용되지 않은 것입니다. 데이터·도구·모델을 함께 바꾸지 않습니다.

### 3. 선택 C: Work IQ / SharePoint

승인된 테스트 테넌트와 **관리자가 제공한 테스트 계정 A/B**만 사용합니다. [Work IQ 연결 문서](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/work-iq)에서 위임·관리자 동의·라이선스 조건을 확인합니다. 계정이나 권한을 실습 중 임의 생성하지 않습니다.

이번에는 **Work IQ Chat의 A2A 연결** 하나만 사용합니다. 관리자가 Work IQ 서비스 주체·위임 권한 `WorkIQAgent.Ask`·동의·기존 연결을 준비합니다. 이 API 경로는 **Copilot Credits 사용량 청구**이며 모든 connector의 라이선스 조건과 같지 않습니다. 학습자에게 Global Administrator를 요구하거나 Outlook·메일 발송 도구까지 붙이지 않습니다.

| 단계 | 직접 할 일·확인 |
| --- | --- |
| 합성 원본 | 승인된 테스트 SharePoint 위치에 문서 하나: 제목 “Contoso 제한 견적 실습”, 내용 “사례 LAB-73, 교육용 견적코드 CONTOSO-QUOTE-DEMO-73. 실제 거래 효력 없음.” |
| 원본 권한 | 관리자가 A만 읽도록 격리. **원본에서 A는 열림, B는 거절**을 먼저 확인. B에게 상위 사이트/그룹 권한이 남아 있으면 진행하지 않음 |
| Toolbox | Foundry Toolkit → My Resources → project → Tools → **+ Add Toolbox → Add tools → Work IQ → Work IQ Chat**. 준비된 연결 선택 → Add → Publish |
| Agent | 별도 Text agent에 그 Toolbox 버전만 연결. File search·Web search·다른 업무 도구는 연결하지 않음 |
| A/B 호출 | 각각 별도 로그인·새 대화에서 “교육용 사례 LAB-73의 견적코드와 원본문서를 확인해줘”를 한 번씩 보냄 |
| 판독 | A는 실제 도구 근거와 코드가 있어야 함. B에게는 제공하지 않은 코드·본문·문서 URL이 나오면 안 됨. 실제 도구 결과도 같이 읽음 |

견적코드를 질문·instructions·공용 검색 인덱스에 넣지 않습니다. 이 표의 코드가 모범 답으로 알려져 있다는 것과 모델이 권한 있는 원본을 조회했다는 것은 별개입니다. A/B 질문은 총 2건으로 제한하며 서비스 내부 처리·과금은 별도입니다. 접근할 문서가 모두 합성인 승인된 테스트 환경이 없으면 실행하지 않습니다.

위 표의 격리된 견적 문서 하나로 확인합니다. L05의 공용 구매 정책을 대신 연결하면 B가 다른 허용 근거에서 정답을 얻을 수 있어 제한 문서 시험과 구분하기 어렵습니다.

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
