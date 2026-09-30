# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · **[English — 기본 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)**

합성 Contoso 구매 도우미로 모델·지식·도구·평가·운영을 배우는 **한·영 25개 모듈과 참고 자료 5개**입니다.
한국어 판은 기존 실제 포털 화면 17장과 명령 120개를 유지합니다. 영어 판은 새 영어 환경에서 촬영한 화면 18장과 영문 데이터용 명령 124개를 제공합니다.
기본 언어는 영어이며 상단 언어 전환으로 같은 모듈의 한국어 판을 열 수 있습니다. 학습 진도·테마·학습 경로는 두 언어가 공유합니다.

## 시작하기

처음에는 가이드의 **L00 시작하기**부터 진행하세요. 기본 코스는 **L00–L12, 약 5시간 20분**이며 심화 L13–L24는 필요한 기능을 선택합니다.
가이드 열람에는 설치·로그인이 필요 없습니다. Azure 실습 준비와 비용·권한 조건은 L01에서 확인합니다.

| 형식 | 최신 자료 |
| --- | --- |
| 영어 웹 · 기본 | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| 한국어 웹 | [GitHub Pages 한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| 텍스트 | [GUIDE.ko.md](GUIDE.ko.md) |
| 인쇄 | [PDF 다운로드](Contoso-Foundry-Hands-on-2026-09-30.pdf) |
| 전체 실습 키트 · 두 언어 포함 | [ZIP 다운로드](Contoso-Foundry-Hands-on-2026-09-30.zip) |
| 문서 이해용 합성 영수증 | [GitHub Pages에서 HTML 열기](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) |

오프라인에서는 ZIP을 **압축 해제한 뒤** 영어 `index.html` 또는 한국어 `index.ko.html`을 엽니다. 폴더 구조를 유지하세요.
실제 코드·설정은 GitHub 파일 목록이나 VS Code의 **파일 → 폴더 열기**에서 확인할 수 있습니다.

## 파일 구성

| 경로 | 내용 |
| --- | --- |
| `docs/`, `docs/en/`, `content/` | 한·영 모듈 원문·학습 경로·공식 출처·언어별 UI·스크린샷 정보 |
| `assets/` | 가이드 화면·그림·포털 스크린샷 |
| `samples/`, `hosted/`, `data/` | 실습 코드·에이전트 실행기·합성 데이터 |
| `.env.example`, `azure.yaml`, `infra/` | 환경 설정 템플릿·배포 정의 |
| `scripts/`, `tests/` | 문서 생성·패키징·회귀 검사 |
| `validation/` | 종류별 최신 검증 결과 |

**합성 데이터만 사용하며 실제 주문·결제·업무 승인은 수행하지 않습니다.**
명령마다 실행 범위가 다르므로 가이드의 비용·변경 설명을 먼저 읽고, `.env`·인증 정보·개인 실행 결과는 커밋하지 마세요.
기존 한글 데이터·명령·포털 화면은 보존합니다. 새 영어 실습은 별도 체크아웃에서 `FOUNDRY_LAB_LANGUAGE=en`을 명시해 `data/en/`과 독립적인 `.env`·`.azure/`·`results/`를 사용합니다. 다른 환경의 소유권 기록을 재사용하지 마세요.

## 검증 결과

[한국어 Azure 실행 보고서](validation/current/report.json) · [한국어 자동 품질 기록](validation/automated-v3/quality.json) · [최신 영어 v5 결과](validation/english/automated-v5/report.json) · [최신 문서 검사](validation/docs/live-v5/browser.json)

**새 영어 실행은 별도 결과입니다.** 기본 학습 평가 10/10, Hosted dev 29/30이지만 독립 holdout은 **7/10, 중대 안전 근거 실패 1건으로 릴리스 품질 게이트를 통과하지 못했습니다.** 기준 완화나 holdout을 본 뒤 재조정·재실행은 하지 않았습니다. [영어 실행 보고서](validation/english/current/report.json)와 [영어 품질 결과](validation/english/automated-v3/quality.json)를 확인하세요.

**최신 영어 v5 live도 릴리스 통과는 아닙니다.** 두 프로토콜 버전 4의 smoke와 judge 대조군 8/8은 통과했고, dev 40건을 한 번씩 수집·native 평가했습니다. Native는 40/40·오류/누락 0이지만 실제 인용·도구 근거를 합친 결과는 **39/40(97.5%)**입니다. `v5-dev-30`의 **access 필수 근거 누락 1건** 때문에 고정된 critical 실패 0 기준을 통과하지 못했고, 독립 holdout은 **0/10 실행·봉인 유지**입니다. [품질 원본](validation/english/automated-v5/quality.json), [실패 분석](validation/english/automated-v5/dev30-diagnosis.json), [Optimizer 결과](validation/english/automated-v5/optimizer.json), [세션·job 정리](validation/english/automated-v5/operations.json)를 구분해서 확인하세요. 보고서의 main 머지·Pages 게시가 에이전트 품질 승인이나 후보 자동 승격을 의미하지는 않습니다.

`explicit-request-v2`는 기존 v4와 분리한 **34개 소스 동결**로 배포했습니다. 노출된 v4 dev 40건과 judge 대조군 8건은 질문·정답 기준을 유지했고, 동결 후 별도 작성 컨텍스트에서 새 holdout 10건을 봉인했습니다. 과거 중단 지점인 환율 사례도 이번에는 응답을 완료했지만, 새 실패를 합격으로 바꾸거나 재샘플링하지 않았습니다.

Optimizer는 dev-only job 한 건을 실행해 **647초** 후 service `succeeded`로 종료됐지만, native **38 통과·1 실패·1 오류** 때문에 `operational_failure`입니다. 새 후보·승격은 0이며 제한 시간 연장이나 재제출은 없었습니다. 새 SDK readback으로 **생성 세션 5개 전부 중지**, 해당 job과 native run들의 종료를 확인했습니다. Responses 에이전트 한정 작업 목록 조회는 성공했지만 프로젝트 전체 무활동을 주장하지 않습니다.

**이전 기록은 그대로 보존했습니다.** [v4 live](validation/english/automated-v4/report.json)의 dev 36건 뒤 중단, Optimizer 평가 오류 3건, 당시 세션 5개 중지와 작업 목록 HTTP 500 기록은 바뀌지 않았습니다. v4 미사용 holdout·27개 동결 소스·v1 원본 재검사 규칙도 유지합니다. [선행 로컬 수정 기록](validation/english/citation-remediation/report.json)은 당시 로컬 작업만 기록하며, 새 Azure 결과는 v5 경로에만 있습니다. 비용 조회·선택 기능·정책/권한 변경·Azure 자원 삭제는 이번에도 수행하지 않습니다.

현재 파일 목록에는 종류별 최신 결과만 둡니다. 이전 기록은 [정리 전 Git 커밋](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/faa5ec26f15cfeb38f69de4036acedc3151c3df4/validation)에서 원본 그대로 볼 수 있습니다.
검증 기록 안의 과거 경로는 해당 실행 당시의 커밋 기준입니다. 문서·로컬 검사 통과를 새로운 Azure 실행이나 품질 통과로 해석하지 않습니다.

## 수정·재생성

`docs/`·`docs/en/`와 `content/`의 두 언어 소스를 함께 수정한 뒤 생성합니다. HTML·통합 Markdown은 직접 수정하지 않습니다.
Python 문서 의존성(`requirements-docs.txt`, `requirements-qa.txt`)과 Node.js/Playwright Chromium이 필요합니다.

```bash
python -m pip install -r requirements-docs.txt -r requirements-qa.txt
npm ci
npx playwright install chromium
python scripts/build_guide.py
python -m unittest discover -s tests -q
npm run guide:pdf
python scripts/check_guide.py --report-dir validation/docs/live-v5
npm run guide:browser -- --report-dir validation/docs/live-v5
python scripts/check_pdf.py --report-dir validation/docs/live-v5
python scripts/package_guide.py --report-dir validation/docs/live-v5
```

각 명령은 두 언어를 함께 생성·검사합니다. 최신 문서 보고서는 `validation/docs/live-v5/`에 저장하며, `validation/docs/citation-remediation/`·`validation/docs/live-v4/` 등 이전 검사 기록은 덮어쓰지 않습니다. 이후 독립적인 후속 작업에는 새 보고서 디렉터리를 선택합니다.
기존 Azure 검증은 재실행 없이 보존하고, 재현·회귀에 필요한 버전별 프롬프트와 시험지는 유지합니다.

Pages는 PR 브랜치와 분리한 **`gh-pages` 브랜치의 루트**에서 게시합니다. PR 병합 후 기능 브랜치를 삭제해도 사이트는 유지됩니다. `.nojekyll`을 유지하고 산출물 재생성·검사 후 `git push origin HEAD:gh-pages`로 검토한 커밋을 게시하세요. 게시 브랜치를 강제 푸시하거나 삭제하지 않습니다. `main` 병합과 리포 공개 범위 변경은 별도 승인 대상입니다.
모든 가이드 HTML은 위의 GitHub Pages 링크로 열 수 있으며, 파일 간 상대 링크는 Pages의 리포 경로와 압축 해제한 오프라인 키트에서 모두 동작합니다.
게시 후 `python scripts/check_pages.py`로 모든 공개 HTML과 연결 파일이 로컬 원본과 일치하는지 확인합니다. 이 검사는 해당 리포의 GitHub Pages만 비인증 조회하며 Azure는 호출하지 않습니다.

이 자료는 Microsoft 공식 교육과정이 아닙니다. 출처와 사용 조건은 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)를 참고하세요.
