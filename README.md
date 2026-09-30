# Microsoft Foundry, 직접 만들며 이해하기

**2026-09-30 Contoso 독립형 실행 가이드 · 한국어 · 25개 실습 모듈**

**온라인 가이드: [GitHub Pages에서 바로 읽기](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)**

**[`index.html`](index.html)을 브라우저에서 여세요.** 설치 없이 목차·검색·학습 경로·진도 체크를 사용할 수 있습니다. 외부 CDN, 로그인, 분석 추적 없이 동작합니다. 인쇄 버튼으로 현재 모듈 또는 전체 가이드를 PDF로 저장할 수 있습니다.

GitHub 또는 텍스트로 읽을 때는 **[`GUIDE.ko.md`](GUIDE.ko.md)** 를 사용하세요. 처음이라면 웹 가이드의 **L00 시작하기**부터 진행합니다.

가이드와 실제 실습 코드·설정은 같은 저장소에 있습니다. 사용할 브랜치의 **전체 폴더**를 받거나 아래 ZIP을 사용하세요.
GitHub에서는 파일 목록, 로컬에서는 VS Code의 **파일 → 폴더 열기**로 `samples/`, `hosted/`, `.env.example`, `azure.yaml`을 확인합니다.
HTML만 한 파일 다운로드하면 그림·원본 코드·데이터가 빠집니다.

각 모듈의 **개념과 실습 지도**에서 경험할 기능·뜻·중요성·사용 흐름·실행 위치를 먼저 읽습니다.
실제 Foundry 포털 화면에는 관찰 순서와 주의점을 붙였고, **55개 실행 블록의 120개 CLI 명령**에는
각각 동작·옵션·결과·비용/변경을 설명했습니다. 포털만으로 모든 실습이 끝난다는 뜻은 아니며,
코드가 필요한 단계는 명확히 구분합니다. 명령을 복사하기 전에 바로 아래 **명령 해설**을 읽으세요.

공유·인쇄본은 **[`Contoso-Foundry-Hands-on-2026-09-30.pdf`](Contoso-Foundry-Hands-on-2026-09-30.pdf)**,
전체 키트는 **[`Contoso-Foundry-Hands-on-2026-09-30.zip`](Contoso-Foundry-Hands-on-2026-09-30.zip)**입니다.
ZIP을 받은 경우 먼저 압축을 풀고, 그 안의 `index.html`을 여세요. ZIP 안에서 파일 하나만 열지 않습니다.
과거 2026-09-29 산출물/검증 원본은 과거 기록이며 Contoso 신규 결과가 아닙니다.

## 무엇을 완성하나요?

가상의 **Contoso 구매·정책·재고·구매 요청 초안 도우미**를 만듭니다.
규정을 인용하고 재고를 조회하며 **초안에서 멈춥니다**. 실제 주문·결제·업무 승인·메일 발송은 없습니다.
노트북 상한 150만원, 재고 단가 145만원, 총액 **200만원 초과** 시 두 승인 역할이라는 A의 업무 규칙을 유지합니다.

**이 저장소만 있으면 됩니다.** B는 제작 시 한 번 참고한 MIT 자료일 뿐이며,
설치·학습·실행·빌드·패키징·CI에서 clone/접근/다운로드하지 않습니다.
출처·라이선스는 [`THIRD_PARTY_NOTICES`](THIRD_PARTY_NOTICES)에 보존합니다.

**보존된 v1 검증 결과:** 새 Azure RG에서 Hosted·Search/IQ·도구·Memory·A2A·평가·Tracing과
[OIDC 배포·업무 검사](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/actions/runs/36649656044)를 수행했습니다.
최종 holdout은 **9/10이나 safety 사례의 필수 인용 누락으로 품질 게이트 미통과**입니다.
실행 성공과 릴리스 품질을 구분하며, Routine history 미확인·optimizer 신규 후보 0도 그대로 기록했습니다.

**현재 자동 검증은 `automated-v3`입니다.** 검색과 명시 SKU 조회를 서버가 먼저 실행하고, 모델이 선택한 실제 인용·도구 결과/정의를
코드로 검사합니다. 노출된 v1/v2 30건은 dev 회귀로 보존하고 별도 봉인 holdout 10건을 사용합니다.
사람 검토는 운영 전 권장 안내이며 이 합성 실습의 자동 완료 조건이 아닙니다.
기존 90%·safety/access 실패 0건 기준과 과거 실패 결과는 유지합니다.

**현재 자동 품질 게이트는 통과했습니다:** dev 29/30, 독립 holdout 9/10, critical 실패 0건,
calibration 8/8입니다. 통과하지 못한 비중대 사례도 [현재 품질 결과](validation/automated-v3/quality.json)에 남겨 둡니다.
이 결과는 모든 답변이 완벽하거나 실제 운영 승인을 받았다는 뜻은 아닙니다.

| 학습 경로 | 범위 |
| --- | --- |
| 90분 핵심 체험 | 강사가 Azure 환경을 준비한 경우의 축약 코스 |
| 기본 코스 | L00–L12, 약 5시간 20분 + 대기·휴식 |
| 심화 코스 | L13–L24, 순수 7시간 20분. 독립·선행 필요·기능별 분기 표시를 보고 선택 |
| Azure 없는 연습 | 데이터 검사, 도구 실행, 평가 게이트, 아키텍처 설계 |

기본은 **L00부터 L12까지 순서대로** 진행합니다. L08 기본 평가는 L05/L06 결과를 사용하므로 심화를 먼저 할 필요가 없습니다.
심화의 핵심 연결은 **L13 → L14 → {L20 Hosted Optimizer 또는 L22 CI/CD}**이며 나머지는 각 장의 준비 조건에 따라 선택합니다.
총 순수 학습 시간은 **12시간 40분**, 실제 교육 일정은 준비된 환경 기준 **2~3일**을 권장합니다.
조건부 학습 작업·관리자 승인·장치 설치는 별도 대기 시간이 추가될 수 있습니다.

**현재 상태를 정확하게 구분합니다.** 새 포털의 GA와 개별 기능의 GA는 다릅니다. Foundry IQ는 API와 포털 상태를 구분하며, 종료 예정인 포털 Workflows 대신 Microsoft Agent Framework를 사용합니다. 상태·출처·실습 매핑은 가이드의 **기능 커버리지 / 출처와 최신성**을 참고하세요.

## 로컬 연습부터 시작

Python 3.11 이상에서, 이 폴더를 작업 디렉터리로 사용합니다. 아래 명령은 외부 패키지나 Azure 계정이 필요 없고 네트워크를 호출하지 않습니다.

```bash
python3 samples/workshop.py doctor
python3 samples/workshop.py tools
python3 samples/workshop.py validate-data
python3 -m unittest discover -s tests -v
```

Azure 실습은 L01의 관리자 준비/학습자 경로를 구분합니다.
검증 조합은 **Python 3.13 / azure-ai-projects 2.7.0 / openai 3.18.0 / Azure CLI 2.86.0 / azd 1.34.0**입니다.
개별 실습 CLI는 `--live` 없이는 Azure를 호출하지 않습니다. `azd deploy`와 CI는 별도 명시적 배포 동작입니다.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
# .env의 두 값을 포털에서 복사한 실제 값으로 수정
az login
python samples/workshop.py model --live
```

Windows PowerShell에서는 `py -3.13 -m venv .venv` 후 `.venv\Scripts\python.exe`를 직접 사용해도 됩니다. 실행 정책을 낮출 필요가 없습니다. 환경 변수는 운영체제 환경 변수 > `.env` 순서로 읽습니다. `.env`는 키나 토큰을 보관하는 용도가 아닙니다.

## 구성

| 경로 | 용도 |
| --- | --- |
| `index.html` | 완성된 오프라인 웹 가이드 |
| `GUIDE.ko.md` | 전체 내용의 Markdown 판 |
| `Contoso-Foundry-Hands-on-2026-09-30.pdf` | 표지·목차·책갈피를 포함한 현재 인쇄본 |
| `docs/` | 모듈별 원문 |
| `assets/` | 로컬 스타일·스크립트·직접 제작한 다이어그램 |
| `assets/portal/` | 실제 포털을 Headless Playwright MCP로 촬영한 식별 정보 마스킹 이미지 |
| `content/portal-screenshots.json` | 촬영 시각·화면·마스킹·파일 hash·실행 범위 |
| `data/` | 가상 정책·재고·평가·튜닝·문서 이해 데이터 |
| `samples/` | 안전한 로컬 도구와 명시적으로 실행하는 Azure 예제 |
| `hosted/`, `azure.yaml`, `infra/` | 동봉 Hosted runtime·code deployment·새 RG용 IaC |
| `content/` | 모듈·기능·공식 출처의 구조화된 목록 |
| `scripts/` | 재생성·문서 검사·출처 링크 확인 |
| `tests/` | 로컬 계약·오류 경로·평가 게이트 회귀 테스트 |
| `validation/current/` | 현재 구현/실행/품질/차단/미실행 구분 |
| `validation/automated-v2/` | 이전 v2 자동 검사·실패와 합성 응답 원본 |
| `validation/automated-v3/` | 현재 v3 자동 검사·native 평가·CI 및 합성 최소 응답 |
| `validation/history/v1/` | 공개된 이전 v1 검증 결과의 불변 사본 |
| `validation/guide-refresh-20260930/` | 이번 가이드 개정의 로컬 브라우저·PDF·패키지 검사; Azure 품질 증거 아님 |
| `validation/`의 기존 파일 | 2026-09-29 과거 검증 원본, 수정하지 않음 |

심화 전체를 하나의 긴 순서로 실행할 필요는 없습니다.
각 모듈의 학습 순서 배지와 [강사용 독립·연계 표](docs/instructor.md)를 참고하세요.
`requirements-hosted.txt`/`requirements-tools.txt`는 기본 환경에 추가할 수 있고,
MAF의 `requirements-advanced.txt`는 충돌 방지를 위해 별도 환경에 설치합니다.

## GitHub Pages 게시

이 저장소와 가이드 사이트는 공개입니다. Pages의 게시 소스는
**`docs/portal-walkthrough-20260930` 브랜치의 `/ (root)`**이며, 해당 브랜치에 푸시하면 사이트가 갱신됩니다.
`main`에 자동 병합하지 않습니다. 향후 게시 브랜치를 바꾸려면 저장소의 **Settings → Pages → Build and deployment**에서 변경합니다.

루트의 `.nojekyll`은 이미 생성된 `index.html`과 로컬 자산을 Jekyll로 다시 처리하지 않고 그대로 게시하도록 합니다.
공개 사이트의 경로는 `/microsoft-foundry-labs-v1.5/`이며 이미지·모듈 링크는 이 하위 경로에서도 동작합니다.
Pages에서 제외되는 `.github/`의 workflow 링크는 GitHub 코드 보기로 연결합니다. ZIP에는 원본 workflow 파일도 포함됩니다.
가이드만 읽을 때 GitHub 로그인이나 Azure 인증은 필요 없고, Azure 실습 실행에는 별도 인증·비용 승인이 필요합니다.

인증 파일·`.env`·`results/`·브라우저 세션은 커밋하지 않습니다. 기존 검증의 저장소 비공개 표시는 그 실행 당시의 기록이므로 고치지 않습니다.
가이드 개정의 원본 검사는 `validation/guide-refresh-20260930/`, Pages 준비 이후 새 패키지 기록은 `validation/pages-20260930/`에 구분합니다.

## 가이드를 수정할 때

`docs/`와 `content/`를 수정한 뒤 재생성합니다. 생성된 HTML/통합 Markdown을 직접 수정하지 마세요.
새 CLI 블록에는 바로 이어서 `command-explanation` 표를 넣고 **논리적 명령마다 한 행**을 작성합니다.
포털 이미지는 실제 화면만 사용하고, 계정/식별 정보를 가린 뒤 촬영 출처·시간·hash를 manifest에 기록합니다.
기존 `validation/current/`와 history는 이전 실행의 기록이므로 아래처럼 별도 보고서 경로를 사용합니다.

```bash
python -m pip install -r requirements-docs.txt -r requirements-qa.txt
python scripts/build_guide.py
python scripts/check_guide.py
python -m unittest discover -s tests -v
# 공식 공개 URL만 접속하며 Azure 인증·리소스를 사용하지 않음
python scripts/check_links.py
npm ci
npx playwright install chromium
npm run guide:browser -- --report-dir validation/guide-refresh-20260930
npm run guide:pdf
python scripts/check_pdf.py --report-dir validation/guide-refresh-20260930
python scripts/package_guide.py --report-dir validation/guide-refresh-20260930
```

`build_guide.py`는 HTML/Markdown, `guide:pdf`는 인쇄본, `package_guide.py`는 전체 ZIP을 생성합니다.
`check_guide.py`는 25개 개념 설명·명령별 해설·실제 이미지 manifest·링크를 검사하고,
브라우저/PDF 검사는 화면 크기·그림·한글·인쇄 링크를 확인합니다. `--report-dir`는 **로컬 검사 보고서의 저장 위치**이며 Azure 배포 대상이 아닙니다.
향후 개정은 새로운 경로를 선택해 이 개정의 결과도 보존하세요.

브라우저/PDF 명령은 **headless Chromium**과 loopback 서버를 사용하고 완료 시 종료합니다.
MCP나 B는 필요 없습니다. Playwright headless MCP에서도 동봉 함수 파일을 실행할 수 있습니다.
일반 독자는 서버 없이 `index.html`을 사용합니다. PDF 검사는 `requirements-qa.txt`가 필요합니다.

**검증의 경계:** [`validation/current/report.json`](validation/current/report.json)의 실제 상태가 기준입니다.
로컬/fixture 통과는 Azure 또는 모델 품질 성공이 아닙니다. 실패·빈 응답·부분 실행은 그대로 남기며,
원시 자료는 배포 패키지에서 제외합니다. Voice·CU·Fine-tuning·Foundry Local의 범위도 각 모듈에 명시합니다.
포털 사진은 촬영 시점의 UI 관찰입니다. 기존 평가·trace·비용 화면을 촬영했다고 새 품질 검증을 수행한 것이 아니며,
학습자가 같은 메뉴·모델·버전을 볼 수 있다는 보장도 아닙니다. 이번 촬영의 실제 요청 범위는 `content/portal-screenshots.json`을 확인합니다.
검증 자원은 삭제 승인 전까지 보존하되 예약과 Hosted compute는 종료합니다. Search 등의 상시 비용은 남을 수 있습니다.

이 자료는 Microsoft 공식 교육과정이나 서비스 보증이 아닌 독립적으로 구성한 실습 자료입니다. 제품 설명의 근거는 Microsoft 공개 문서이며, 시나리오·데이터·그림은 본 가이드용으로 작성했습니다.

상단의 Microsoft Foundry 제품 아이콘은 Microsoft 공식 Azure Icons V24의 SVG 원본을
로컬 파일로 포함했습니다. 아이콘의 별도 사용 조건과 출처는 `THIRD_PARTY_NOTICES`를 참고하세요.
