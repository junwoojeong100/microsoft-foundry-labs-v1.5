# `samples/` 파일 안내

`samples/`에는 가이드에서 실행하는 실습 스크립트와 여러 스크립트가 공유하는 지원 코드가 함께 있습니다. 모든 파일을 실행할 필요는 없습니다. 각 실습에서 지정한 파일과 명령만 사용하세요.

## 실행 전에

- 명령은 별도 안내가 없으면 실습 ZIP을 푼 저장소 루트에서 실행합니다. L00–L19에서 지정하는 Python 환경과 실행 위치를 우선하세요.
- `doctor`, `validate-data`, `tools`는 로컬에서 환경·합성 데이터·함수 동작을 확인합니다. 예를 들어 `python samples/workshop.py tools`는 네트워크나 주문 없이 초안 계산 결과를 보여 줍니다.
- Foundry나 Azure에 연결하는 작업은 해당 실습의 범위와 승인된 프로젝트를 먼저 확인하세요. 여러 파일은 `--live` 없이는 계획만 보여 주지만, `--live`는 모든 프로그램에 공통인 안전 스위치가 아닙니다. `--confirm`, 영수증, 도구별 승인 등 각 명령의 조건도 지켜야 합니다.
- 데이터는 합성 Contoso 구매 자료입니다. 실제 주문·결제·업무 승인을 수행하지 않습니다. `results/`에는 개인 실행 결과와 영수증이 저장될 수 있으므로 공유하거나 저장소에 올리지 마세요.

## 실습에서 직접 실행하는 파일

| 파일 | 역할 | 안내서에서의 위치·경계 |
| --- | --- | --- |
| [a2a_lab.py](a2a_lab.py) | 원격 에이전트에 A2A 위임을 수행합니다. | L14의 선택 확장입니다. `multi_agent.py`의 한 프로세스 내 오케스트레이션과는 다른 실습입니다. |
| [evaluation_lab.py](evaluation_lab.py) | 고정 평가 데이터의 준비·보정·Foundry 평가를 다룹니다. | 평가 확장 스크립트입니다. 데이터 split과 각 명령의 `--live` 조건을 확인하세요. |
| [first_response.py](first_response.py) | Responses API 요청 한 번을 짧은 코드로 보여 줍니다. | L03의 첫 코드 실습입니다. 기본은 계획만 출력하고 `--live`에서만 한 번 호출합니다. |
| [hosted_client.py](hosted_client.py) | 로컬 또는 배포된 Hosted Agent를 호출·평가하고 실행 근거를 보존합니다. | L12. `--local`이어도 에이전트가 실제 Azure 서비스를 호출할 수 있으므로 `--live`가 필요합니다. 세션을 삭제하지 않습니다. |
| [instruction_evaluation.py](instruction_evaluation.py) | 이미 수집한 v1/v2 답변을 Foundry에서 한 번 평가합니다. | L08의 선택 경로입니다. 대상 에이전트를 다시 호출하지 않습니다. |
| [instruction_lab.py](instruction_lab.py) | 개발용 데이터로 제한된 v1/v2 지침 비교를 수집합니다. | 선택 비교 스크립트입니다. 재시도나 holdout 사용을 하지 않습니다. |
| [instruction_prompt_agent_lab.py](instruction_prompt_agent_lab.py) | 버전을 고정한 Prompt Agent로 v1/v2 답변을 수집합니다. | L08의 선택 경로입니다. `--live`는 에이전트 버전을 만들고 모델 호출을 수행할 수 있습니다. |
| [inventory_api.py](inventory_api.py) | 합성 재고를 읽는 로컬 HTTP 서버입니다. 초안 생성 endpoint는 없습니다. | L07. loopback 전용이며 클라우드에 노출하거나 터널링하지 않습니다. |
| [local_lab.py](local_lab.py) | Foundry Local 기기 실습을 검사하거나 실행합니다. | 기본은 검사만 합니다. `--local`은 실제 로컬 기기 작업을, `--allow-download`는 모델·실행 공급자 다운로드를 허용합니다. Azure 호출은 하지 않습니다. |
| [memory_lab.py](memory_lab.py) | 합성 선호 정보의 저장·조회·검증·항목 삭제를 보여 줍니다. | L15의 선택 실습입니다. 항목 삭제는 Memory 저장소나 리소스 그룹을 삭제하지 않습니다. |
| [model_capacity.py](model_capacity.py) | 학습자 수·역할 기준 모델 처리량을 계획하고 용량을 확인·변경·시험합니다. | L02/L13의 선택 경로입니다. Azure 용량 변경·시험에는 명시적 `--live`와 소유 범위 확인이 필요합니다. |
| [multi_agent.py](multi_agent.py) | Agent Framework의 순차·동시·그룹 채팅·핸드오프 흐름을 실행합니다. | L13–L14. 계획 출력은 기본이며 실제 모델 실행에는 `--live`가 필요합니다. 원격 A2A 실습은 아닙니다. |
| [mcp_server.py](mcp_server.py) | 재고 조회와 구매 초안 계산을 제공하는 로컬 stdio MCP 서버입니다. | L07. 합성 데이터만 쓰며 외부 업무 작업을 수행하지 않습니다. |
| [optimizer_lab.py](optimizer_lab.py) | 개발 데이터에 한정해 Foundry Agent Optimizer 작업을 시작·관찰합니다. | 선택 확장입니다. 후보를 자동 적용하거나 배포하지 않습니다. |
| [prepare_practice.py](prepare_practice.py) | 의도적으로 결함이 있는 로컬 연습 문제를 새 학습자 폴더로 복사합니다. | L17/L18 설계 연습 보조 도구입니다. Azure 작업은 수행하지 않습니다. |
| [prepare_tuning.py](prepare_tuning.py) | 작은 합성 SFT 형식 연습 데이터를 만듭니다. | 선택 참고 도구입니다. 학습 작업을 제출하거나 모델을 변경하지 않습니다. |
| [routine_lab.py](routine_lab.py) | 제한된 범위의 Routine 생성·실행·상태 확인·중지를 연습합니다. | L16. 중지 절차를 따르며 Routine이나 리소스 그룹을 삭제하지 않습니다. |
| [search_lab.py](search_lab.py) | 합성 정책 말뭉치와 Search/Foundry IQ 검색 경로를 다룹니다. | L11. `corpus`는 로컬 확인이며 인덱스 초기화·검색의 Azure 실행에는 명시적 `--live`가 필요합니다. |
| [toolbox_lab.py](toolbox_lab.py) | MCP, OpenAPI, Toolbox, Skill 도구의 설정·검사·호출을 연습합니다. | L07 및 선택 확장. `--approve-tool`은 해당 호출 한 건의 도구 이름을 지정합니다. |
| [trace_lab.py](trace_lab.py) | 보존된 응답 ID와 Application Insights trace를 연결해 조회합니다. | L10의 선택 경로입니다. 없는 trace를 성공으로 추정하지 않습니다. |
| [workshop.py](workshop.py) | 로컬 함수, 모델 호출, 에이전트, File search, 통합 실습을 묶은 실행기입니다. | L02–L06의 완성형·참고 구현입니다. 처음에는 작은 `first_response.py`부터 따라가세요. |

### `workshop.py` 명령 구분

| 명령 | 동작 |
| --- | --- |
| `doctor`, `validate-data`, `tools` | 로컬 환경·합성 데이터·함수 동작 확인. 네트워크나 Azure 호출 없음. |
| `read-result --input ...` | 저장된 응답·도구 결과·인용을 로컬에서 읽습니다. 새 Azure 호출이나 품질 판정은 하지 않습니다. |
| `score --input ...` | 사람이 검토한 전체 기록에 평가 기준을 적용합니다. 통과 결과는 운영 인증이 아닙니다. |
| `model`, `agent`, `rag`, `capstone`, `evaluate` | `--live`가 없으면 실행 계획만 출력합니다. `--live`를 지정하면 설정된 Foundry 프로젝트에 요청하고 리소스를 만들 수 있으며 비용이 발생할 수 있습니다. |
| `cleanup --receipt ... --confirm ... --live` | 영수증에 기록된 리소스만 삭제합니다. 확인 값은 해당 영수증의 정확한 실행 ID여야 합니다. 실행 전 실습의 소유 범위와 정리 안내를 다시 확인하세요. |

## 터미널 명령을 코드 흐름으로 읽기

`python samples/파일.py 하위명령 --옵션 값`은 **실행기 → 파일 → 작업 → 입력값** 순서입니다. 각 장의 명령 해설과 함께 아래 흐름을 보면, 실행 전에 코드가 무엇을 읽고 어디에 결과를 남기는지 알 수 있습니다. 먼저 로컬·계획 경로에서 입력값을 하나만 바꿔 봅니다. Azure 요청·리소스 변경은 해당 장의 승인·`--live` 조건을 따릅니다.

| 실습·대표 명령 | 입력 → 코드 흐름 → 결과 | 먼저 바꿔 보거나 확인할 것 |
| --- | --- | --- |
| L03 `first_response.py` | 질문 → 설정·인증 → Responses API 1회 → 답변과 `response_id` | `--query`를 바꾸고 계획 출력을 먼저 읽습니다. |
| L06 `workshop.py tools` | SKU·수량 → 재고 조회 → 입력·재고 검사 → 승인 대기 초안 JSON | SKU·수량을 하나씩 바꾸고 오류와 정상 결과를 비교합니다. Azure 호출 없음. |
| L03–L06 `workshop.py model/agent/rag/capstone` | 질문·프롬프트·정책·도구 → 모델/검색/dispatcher → 응답 JSONL과 리소스 영수증 | `--live`가 없을 때는 계획만 봅니다. 통합 결과는 `read-result`로 다시 읽습니다. |
| L02/L13 `model_capacity.py` | 학습자 수·역할 → 처리량 계획 → 계획 출력; 라이브 하위명령은 용량 확인·변경·시험 | `plan --learners 1`과 다른 인원 수를 비교합니다. `apply`는 리소스 변경입니다. |
| L07 `inventory_api.py` + `toolbox_lab.py` | 로컬 HTTP/MCP 서버 → 승인한 도구 호출 → 합성 재고·초안 결과 | `--local` 호출은 한 도구만 골라 `--approve-tool`로 확인합니다. |
| L08 `instruction_prompt_agent_lab.py` → `instruction_evaluation.py` | 고정 질문·v1/v2 → 저장된 답변 파일 → 그 파일을 그대로 Foundry에서 평가 | 응답 JSON과 평가 JSON을 구분합니다. 평가는 대상 agent를 다시 호출하지 않습니다. |
| L10 `trace_lab.py` | 저장 응답 파일의 ID + App Insights 식별자 → trace 상관 조회 → 보고서 | 실행 전 로컬 입력 파일을 확인합니다. 원격 조회는 `--live`가 필요합니다. |
| L11 `search_lab.py` | 합성 정책 말뭉치 → 인덱스 설정·검색 모드 → 검색 결과와 근거 | `corpus`는 로컬입니다. 인덱스 생성·질의는 `--live` 경계를 확인합니다. |
| L12 `hosted_client.py` | 질문·agent 버전 → 로컬/배포 Hosted Agent → 보존된 실행 근거 | `--local`이어도 실제 Azure 호출일 수 있어 `--live` 조건을 확인합니다. |
| L13/L14 `multi_agent.py` | `--mode` → 로컬 SDK의 단계별 전달/위임 → Evidence 결과 | 실제 입력·출력을 비교합니다. `a2a_lab.py`의 원격 위임은 별도 참고이며 이 두 장의 실행 범위가 아닙니다. |
| L15/L16 `memory_lab.py`·`routine_lab.py` | 하위명령·영수증 → 해당 기억 항목 또는 Routine 처리 → 상태·receipt | 대상 ID와 receipt를 먼저 확인합니다. Routine은 안내된 절차대로 중지합니다. |
| 선택 `prepare_practice.py`·`prepare_tuning.py`·`local_lab.py`·`optimizer_lab.py` | 연습 유형·로컬 옵션·dev 입력 → 복사/기기 작업/최적화 → 폴더·기기 결과·job 결과 | 목적에 맞는 선택 경로만 실행합니다. 다운로드·live 작업은 별도 조건을 확인합니다. |

## `scripts/` 명령은 실습 코드와 구분하세요

`python scripts/...`는 대개 준비·운영 자동화이지 작은 학습 예제가 아닙니다. 리소스 생성이나 접근 변경은 L01/L10/L12의 소유 범위·승인을 읽고 실행합니다.

| 명령 파일 | 용도 |
| --- | --- |
| `scripts/azure_environment.py` | L01에서 참여자가 직접 전용 환경·모델·역할·로그를 만들고 L11에서 Search를 추가합니다. 생성·변경에는 `--live`와 해당 권한·비용 범위가 필요합니다. |
| `scripts/build_hosted.py`, `run_hosted_local.py`, `configure_hosted.py`, `runtime_roles.py` | Hosted Agent의 빌드·로컬 실행·구성·권한 설정입니다. 단순 Python 문법 실습이 아닙니다. |
| `scripts/stop_sessions.py`, `operations_status.py`, `cost_status.py` | 기록된 세션 중지 또는 소유 환경의 상태·비용을 확인합니다. L19 안내를 따릅니다. |
| `scripts/build_guide.py`, `check_guide.py`, `check_pdf.py`, `package_guide.py` | 가이드 원본의 생성·검사·패키징입니다. L18의 문서 자동화 참고이며 AI agent 배포나 Foundry 실행을 대신하지 않습니다. |

## 공통 지원 코드와 계약

이 파일들은 보통 직접 실행하지 않습니다. 위의 실습 스크립트에서 가져와 사용합니다.

| 파일 | 역할 |
| --- | --- |
| [business_checks.py](business_checks.py) | 실제 실행 근거의 구조·업무 경계를 결정적으로 검사합니다. 모델의 의미 평가와 구분됩니다. |
| [cloud.py](cloud.py) | 선택형 라이브 실습이 공유하는 Azure 연결·요청 전송 코드입니다. |
| [evidence.py](evidence.py) | 실행 근거를 제한된 범위로 기록하고 민감값을 가리며 요청·시간 예산을 적용합니다. |
| [evaluation_data.py](evaluation_data.py) | 평가 데이터 버전과 split을 다룹니다. 개발 데이터 읽기가 잠긴 holdout 자료를 열지 않도록 합니다. |
| [grounding.py](grounding.py) | 실제 검색된 자료에 근거해 인용을 선택·검사합니다. 추측한 출처를 만들지 않습니다. |
| [hosted_runtime.py](hosted_runtime.py) | 로컬·Hosted 호출이 공유하는 한 번의 제한된 구매 에이전트 처리 흐름입니다. |
| [lab_profile.py](lab_profile.py) | `FOUNDRY_LAB_LANGUAGE`에 따라 한국어 또는 영어 합성 자료를 선택해 두 프로필이 섞이지 않게 합니다. |
| [request_contract.py](request_contract.py) | 도구 초안의 입력이 사용자의 명시 요청에 근거하는지 검사하고 임의로 만들어진 수량을 거부합니다. |
| [inventory.openapi.json](inventory.openapi.json) | L07 로컬 재고 API의 OpenAPI 계약입니다. 서버 주소는 `127.0.0.1`이며 Foundry에서 직접 접근할 수 없습니다. |

## 관련 파일 위치

- `data/`는 정책·프롬프트·합성 재고·평가 입력입니다. 한국어 기본 프로필과 영어 프로필은 분리되어 있습니다.
- `.env.example`은 설정 이름의 예시입니다. 개인 설정은 `.env`에 두고 커밋하지 마세요.
- `results/`는 실행 결과·영수증·증거 파일의 개인 보관 위치입니다. `completed`는 실행 완료를 뜻할 뿐 품질 통과가 아니며, 로컬 검사나 fixture 결과를 Azure 실행 증거로 기록하지 마세요.
- `hosted/`, `scripts/`, `infra/`에는 Hosted 서비스, 빌드·운영 스크립트, 인프라 정의가 있습니다. 해당 파일은 관련 실습 장에서 설명합니다.
