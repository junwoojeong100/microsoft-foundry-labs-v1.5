# `samples/` 파일 안내

**기본 포털 실습은 이 스크립트를 실행하지 않습니다.** 코드가 필요한 현재 [L12](../docs/14-hosted.md)·[L13–L14](../docs/15-multiagent.md)에서 명시한 명령만 사용합니다. 나머지는 보존된 개발 참고이며 포털 코스의 추가 단계가 아닙니다.

## 실행 전에

- 현재 코드 실습은 전체 ZIP의 저장소 루트에서 실행합니다. Hosted는 `.venv-hosted`, MAF는 `.venv-maf`이며 project SDK 고정 버전이 충돌하므로 requirements를 섞지 않습니다.
- `doctor`, `validate-data`, `tools`는 로컬에서 환경·합성 데이터·함수 동작을 확인합니다. 예를 들어 `python samples/workshop.py tools`는 네트워크나 주문 없이 초안 계산 결과를 보여 줍니다.
- Microsoft Foundry나 Microsoft Azure에 연결하는 작업은 해당 실습의 범위와 승인된 프로젝트를 먼저 확인하세요. 여러 파일은 `--live` 없이는 계획만 보여 주지만, `--live`는 모든 프로그램에 공통인 안전 스위치가 아닙니다. `--confirm`, 영수증, 도구별 승인 등 각 명령의 조건도 지켜야 합니다.
- 데이터는 합성 Contoso 구매 자료입니다. 실제 주문·결제·업무 승인을 수행하지 않습니다. `results/`에는 개인 실행 결과와 영수증이 저장될 수 있으므로 공유하거나 저장소에 올리지 마세요.

## 실행 파일: 현재 실습과 보존된 참고 구분

| 파일 | 역할 | 안내서에서의 위치·경계 |
| --- | --- | --- |
| [a2a_lab.py](a2a_lab.py) | 원격 에이전트에 A2A 위임을 수행합니다. | 참고 전용. L14는 같은 프로세스의 SDK handoff이며 이 원격 프로토콜을 실행하지 않습니다. |
| [first_response.py](first_response.py) | Responses API 요청 한 번을 짧은 코드로 보여 줍니다. | 참고 전용. 현재 L03은 포털 Chat입니다. 기본 계획, 승인된 `--live`에서 1회 호출입니다. |
| [hosted_client.py](hosted_client.py) | 로컬 또는 배포된 Hosted Agent를 호출·평가하고 실행 근거를 보존합니다. | L12. `--local`이어도 에이전트가 실제 Microsoft Azure 서비스를 호출할 수 있으므로 `--live`가 필요합니다. 세션을 삭제하지 않습니다. 실습은 `invoke`만 사용하며, `evaluate`는 ZIP에 없는 유지관리자용 검증 평가 세트를 실행합니다. |
| [instruction_evaluation.py](instruction_evaluation.py) | 이미 수집한 v1/v2 답변을 Microsoft Foundry에서 한 번 평가합니다. | 참고 전용. 현재 L08은 포털 JSONL 업로드이며 이 스크립트는 대상을 다시 호출하지 않습니다. |
| [instruction_lab.py](instruction_lab.py) | 개발 데이터로 제한된 v1/v2 비교를 수집합니다. | 참고 전용. 재시도·holdout 사용 없음. |
| [instruction_prompt_agent_lab.py](instruction_prompt_agent_lab.py) | 버전을 고정한 Prompt Agent로 v1/v2 답변을 수집합니다. | 현재 L08이 아닌 참고. 승인된 `--live`는 버전 생성·모델 호출입니다. |
| [inventory_api.py](inventory_api.py) | 로컬 읽기 전용 재고 HTTP 서버이며 초안 endpoint는 없습니다. | 현재 L07이 아닌 참고. loopback 전용, 외부 노출·터널 금지. |
| [local_lab.py](local_lab.py) | Foundry Local 기기 실습을 검사·실행합니다. | 참고 전용. `--local` 기기 실행, `--allow-download` 모델/provider 다운로드. Microsoft Azure 호출 없음. |
| [memory_lab.py](memory_lab.py) | 합성 선호 정보 저장·조회·검증·항목 삭제입니다. | 참고 전용. L15 포털 관찰은 이 CRUD를 실행하지 않습니다. 항목 삭제는 store/그룹 삭제가 아닙니다. |
| [model_capacity.py](model_capacity.py) | 모델 처리량 계획·확인·변경·시험입니다. | 현재 MAF는 읽기 전용 readiness를 import합니다. CLI 용량 변경·시험은 별도 scope 승인이 필요한 참고입니다. |
| [multi_agent.py](multi_agent.py) | 실제 MAF 순차·동시·그룹 채팅·핸드오프 builder 실행입니다. | **현재 L13–L14.** 기본 계획, `--offline` 네트워크 차단 고정 fixture, 승인된 `--live` 실제 모델입니다. 원격 A2A 아님. |
| [mcp_server.py](mcp_server.py) | 로컬 stdio 합성 재고·초안 도구입니다. | 참고 전용. 현재 L07은 원격 읽기 Learn MCP이며 외부 업무 작업은 없습니다. |
| [optimizer_lab.py](optimizer_lab.py) | 개발 데이터에 한정한 최적화 시작·관찰입니다. | 참고 전용. 자동 적용·배포 없음. 기본 유지보수 세트는 ZIP·현재 실습에서 사용하지 않습니다. |
| [prepare_practice.py](prepare_practice.py) | 결함 연습 문제를 새 로컬 폴더로 복사합니다. | 참고 전용. 현재 L17/L18은 이 도구 대신 판단표입니다. Microsoft Azure 호출 없음. |
| [prepare_tuning.py](prepare_tuning.py) | 작은 합성 SFT 형식 자료를 생성합니다. | 참고 전용. 학습 제출·모델 변경 없음. |
| [routine_lab.py](routine_lab.py) | 제한된 Routine 생성·dispatch·상태·중지입니다. | 참고 전용. 현재 L16은 제출 전 취소이며 Routine/그룹 삭제 없음. |
| [search_lab.py](search_lab.py) | 정책 corpus와 Azure AI Search/Foundry IQ 검색입니다. | **현재 L12 선택 초기화**는 승인된 기존 Search만 사용합니다. L11 포털 절차가 아닙니다. 데이터 쓰기·embedding 비용 승인과 `--live` 필요. |
| [toolbox_lab.py](toolbox_lab.py) | MCP/OpenAPI/Toolbox/Skill 설정·검사·호출입니다. | 현재 L07이 아닌 참고. `--approve-tool`은 지정 도구 1회입니다. |
| [trace_lab.py](trace_lab.py) | 응답 ID와 Application Insights trace의 상관 조회입니다. | 참고 전용. 현재 L10은 포털 Traces이며 누락은 그대로 남깁니다. |
| [workshop.py](workshop.py) | 함수·모델·agent·File search·capstone 통합 실행기입니다. | **현재 L02–L06 단계가 아닌** 보존된 참고 구현입니다. 포털 완주를 위해 실행하지 않습니다. |

### `workshop.py` 명령 구분

| 명령 | 동작 |
| --- | --- |
| `doctor`, `validate-data`, `tools` | 로컬 환경·합성 데이터·함수 동작 확인. 네트워크나 Microsoft Azure 호출 없음. |
| `read-result --input ...` | 저장된 응답·도구 결과·인용을 로컬에서 읽습니다. 새 Microsoft Azure 호출이나 품질 판정은 하지 않습니다. |
| `score --input ...` | 사람이 검토한 전체 기록에 평가 기준을 적용합니다. 통과 결과는 운영 인증이 아닙니다. |
| `model`, `agent`, `rag`, `capstone`, `evaluate` | `--live`가 없으면 실행 계획만 출력합니다. `--live`를 지정하면 설정된 Microsoft Foundry 프로젝트에 요청하고 리소스를 만들 수 있으며 비용이 발생할 수 있습니다. |
| `cleanup --receipt ... --confirm ... --live` | 영수증에 기록된 리소스만 삭제합니다. 확인 값은 해당 영수증의 정확한 실행 ID여야 합니다. 실행 전 실습의 소유 범위와 정리 안내를 다시 확인하세요. |

## 터미널 명령을 코드 흐름으로 읽기

`python samples/파일.py 하위명령 --옵션 값`은 **실행기 → 파일 → 작업 → 입력값** 순서입니다. 현재 L12–L14는 명령마다 해설이 있습니다. Microsoft Azure 요청·자원 변경은 별도 승인·일치하는 receipt·명시된 상한이 필요합니다.

| 실습·대표 명령 | 입력 → 코드 흐름 → 결과 | 먼저 바꿔 보거나 확인할 것 |
| --- | --- | --- |
| L12 `search_lab.py initialize` | 합성 정책 절 → embedding 1배치 → 정확한 index·knowledge source/base → 비공개 결과 | 승인된 전용 기존 Search·호환 embedding만 사용하며 임의 포털 index가 아닙니다. |
| L12 `hosted_client.py` | 질문·agent 버전 → 로컬/배포 Hosted Agent → 보존된 실행 근거 | `--local`이어도 실제 Microsoft Azure 호출일 수 있어 `--live` 조건을 확인합니다. |
| L13/L14 `multi_agent.py --offline` | mode·case·정책 → 실제 SDK+고정 합성 backend → 전달·도구·종료 기록 | 응답·usage·고정 policy 라우팅은 모델 품질·청구·Microsoft Azure 증거가 아닙니다. |
| L13/L14 `multi_agent.py --live` | 검증된 receipt·TPM/RPM → 실제 SDK+기존 모델 → 원문·ID·usage | 로컬 orchestration+Microsoft Azure inference이며 Hosted orchestration·원격 A2A 아님. |
| 참고 `workshop.py tools` | SKU·수량 → 로컬 검증·계산 → 승인 대기 초안 | 네트워크·주문 없음. 현재 기본 실습 단계가 아닙니다. |

## `scripts/` 명령은 실습 코드와 구분하세요

`python scripts/...`는 주로 준비·운영 자동화입니다. 현재 L12–L14는 오프라인 패키징·읽기 전용 adoption·데이터 쓰기·유료 배포·권한 변경·호출을 명확히 구분합니다.

| 명령 파일 | 용도 |
| --- | --- |
| `scripts/adopt_portal.py` | 현재 L12/L13에서 기존 포털 자원을 읽기만 하여 개인 CLI receipt를 만듭니다. 기본 5회, Search·embedding 포함 7회 읽기이며 생성·권한·모델 호출·덮어쓰기 없음. |
| `scripts/azure_environment.py` | **현재 L01/L11이 아닌** 보존된 CLI 생성 참고입니다. 기존 포털 자원을 중복 생성하지 않습니다. `env --write`는 receipt 설정을 로컬에만 복사합니다. |
| `scripts/build_hosted.py`, `run_hosted_local.py`, `configure_hosted.py`, `runtime_roles.py` | Hosted Agent의 빌드·로컬 실행·구성·권한 설정입니다. 단순 Python 문법 실습이 아닙니다. |
| `scripts/check_sdk.py` | 오프라인 설치 SDK 계약 검사이며 `--advanced`는 실제 MAF fixture입니다. Microsoft Azure 라이브 검증 아님. |
| `scripts/stop_sessions.py`, `operations_status.py`, `cost_status.py` | 기록된 세션 중지 또는 소유 환경의 상태·비용을 확인합니다. L19 안내를 따릅니다. |
| `scripts/build_guide.py`, `check_guide.py`, `package_guide.py` | 유지보수 문서 생성·검사·패키징이며 학습자 L18 명령·agent 배포가 아닙니다. |

## 공통 지원 코드와 계약

이 파일들은 보통 직접 실행하지 않습니다. 위의 실습 스크립트에서 가져와 사용합니다.

| 파일 | 역할 |
| --- | --- |
| [business_checks.py](business_checks.py) | 실제 실행 근거의 구조·업무 경계를 결정적으로 검사합니다. 모델의 의미 평가와 구분됩니다. |
| [cloud.py](cloud.py) | 선택형 라이브 실습이 공유하는 Microsoft Azure 연결·요청 전송 코드입니다. |
| [evidence.py](evidence.py) | 실행 근거를 제한된 범위로 기록하고 민감값을 가리며 요청·시간 예산을 적용합니다. |
| [evaluation_data.py](evaluation_data.py) | 평가 데이터 버전과 split을 다룹니다. 개발 데이터 읽기가 잠긴 holdout 자료를 열지 않도록 합니다. |
| [evaluation_lab.py](evaluation_lab.py) | 보존된 `instruction_evaluation.py`가 가져오는 Native 평가 보조입니다. `prepare`·`calibrate`·`run --suite`는 유지보수 라이브 검증이며 현재 L08 단계가 아닙니다. |
| [grounding.py](grounding.py) | 실제 검색된 자료에 근거해 인용을 선택·검사합니다. 추측한 출처를 만들지 않습니다. |
| [hosted_runtime.py](hosted_runtime.py) | 로컬·Hosted 호출이 공유하는 한 번의 제한된 구매 에이전트 처리 흐름입니다. |
| [lab_cli.py](lab_cli.py) | 실습 진입점을 실행하고, 예상된 학습자 오류를 트레이스백 대신 `ERROR:` 한 줄(종료 코드 2)로 보여 줍니다. 트레이스백이 필요하면 `FOUNDRY_LAB_DEBUG=1`을 설정합니다. |
| [lab_profile.py](lab_profile.py) | `FOUNDRY_LAB_LANGUAGE`에 따라 한국어 또는 영어 합성 자료를 선택해 두 프로필이 섞이지 않게 합니다. |
| [maf_fixture.py](maf_fixture.py) | 실제 SDK builder·고정 합성 backend·socket/DNS 차단·합성 usage·고정 policy 라우팅입니다. 현재 MAF 실습·테스트·SDK 검사가 공유합니다. |
| [original_files.py](original_files.py) | 한 번만 만드는 결과 원본을 보호합니다. Microsoft Azure를 바꾸기 전에 실패한 실행은 기록을 `…failed-<시각>.json`으로 보관해 같은 명령을 다시 실행할 수 있게 합니다. |
| [request_contract.py](request_contract.py) | 도구 초안의 입력이 사용자의 명시 요청에 근거하는지 검사하고 임의로 만들어진 수량을 거부합니다. |
| [inventory.openapi.json](inventory.openapi.json) | 현재 L07이 아닌 보존된 로컬 API 계약입니다. `127.0.0.1`은 Microsoft Foundry에서 직접 접근할 수 없습니다. |

## 유지보수 전용 검증 자료

Microsoft Azure 라이브 검증 이력은 유지보수용으로 남지만 **ZIP·어떤 실습에도 사용하지 않습니다.** 평가 세트 v2–v5·저작/라이브 CI 스크립트·관련 테스트를 `content/maintainer-only.json` 한 곳에서 제외합니다. 현재 L08 포털 입력은 `data/evaluation/instruction-comparison.json`에서 생성합니다. Hosted `invoke`·MAF fixture는 유지보수 평가/holdout 세트를 열지 않습니다.

## 관련 파일 위치

- `data/`는 정책·프롬프트·합성 재고·평가 입력입니다. 한국어 기본 프로필과 영어 프로필은 분리되어 있습니다.
- `.env.example`은 설정 이름의 예시입니다. 개인 설정은 `.env`에 두고 커밋하지 마세요.
- `results/`는 실행 결과·영수증·증거 파일의 개인 보관 위치입니다. `completed`는 실행 완료를 뜻할 뿐 품질 통과가 아니며, 로컬 검사나 fixture 결과를 Microsoft Azure 실행 증거로 기록하지 마세요.
- `hosted/`, `scripts/`, `infra/`에는 Hosted 서비스, 빌드·운영 스크립트, 인프라 정의가 있습니다. 해당 파일은 관련 실습 장에서 설명합니다.
