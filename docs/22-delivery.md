> **이 모듈에서 만드는 것:** 다른 사람이 같은 소스로 읽고 실행할 수 있는 실습 패키지와 안전한 변경·전달 절차입니다.

## 목표

학습 가이드는 **기본 v1·개선 v2·최신 결과 한 묶음**으로 이해할 수 있게 유지합니다.
문서 배포와 에이전트 품질 승인은 다르며, 수정할 때마다 유료 검증이나 새 실험 번호를 만들지 않습니다.

## 개념과 실습 지도

**경험할 기능:** 로컬 CI, GitHub Actions, OIDC의 역할, 배포·롤백, 비용과 리소스 수명 관리입니다.

**무엇이며 왜 중요한가요?** CI는 동일 소스의 문서·데이터·코드 오류를 찾습니다.
CI 성공만으로 Azure를 실행했거나 모델 품질이 좋아졌다고 판단할 수 없습니다.

**어떻게 사용하나요?** 지침은 v2 파일에서 개선하고, L08의 한 번 비교를 근거로 설명합니다.
현재 파일 목록에는 최신 원본만 두며 이전 실패·질문·기준은 Git 이력에서 찾을 수 있게 보존합니다.

**어디서 실행하나요?** [validate.yml](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/validate.yml)은 기본 로컬 검사,
[azure-validation.yml](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/blob/main/.github/workflows/azure-validation.yml)은 별도 승인 실행 예제입니다.
현재 실습의 빠른 경로는 터미널과 GitHub Actions의 **offline/SDK 검사**입니다.

## 준비

L01의 환경과 저장소 소스가 필요합니다. 패키지에는 `.env`, 토큰, `.azure/`, `results/`, 가상환경을 넣지 않습니다.
영어와 한국어는 같은 코드와 각 언어의 합성 데이터·지침을 사용합니다.

## 실행

### 1. 소스에서 가이드 만들기

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서와 명령 | 하는 일과 옵션 | 결과·비용·변경 |
| --- | --- | --- |
| 1. `build_guide.py` | 두 언어의 Markdown 원본과 메타데이터로 HTML/Markdown을 생성합니다. | 로컬 파일만 생성합니다. 생성물을 손으로 수정하지 않습니다. |
| 2. `FOUNDRY_LAB_LANGUAGE=ko ... unittest ... -q` | 공유 테스트는 한국어 기본값과 별도의 영어 검사로 실행합니다. `-q`는 간결한 출력입니다. | 로컬 검사이며 새 Azure 성공이나 점수 향상이 아닙니다. |
| 3. `check_guide.py` | 25개 모듈, 명령 해설, 링크, 화면 출처를 확인합니다. | 최신 문서 검사만 `validation/docs/`에 둡니다. |

</div>

PDF와 ZIP은 README의 생성 명령으로 같은 소스에서 만듭니다. [최신 상태](../validation/current/instructions.json)는
현재 국문·영문 GPT-6 Sol 실측과 그 동점 결과·보존된 형식 오류를 구분해 보여 줍니다.
생성된 Markdown·PDF·ZIP은 루트의 `downloads/`에 모으며, 웹 진입점 `index.html`과 `index.ko.html`은 Pages 경로를 위해 루트에 유지합니다.

### 2. GitHub Actions에서 같은 검사 확인하기

push/PR의 기본 workflow는 offline/SDK 검사입니다. 유료 Azure workflow는 명시적 opt-in 없이 실행하지 않습니다.
저장소 병합이나 Pages 게시 역시 별도 승인 동작입니다. 게시했다고 실패한 품질 판정을 통과로 바꾸지 않습니다.

필요할 때만 OIDC를 검토합니다. 이는 저장된 장기 비밀 대신 workflow identity로 인증하는 방법입니다.
`repository_id`, 실행 branch/environment, tenant·subscription·project, 최소 역할을 대조하고 다른 사람의 환경이나 권한을 재사용하지 않습니다.
이 학습 비교를 위해 새 identity, 역할, Environment 정책을 만들 필요는 없습니다.

### 3. 배포와 롤백 구분하기

| 대상 | 유지할 정보 |
| --- | --- |
| 지침 | v1 기준선, 현재 v2, 실제 사용한 파일 해시 |
| 실행 | 실제 response/trace ID와 사용한 모델·데이터 |
| 배포 | 서비스가 발급한 실제 agent version; 지침의 v1/v2와 다른 식별자 |
| 전달물 | 소스와 일치하는 HTML/Markdown/PDF/ZIP |

서비스 배포 ID나 원본 증거의 식별자를 “v2”로 바꾸어 쓰지 않습니다. 문서에는 지침 v2라는 단순한 이름을 유지하되,
실제 결과의 식별자와 해시는 원래대로 남깁니다. 배포 변경·롤백에는 대상과 승인 범위를 다시 확인합니다.

### 4. 비용과 수명 이해하기

![운영 모니터 화면. 요청·오류·사용량과 실제 품질 판정을 구분합니다.](../assets/portal/07-monitor.png)

모델 호출, Search, Hosted compute, 보관 데이터는 서로 다른 비용 원인입니다.
세션 중지는 리소스 삭제나 전체 비용 0을 뜻하지 않습니다. 비용 데이터가 비어 있어도 무료였다고 판단하지 않습니다.
실제 비용 조회·추가 기능 실행·삭제는 각각 승인된 범위에서만 수행합니다.

## 성공 기준

다른 사람이 ZIP을 풀어 두 언어의 25개 모듈을 읽고, 같은 v1/v2 비교 계획을 확인할 수 있습니다.
최신 원본·현재 지침·로컬 검사·Azure 실행·품질 판정을 혼동하지 않고 설명할 수 있습니다.

## 막혔을 때

`.env`와 언어 profile, 누락된 의존성, 생성 소스와 결과물의 차이를 먼저 확인합니다.
CI 실패를 숨기거나 유료 검증의 기준을 낮추지 않습니다. 과거 로그를 새 실행 결과로 복사하지 않습니다.

## 정리

개인 설정과 원시 응답은 `results/`에 두고 최신 검토 원본만 공유합니다.
Git 이력은 재작성하지 않으며, Azure 리소스 삭제는 이 모듈의 기본 동작이 아닙니다.
