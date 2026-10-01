# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)

합성 Contoso 구매 도우미를 만들며 배우는 **25개 실습 모듈과 5개 참고 절**입니다. 두 언어가 같은 구현과 각각의 합성 데이터·지침을 사용합니다.

**학습 흐름은 교육용 초기 v1 → 평가 → 이유 분석·개선 → v2 재평가입니다.** 현재 개선은 `agent-v2.txt`에서 관리하며 지침 버전과 검증 이력을 계속 늘리지 않습니다.
v2는 공용·비공개 질문 분리, 모든 하위 질문의 답변, 주장별 근거, 미확인 사실 보류, 실제 도구 권한·결과 확인을 구체화했습니다.

L02에 **`gpt-6-sol` / `2026-09-22`**, 배포 이름 `contoso-gpt-6-sol`을 명시했습니다. L08에서는 같은 복합 질문 12개를 두 언어에서 지침별 한 번씩 호출한 뒤 그 원문을 Foundry로 평가합니다. Holdout·Hosted 재배포·Optimizer는 필수가 아니며 **실제 점수 상승을 미리 보장하거나 결과를 작성하지 않습니다.**

## 읽기와 다운로드

| 형식 | 경로 |
| --- | --- |
| 한국어 웹 | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| 영어 웹 | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Markdown | [한국어](GUIDE.ko.md) · [English](GUIDE.en.md) |
| PDF | [한국어](Contoso-Foundry-Hands-on-2026-09-30.pdf) · [English](Contoso-Foundry-Hands-on-2026-09-30.en.pdf) |
| 전체 실습 패키지 | [두 언어 ZIP](Contoso-Foundry-Hands-on-2026-09-30.zip) |
| 합성 영수증 | [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) |

ZIP은 먼저 풀고 폴더 구조를 유지합니다. `index.ko.html` 또는 `index.html`을 열고, 코드는 편집기에서 확인합니다.
기본 코스는 L00–L12, 약 5시간 20분입니다. 고급 모듈은 필요에 따라 선택합니다. 읽기에는 로그인이 필요하지 않습니다.

## 지침과 최신 검증

- 교육용 기준선: 각 폴더의 `agent-v1.txt`는 역할·목표 중심의 단순한 시작 지침이며, 점수를 낮추려고 일부러 약화하지 않았습니다.
- 현재 지침: 같은 폴더의 `agent-v2.txt`. Prompt/Hosted 기본값도 v2입니다.
- 한 번 비교: `samples/instruction_lab.py`; 원문 native 평가: `samples/instruction_evaluation.py`. 둘 다 명시적인 `--live` 전에는 계획만 표시합니다.
- [현재 상태](validation/current/instructions.json), [최신 실제 Azure 원본](validation/current/report.json), [최신 문서 검사](validation/docs/structure.json).

**국문·영문 모두 GPT-6 Sol Prompt Agent 버전으로 실측했습니다.** 한국어 Native 관련성은 v1 **4.9167/5**에서 v2 **5.0/5**로 한 문항만 상승했고, 완결성·근거성은 동점이었습니다. 영어는 세 지표 모두 v1/v2 **5.0/5** 동점입니다. 따라서 이번 소규모 dev 표본에서는 한국어 관련성의 제한적 향상만 관측했으며 일반화·통계적 유의성·운영 승인을 뜻하지 않습니다. 보조 기계식 체크리스트는 국문 **33/40→33/40**, 영문 **29/40→28/40(−1)**였습니다. 모든 변경 critical flag를 원문과 대조했고, 일부 표현 차이로 인한 정규식 누락을 확인했습니다. Judge는 별도로 고정한 GPT-4.1을 사용했습니다.

대상 응답은 총 **48개**를 한 번씩 수집했고 Native 평가는 **24행씩 두 번** 완료했습니다. 평가 전용 Prompt Agent 두 개에 언어별 v1/v2 버전을 고정했습니다. v2 토큰 증가는 국문 **+7,376**, 영문 **+5,157**이며 평균 지연은 각각 **+0.427초**, **+0.496초**였습니다. Optimizer·holdout은 실행하지 않았고, 앞선 실패 시도는 대상 응답 0건으로 보존했습니다. 이 노출된 dev 비교는 출시 품질 승인이 아닙니다.
이번 비교 전 공개된 지침과 측정 원본은 [보존된 기준선 커밋의 Git 이력](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/39b2bd1a1c85cb18d3d46d8bf876a6e274d32958/validation)에 남아 있습니다.
원본의 실행·배포 ID는 추적용이며 지침 버전이 아닙니다.

## 안전한 실행

합성 Contoso 데이터만 사용합니다. 실제 주문·결제·업무 승인을 수행하지 않습니다.
개인 `.env`, `.azure/`, 자격 증명과 원시 실행 파일은 Git·패키지에 넣지 않습니다.
영어 환경은 별도로 `FOUNDRY_LAB_LANGUAGE=en`을 선택하며 한국어가 기본값입니다. 환경과 소유권 기록을 섞지 않습니다.
`microsoft-foundry` skill은 개발 지침이지 학습자·런타임 의존성이 아닙니다. 새 Azure 호출·권한 변경·리소스 삭제에는 범위와 승인이 필요합니다.

## 소스에서 다시 생성하기

`docs/`, `docs/en/`, `content/`와 공통 소스를 수정하며 생성물을 직접 편집하지 않습니다.
선언된 Python/Node 의존성이 설치된 환경에서 실행합니다.

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
npm run guide:pdf
python scripts/check_guide.py
npm run guide:browser
python scripts/check_pdf.py
python scripts/package_guide.py
```

같은 체크인 소스로 두 언어의 HTML/Markdown/PDF와 ZIP을 만듭니다. 로컬 검사도 `validation/docs/`에 최신 한 묶음만 둡니다.
이를 Azure 실행이나 모델 점수 향상 증거로 기록하지 않습니다.

## GitHub Pages

Pages는 `gh-pages` branch의 루트를 게시합니다. `.nojekyll`을 유지하고 승인된 생성물만 게시하며 강제 push나 branch 삭제를 하지 않습니다.
main 병합·Pages 게시·공개 범위 변경은 지침 수정과 별도로 승인받습니다.
승인된 게시 후 `python scripts/check_pages.py`로 공개 HTML·자산과 원본을 대조합니다.

Microsoft 공식 교육과정이 아닙니다. 출처와 사용 조건은 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)를 확인합니다.
