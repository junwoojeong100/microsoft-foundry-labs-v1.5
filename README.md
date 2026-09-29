# Microsoft Foundry, 직접 만들며 이해하기

**2026-09-29 공개 공식 문서 확인본 · 한국어 · 25개 실습 모듈**

**[`index.html`](index.html)을 브라우저에서 여세요.** 설치 없이 목차·검색·학습 경로·진도 체크를 사용할 수 있습니다. 외부 CDN, 로그인, 분석 추적 없이 동작합니다. 인쇄 버튼으로 현재 모듈 또는 전체 가이드를 PDF로 저장할 수 있습니다.

GitHub 또는 텍스트로 읽을 때는 **[`GUIDE.ko.md`](GUIDE.ko.md)** 를 사용하세요. 처음이라면 웹 가이드의 **L00 시작하기**부터 진행합니다.

공유·인쇄용 완성본은 **[`Foundry-Hands-on-2026-09-29.pdf`](Foundry-Hands-on-2026-09-29.pdf)** 입니다. PDF 목차와 책갈피로 각 모듈에 이동할 수 있습니다. 실행 코드와 데이터는 이 폴더의 원본 파일을 사용하세요.

## 무엇을 완성하나요?

가상의 **한빛 오피스 구매·정책 도우미**를 만듭니다. 규정을 근거와 함께 답하고, 재고를 조회하고, 승인 전 구매 초안까지만 작성합니다. 이후 평가·안전·추적·배포·운영을 연결합니다. 실제 주문·결제·메일 발송 기능은 없습니다.

| 학습 경로 | 범위 |
| --- | --- |
| 90분 핵심 체험 | 강사가 Azure 환경을 준비한 경우의 축약 코스 |
| 기본 코스 | L00–L12, 약 5시간 20분 + 대기·휴식 |
| 심화 코스 | L13–L24, 필요한 기능을 골라 진행 |
| Azure 없는 연습 | 데이터 검사, 도구 실행, 평가 게이트, 아키텍처 설계 |

**현재 상태를 정확하게 구분합니다.** 새 포털의 GA와 개별 기능의 GA는 다릅니다. Foundry IQ는 API와 포털 상태를 구분하며, 종료 예정인 포털 Workflows 대신 Microsoft Agent Framework를 사용합니다. 상태·출처·실습 매핑은 가이드의 **기능 커버리지 / 출처와 최신성**을 참고하세요.

## 로컬 연습부터 시작

Python 3.11 이상에서, 이 폴더를 작업 디렉터리로 사용합니다. 아래 명령은 외부 패키지나 Azure 계정이 필요 없고 네트워크를 호출하지 않습니다.

```bash
python3 samples/workshop.py doctor
python3 samples/workshop.py tools
python3 samples/workshop.py validate-data
python3 -m unittest discover -s tests -v
```

Azure 실습은 가이드 L01에서 인증·권한·모델을 준비한 후 진행합니다. `requirements.txt`는 2026-09-29 PyPI에서 확인한 SDK 버전입니다. 모든 Azure 호출은 `--live`를 명시해야 시작됩니다. `--live` 없이 실행하면 계획만 출력합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# .env의 두 값을 포털에서 복사한 실제 값으로 수정
az login
python samples/workshop.py model --live
```

Windows PowerShell에서는 `py -3 -m venv .venv` 후 `.venv\Scripts\python.exe`를 직접 사용해도 됩니다. 실행 정책을 낮출 필요가 없습니다. 환경 변수는 운영체제 환경 변수 > `.env` 순서로 읽습니다. `.env`는 키나 토큰을 보관하는 용도가 아닙니다.

## 구성

| 경로 | 용도 |
| --- | --- |
| `index.html` | 완성된 오프라인 웹 가이드 |
| `GUIDE.ko.md` | 전체 내용의 Markdown 판 |
| `Foundry-Hands-on-2026-09-29.pdf` | 표지·목차·책갈피를 포함한 인쇄용 완성본 |
| `docs/` | 모듈별 원문 |
| `assets/` | 로컬 스타일·스크립트·직접 제작한 다이어그램 |
| `data/` | 가상 정책·재고·평가·튜닝·문서 이해 데이터 |
| `samples/` | 안전한 로컬 도구와 명시적으로 실행하는 Azure 예제 |
| `content/` | 모듈·기능·공식 출처의 구조화된 목록 |
| `scripts/` | 재생성·문서 검사·출처 링크 확인 |
| `tests/` | 로컬 계약·오류 경로·평가 게이트 회귀 테스트 |
| `validation/` | 이 배포본의 검증 범위와 결과 |

## 가이드를 수정할 때

`docs/`와 `content/`를 수정한 뒤 재생성합니다. 생성된 HTML/통합 Markdown을 직접 수정하지 마세요.

```bash
python -m pip install -r requirements-docs.txt
python scripts/build_guide.py
python scripts/check_guide.py
python -m unittest discover -s tests -v
# 공식 공개 URL만 접속하며 Azure 인증·리소스를 사용하지 않음
python scripts/check_links.py
```

`scripts/browser-check.js`와 `scripts/export-pdf.js`는 프로젝트 루트에서 구동한 Playwright MCP의 코드 실행 도구에 전달하는 함수 파일입니다. 이 재생성 경로에서는 `127.0.0.1:8765`에 가이드를 제공해야 합니다. 일반 사용자는 서버 없이 `index.html`의 인쇄 버튼을 사용하면 됩니다. PDF를 검사할 때만 `requirements-qa.txt`를 설치하고 `python scripts/check_pdf.py`를 실행합니다.

**검증의 경계:** 로컬 테스트와 SDK 계약 확인은 Azure 실행 성공을 의미하지 않습니다. 이 가이드를 제작하면서 Azure 리소스 생성·모델 추론·유료 평가·학습·조직 게시를 실행하지 않았습니다. 실습자는 자신의 테넌트에서 각 모듈의 성공 기준을 확인해야 합니다.

이 자료는 Microsoft 공식 교육과정이나 서비스 보증이 아닌 독립적으로 구성한 실습 자료입니다. 제품 설명의 근거는 Microsoft 공개 문서이며, 시나리오·데이터·그림은 본 가이드용으로 작성했습니다.
