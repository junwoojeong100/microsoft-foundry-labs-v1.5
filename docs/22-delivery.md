> **완성할 결과:** 코드 변경이 곧 운영 변경이 되지 않도록 검사·평가·승인·롤백을 연결합니다.

## 목표

코드뿐 아니라 **모델, agent, 도구, 지식, evaluator, dataset 버전**을 함께 관리합니다.

## 준비

L08의 평가 게이트, L14의 hosted 프로젝트 또는 버전 관리되는 prompt agent, 비운영/운영 분리가 필요합니다. 실제 CI/CD의 OIDC federation·role assignment는 관리자 작업입니다.

## 실행

### 1. 릴리스 경로 만들기

```text
변경 제안
 → 로컬 계약 테스트
 → 비운영 배포
 → smoke test
 → 대표 데이터 평가 + 권한/안전 검사
 → 사람 승인
 → 운영 active version 전환
 → 모니터링
 → 실패 시 이전 승인 버전으로 복구
```

응답 파일이 비어 있지 않다는 조건은 smoke test일 뿐입니다. **에러 로그가 들어 있어도 파일은 비어 있지 않을 수 있습니다.** 실제 response 상태·출력 schema·기대 행동을 검사합니다.

### 2. 제공 키트의 로컬 검사를 재현하기

```bash
python -m unittest discover -s tests -v
python samples/workshop.py validate-data
python samples/workshop.py score --input results/실제-검토파일.jsonl
```

마지막 명령은 실제로 검토한 20건이 있을 때 실행합니다. dummy 응답으로 통과 파일을 만들어 출시 근거로 사용하지 않습니다.

이 폴더의 `.github/workflows/validate.yml`은 문서와 로컬 테스트만 검사합니다. **Azure 배포·유료 추론을 자동 실행하지 않습니다.**

### 3. 조건부: Hosted CI/CD 연결하기

동봉 `.github/workflows/azure-validation.yml`은 **수동 dispatch / 명시적 재사용 호출 전용**입니다.
일반 push·PR에는 유료 Azure job이 없습니다. `acknowledge_cost=true`와
`contoso-validation` GitHub Environment 승인을 통과한 실행만 배포합니다.
기존 `.github/workflows/validate.yml`은 계속 자동 로컬 검사를 수행합니다.

관리자는 새 테스트 RG의 workload identity에 최소 역할을 부여하고,
federated credential의 subject를 **Actions가 실제 발행한 A의 environment-bound `sub`**로 제한합니다.
최근 형식은 owner/repository의 immutable ID를 이름 뒤에 `@ID`로 포함할 수 있습니다.
과거 `repo:owner/repo:environment:name` 문자열을 그대로 가정하지 않습니다.
audience는 `api://AzureADTokenExchange`입니다. client secret을 만들지 않습니다.
identity는 프로젝트 Foundry User, 필요한 배포/읽기 권한만 받으며 CI가 RBAC를 스스로 확대하지 않습니다.

관리자용 명령은 `python scripts/setup_oidc.py --branch 실제-feature-branch --subject "확인한-sub-claim" --live`입니다.
새 RG의 user-assigned identity, environment-bound federated credential,
새 GitHub Environment와 해당 branch policy를 함께 기록합니다.
기존 환경/identity가 있으면 충돌로 중단하며, tenant 전체 앱 권한을 부여하지 않습니다.
AADSTS700213이면 issuer·audience·subject를 로그의 비밀이 아닌 claims와 대조합니다.
`--repair-subject`는 이번 receipt의 FIC만 보정하며, GitHub 전체 OIDC 정책은 변경하지 않습니다.

Environment variables는 workflow `env` 목록의 client/tenant/subscription/project ID 및
모델·Search endpoint/index/KB입니다. 비밀이 아닌 구성값만 등록하고 인증 토큰·전체 `.env`·
원시 실행 결과를 artifact로 올리지 않습니다.

```bash
gh workflow run validate.yml --ref 승인된-작업브랜치 -f acknowledge_cost=true
```

`validate.yml`은 기존 기본 브랜치에 있는 수동 진입점입니다. 승인한 작업 브랜치의
동일 파일이 로컬 검사를 마친 뒤 재사용 Azure workflow를 호출하므로,
새 workflow를 main에 먼저 merge할 필요가 없습니다.
GitHub 정책으로 수동 브랜치 실행이 막히면 차단으로 기록하며 main을 임의 merge하지 않습니다.
`scripts/ci_live.py`는 OIDC 주체와 RG/project 일치를 확인하고 Hosted를 배포하여
**290만원 초안·두 승인 역할·미주문**을 실제 tool result로 검사합니다.
이후 judge 대조군과, 제공된 실제 holdout 응답의 native 평가를 수행합니다.
holdout은 환경 fingerprint·runtime hash·실제 모델이 현재 테스트 환경과 같아야 사용합니다.
다른 환경의 제작자 결과를 자신의 CI 품질 근거로 재사용할 수 없습니다.
calibration 실패 후에도 독립적인 holdout 증거를 수집할 수 있지만 **릴리스 게이트는 실패**입니다.
smoke 성공은 전체 holdout 품질 게이트와 별개입니다. `always()` 단계는 기록된 세션만 stop합니다.
원시 증거는 `results/`, 공유 가능한 최소 요약은 `validation/current/ci.json`으로 분리합니다.

### 4. 모델 업그레이드와 지식 변경 검사하기

| 변경 | 같이 재검사 |
| --- | --- |
| 모델 버전/auto-update | 응답 형식·도구 선택·지연·비용 |
| model router pool/subset | 허용 모델·품질·fallback·context |
| 지식 문서/index | 정확도·citation·삭제·권한·freshness |
| tool schema/endpoint | 호출 인수·인증·오류·중복 행동 |
| instructions/skills | regression·안전 경계 |
| evaluator/judge | 점수 의미·판정 일관성 |

모델 retirement 공지를 확인하고 충분한 기간에 대체 모델을 비교합니다. 같은 agent version이라도 router pool이나 외부 데이터가 변하면 행동이 달라질 수 있습니다.

### 5. 비용 계산표 만들기

개략적 추론비:

```text
입력 토큰 / 1,000,000 × 입력 단가
+ 출력 토큰 / 1,000,000 × 출력 단가
+ 평가 judge·검색·도구·음성/영상·로그·hosted runtime
+ 고정 용량·예약·스토리지 비용
```

가격은 실행 시 지역·통화·계약·모델별 가격표를 사용합니다. 캐시 할인·reasoning token·router·Batch 등의 과금 규칙도 확인합니다. 이 가이드는 “1인당 반드시 몇 달러”라는 고정 비용을 보장하지 않습니다.

### 6. 장애 훈련하기

도구 timeout, 429, 잘못된 연결, 단일 backend 장애를 비운영 환경에서 가정합니다. 중단·재시도·fallback·사람 인계가 어떻게 동작할지 기록합니다.

재시도는 제한된 횟수와 backoff/Retry-After를 사용하고, 비멱등 작업은 blindly retry하지 않습니다. 다지역 복구는 데이터를 허용되지 않은 지역으로 보내지 않아야 합니다. RTO/RPO를 조직 목표로 정하고 실제 훈련으로 측정합니다.

## 성공 기준

릴리스 버전 묶음·평가 기준·승인자·rollback 대상·비용 담당자·장애 대응 경로가 있습니다. CI 성공과 업무 품질 통과를 구분합니다.

## 막혔을 때

개발 환경에서는 되는데 CI에서 안 되면 OIDC subject, environment, identity 역할, 네트워크 접근, SDK/CLI 버전 차이를 확인합니다. 로그에 토큰이나 전체 환경 값을 출력하지 않습니다.

## 정리

불필요한 staging deployment, 지속 평가, 임시 federated credential과 권한을 담당자와 정리합니다.
