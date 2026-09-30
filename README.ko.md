# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · **[English — 기본 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)**

합성 Contoso 구매 도우미로 모델·지식·도구·평가·운영을 배우는 **한·영 25개 모듈과 참고 자료 5개**입니다.
실제 포털 화면 17장과 CLI 명령 120개의 개별 해설을 제공합니다.
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
번역은 실습 코드를 변경하지 않습니다. 실행 명령의 한글 입력·자리표시자, 합성 데이터와 원본 포털 화면은 재현성을 위해 보존합니다.

## 검증 결과

[마지막 Azure 실행 보고서](validation/current/report.json) · [최신 자동 품질 결과](validation/automated-v3/quality.json) · [최신 문서 검사](validation/docs/browser.json)

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
python scripts/check_guide.py
npm run guide:browser
python scripts/check_pdf.py
python scripts/package_guide.py
```

각 명령은 두 언어를 함께 생성·검사합니다. 문서 검사·패키지 보고서의 기본 저장 위치는 `validation/docs/`입니다.
기존 Azure 검증은 재실행 없이 보존하고, 재현·회귀에 필요한 버전별 프롬프트와 시험지는 유지합니다.

Pages는 **`docs/bilingual-guide` 브랜치의 루트**에서 게시합니다. `.nojekyll`을 유지하고 해당 브랜치에 재생성한 산출물을 푸시하면 사이트가 갱신됩니다. `main` 병합과 리포 공개 범위 변경은 별도 승인 대상입니다.
모든 가이드 HTML은 위의 GitHub Pages 링크로 열 수 있으며, 파일 간 상대 링크는 Pages의 리포 경로와 압축 해제한 오프라인 키트에서 모두 동작합니다.
게시 후 `python scripts/check_pages.py`로 모든 공개 HTML과 연결 파일이 로컬 원본과 일치하는지 확인합니다. 이 검사는 해당 리포의 GitHub Pages만 비인증 조회하며 Azure는 호출하지 않습니다.

이 자료는 Microsoft 공식 교육과정이 아닙니다. 출처와 사용 조건은 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)를 참고하세요.
