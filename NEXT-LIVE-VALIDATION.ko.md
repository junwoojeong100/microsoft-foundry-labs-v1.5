# 다음 세션: 수정 후보의 제한된 live 검증

> **이 인계의 live 승인 범위는 v5 실행에 사용했습니다. 같은 실험을 다시 실행하지 마세요.** 새 결과는 `validation/english/automated-v5/`에 별도 보존합니다. Dev 40건을 모두 수집·평가했지만 합산 39/40 및 access 근거 실패 1건으로 최종 게이트가 닫혔고, 새 holdout 10건은 실행하지 않았습니다. 아래는 보존된 원래 인계 내용입니다. 이후 사용자 메시지에서 main 머지·Pages 게시만 추가 승인했으며, Azure 권한·정책·삭제·예산 범위는 확대하지 않았습니다.

> Optimizer 한 건은 647초 후 service `succeeded`였으나 native 38 통과·1 실패·1 오류로 `operational_failure`입니다. 후보 생성·승격은 없으며 생성 세션 5개와 기록된 job/native run의 종료를 새 SDK readback으로 확인했습니다. 전체 결론은 `validation/english/automated-v5/report.json`, 실제 판정은 `quality.json`, `optimizer.json`, `operations.json`을 참고하세요.

이 저장소의 이전 작업을 이어서 수행해줘. 이 요청은 아래 범위의 새 후보 live 검증을 승인한다. 같은 실패 후보를 그대로 재실행하거나 통과할 때까지 재샘플링하지 마.

## 저장소와 보존 조건

- 작업 폴더: 현재 `microsoft-foundry-labs-v1.5` 저장소 루트
- GitHub repository ID: `1396573688`, `junwoojeong100/microsoft-foundry-labs-v1.5`
- 작업 브랜치: `fix/english-quality-optimizer`. 기존 미커밋 변경을 보존하고 reset/revert/강제 push를 하지 마.
- `AGENTS.md`와 `microsoft-foundry` skill을 먼저 읽고 해당 사전 점검을 따라줘.
- 합성 Contoso 데이터만 사용해. 과거 실패, 질문, 정답 기준, judge 대조군을 수정하지 마.

## 먼저 읽을 근거와 수정 내용

1. `validation/english/automated-v4/report.json`, `quality.json`, `optimizer.json`, `dev37-diagnosis.json`
2. `validation/english/automated-v4/attempts/initial-dev/`
3. `validation/english/citation-remediation/report.json`
4. `samples/request_contract.py`, `samples/hosted_runtime.py`, `samples/business_checks.py`, `scripts/share_evidence.py`
5. `tests/test_request_authorization.py`, `tests/test_quality_revision.py`, `tests/test_live_v4_evidence.py`

이전 live: 두 프로토콜 버전 3의 smoke와 judge 대조군 8/8은 통과했지만 dev는 36개 응답 뒤 37번에서 인용 검사 오류로 중단됐다. 나머지 세 사례와 새 holdout은 실행하지 않았다. Optimizer는 647초 후 service `succeeded`였지만 40건 중 평가 오류 3건으로 운영 실패였다. 당시 생성 세션 5개는 모두 중지 확인했다.

현재 로컬 수정은 `explicit-request-v2`다. 승인된 환율과 순수한 초안 금지 문구를 구매 승인/실행 판단으로 오인하지 않도록 분리했다. 명시적인 일반 가격 조회를 허용하며, 도구 schema에 없는 SKU는 실제 읽기 전용 검증 오류를 모델에 전달한다. 기존 v1 증거는 v1 규칙으로 재검사한다. 필수 인용 자동 보충이나 게이트 완화는 하지 않았다. 이 수정본은 아직 Azure에서 검증하지 않았다.

## 새 실험 준비 — 생략하지 마

현재 CLI 기본 suite와 일부 경로는 여전히 `automated-v4`다. 수정 후 현재 소스는 기존 v4 freeze와 다르므로 v4 live 수집/새 Optimizer 제출이 차단되는 것이 정상이다. 그 검사를 우회하거나 v4 manifest를 다시 쓰지 마.

- 원래 v4 동결 소스 27개는 `validation/english/automated-v4/source-snapshot.zip`에 원래 해시 그대로 보존돼 있다.
- 새 `automated-v5` 실험을 준비하고 필요한 suite 선택, CLI/CI, 빌드, fingerprint, 증거 export 경로를 일관되게 연결해.
- 새 v5 응답과 export에는 `explicit-request-v2` 및 실제 인용/도구 증거가 유지돼야 해. v1 규칙은 과거 원본의 재검사에만 사용하고, 새 후보를 v1로 기록하지 마.
- v5 dev는 노출된 v4 dev 40건의 질문·oracle를 그대로 계승하고 origin을 기록해. 8개 judge 대조군과 native 기준 4/5, 전체 90% 이상, safety/access 실패 0, 누락·평가 오류 불허 조건을 유지해.
- 로컬 회귀 검사를 완료한 새 후보의 코드·프롬프트·정책·dev·judge를 동결해. 그 뒤 별도 작성 컨텍스트에서 새 독립 holdout 10건을 작성·봉인하고, 개발/Optimizer에는 노출하지 마. 기존 미사용 v4 holdout을 열거나 이름만 바꿔 새 시험지로 만들지 마.
- 로컬 검사를 Azure 성공 증거로 기록하지 마. 추가 수정이 필요하면 먼저 분석하고 회귀 검사를 추가해.

## 기존 영어 환경에서만 실행

- 소유 RG: `rg-contoso-en-260930ae24ba`
- 프로젝트: `contoso-workshop-en`
- endpoint: `https://ai-contoso-en-260930ae24ba.services.ai.azure.com/api/projects/contoso-workshop-en`
- azd 환경: `contoso-en-260930ae24ba`
- 이전 격리 실행 폴더: `.build/english-v4-live/Contoso-Foundry-Hands-on-2026-09-30/`
- 그 폴더의 `.env`, 선택된 `.azure` 환경, `results/azure-environment.json`·`search.json`은 같은 영어 환경의 비공개 설정/소유권 기록이다. 원본은 수정하지 말고 새 격리 실행 폴더에서 동일 소유 범위를 재확인해. 루트의 한국어 설정과 혼합하지 마.
- 모델은 기존 `contoso-chat`, `contoso-judge`, `contoso-embedding`, `contoso-reflection`만 사용하고 실제 배포 모델/버전을 확인해. azd 명령에는 프로세스 한정 `AZURE_DEV_USER_AGENT=microsoft_foundry_skill`을 사용해.

## 이번 live 한도와 순서

1. 새 후보를 Invocations/Responses에 각각 한 번 배포하고 각 프로토콜에서 smoke 한 번만 실행해.
2. native judge 대조군 8건을 통과한 뒤 dev 40건 전체를 실행·평가해. 수집은 split당 최대 1200초, native 평가 run은 최대 600초로 제한해.
3. 전체 dev가 완료되고 고정된 business gate를 통과했을 때만 새 holdout 10건을 한 번 실행해. 실패·불완전이면 holdout을 열지 말고 원본을 보존해.
4. Optimizer는 dev만 사용한 job 한 건, 최대 2후보·1 stall·1200초로 제한해. 취소 확인 최대 90초, 소유 세션 정리 최대 180초를 적용하고 자동 후보 적용/승격은 하지 마.
5. 모델 호출 단계는 순차 실행해. 예산 연장, 반복 재배포, 실패 사례만 재샘플링해 합격으로 만드는 작업은 하지 마.
6. 작업 목록 API가 다시 HTTP 500이면 숨기지 마. 기록된 정확한 job ID와 소유 세션을 좁게 확인하고 프로젝트 전체 무활동을 주장하지 마.

## 종료 및 산출물

- 실제 생성한 세션/job의 종료·중지를 소유권 기록과 새 SDK readback으로 확인해. 목록 누락, 잘못된 소유권, 중지 미확인은 명시적인 미완료로 남겨.
- service `succeeded`나 “perfect scores” 문구 대신 native 전체 행 수, errored/skipped, 실제 도구·인용 근거를 확인해.
- 새 결과는 `validation/english/automated-v5/` 등 새 경로에 보존하고, 한·영 25개 모듈의 HTML/Markdown/PDF/ZIP을 체크인 소스로 갱신해. 문서 검증도 새 폴더에 기록해.
- 비용 조회, 선택 기능 검증, Azure 자원 삭제, 조직 정책/권한 변경, main 머지, 저장소 공개 범위 변경, Pages 게시를 하지 마.
- 외부 로그 workspace 문제는 관리자 확인 대기다. 승인 없이 수정하거나 외부 자원을 조회하지 마.
- 한국어로 실제 통과/실패, 실행 건수, 미실행 범위, cleanup 상태와 보고서 경로를 간결하게 알려줘. 성공을 보장하거나 실패를 합격으로 바꾸지 마.
