# Microsoft Foundry, 직접 만들며 이해하기

**2026-09-30 Contoso 독립형 실행 가이드 · 한국어 · 25개 실습 모듈**

**[`index.html`](index.html)을 브라우저에서 여세요.** 설치 없이 목차·검색·학습 경로·진도 체크를 사용할 수 있습니다. 외부 CDN, 로그인, 분석 추적 없이 동작합니다. 인쇄 버튼으로 현재 모듈 또는 전체 가이드를 PDF로 저장할 수 있습니다.

GitHub 또는 텍스트로 읽을 때는 **[`GUIDE.ko.md`](GUIDE.ko.md)** 를 사용하세요. 처음이라면 웹 가이드의 **L00 시작하기**부터 진행합니다.

공유·인쇄본은 **[`Contoso-Foundry-Hands-on-2026-09-30.pdf`](Contoso-Foundry-Hands-on-2026-09-30.pdf)**,
전체 키트는 **[`Contoso-Foundry-Hands-on-2026-09-30.zip`](Contoso-Foundry-Hands-on-2026-09-30.zip)**입니다.
과거 2026-09-29 산출물/검증 원본은 과거 기록이며 Contoso 신규 결과가 아닙니다.

## 무엇을 완성하나요?

가상의 **Contoso 구매·정책·재고·구매 요청 초안 도우미**를 만듭니다.
규정을 인용하고 재고를 조회하며 **초안에서 멈춥니다**. 실제 주문·결제·업무 승인·메일 발송은 없습니다.
노트북 상한 150만원, 재고 단가 145만원, 총액 **200만원 초과** 시 두 승인 역할이라는 A의 업무 규칙을 유지합니다.

**이 저장소만 있으면 됩니다.** B는 제작 시 한 번 참고한 MIT 자료일 뿐이며,
설치·학습·실행·빌드·패키징·CI에서 clone/접근/다운로드하지 않습니다.
출처·라이선스는 [`THIRD_PARTY_NOTICES`](THIRD_PARTY_NOTICES)에 보존합니다.

**실제 검증 결과:** 새 Azure RG에서 Hosted·Search/IQ·도구·Memory·A2A·평가·Tracing과
[OIDC 배포·업무 검사](https://github.com/junwoojeong100/foundry-labs-v1.5/actions/runs/36649656044)를 수행했습니다.
최종 holdout은 **9/10이나 safety 사례의 필수 인용 누락으로 품질 게이트 미통과**입니다.
실행 성공과 릴리스 품질을 구분하며, Routine history 미확인·optimizer 신규 후보 0도 그대로 기록했습니다.

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

Azure 실습은 L01의 관리자 준비/학습자 경로를 구분합니다.
검증 조합은 **Python 3.13 / azure-ai-projects 2.7.0 / openai 3.18.0 / Azure CLI 2.86.0 / azd 1.34.0**입니다.
개별 실습 CLI는 `--live` 없이는 Azure를 호출하지 않습니다. `azd deploy`와 CI는 별도 명시적 배포 동작입니다.

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
| `Contoso-Foundry-Hands-on-2026-09-30.pdf` | 표지·목차·책갈피를 포함한 현재 인쇄본 |
| `docs/` | 모듈별 원문 |
| `assets/` | 로컬 스타일·스크립트·직접 제작한 다이어그램 |
| `data/` | 가상 정책·재고·평가·튜닝·문서 이해 데이터 |
| `samples/` | 안전한 로컬 도구와 명시적으로 실행하는 Azure 예제 |
| `hosted/`, `azure.yaml`, `infra/` | 동봉 Hosted runtime·code deployment·새 RG용 IaC |
| `content/` | 모듈·기능·공식 출처의 구조화된 목록 |
| `scripts/` | 재생성·문서 검사·출처 링크 확인 |
| `tests/` | 로컬 계약·오류 경로·평가 게이트 회귀 테스트 |
| `validation/current/` | 현재 구현/실행/품질/차단/미실행 구분 |
| `validation/`의 기존 파일 | 2026-09-29 과거 검증 원본, 수정하지 않음 |

심화 실행 순서는 **L13 Search/IQ → L14 Hosted → L07 Toolbox → L15 A2A → L16 Memory → L17 Routine → L08 평가 → L10 Trace → L22 CI**입니다.
`requirements-hosted.txt`/`requirements-tools.txt`는 기본 환경에 추가할 수 있고,
MAF의 `requirements-advanced.txt`는 충돌 방지를 위해 별도 환경에 설치합니다.

## 가이드를 수정할 때

`docs/`와 `content/`를 수정한 뒤 재생성합니다. 생성된 HTML/통합 Markdown을 직접 수정하지 마세요.

```bash
python -m pip install -r requirements-docs.txt
python scripts/build_guide.py
python scripts/check_guide.py
python -m unittest discover -s tests -v
# 공식 공개 URL만 접속하며 Azure 인증·리소스를 사용하지 않음
python scripts/check_links.py
npm ci
npx playwright install chromium
npm run guide:browser
npm run guide:pdf
python scripts/check_pdf.py
python scripts/package_guide.py
```

브라우저/PDF 명령은 **headless Chromium**과 loopback 서버를 사용하고 완료 시 종료합니다.
MCP나 B는 필요 없습니다. Playwright headless MCP에서도 동봉 함수 파일을 실행할 수 있습니다.
일반 독자는 서버 없이 `index.html`을 사용합니다. PDF 검사는 `requirements-qa.txt`가 필요합니다.

**검증의 경계:** [`validation/current/report.json`](validation/current/report.json)의 실제 상태가 기준입니다.
로컬/fixture 통과는 Azure 또는 모델 품질 성공이 아닙니다. 실패·빈 응답·부분 실행은 그대로 남기며,
원시 자료는 배포 패키지에서 제외합니다. Voice·CU·Fine-tuning·Foundry Local의 범위도 각 모듈에 명시합니다.
검증 자원은 삭제 승인 전까지 보존하되 예약과 Hosted compute는 종료합니다. Search 등의 상시 비용은 남을 수 있습니다.

이 자료는 Microsoft 공식 교육과정이나 서비스 보증이 아닌 독립적으로 구성한 실습 자료입니다. 제품 설명의 근거는 Microsoft 공개 문서이며, 시나리오·데이터·그림은 본 가이드용으로 작성했습니다.
