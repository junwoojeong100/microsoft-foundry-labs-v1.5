# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)

합성 Contoso 구매 도우미를 만들며 배우는 **25개 실습 모듈과 5개 참고 절**입니다. 두 언어가 같은 구현과 각각의 합성 데이터·지침을 사용합니다.

**학습 흐름은 변경하지 않은 v1 → 개선 v2 → 한 번 비교입니다.** 현재 개선은 `agent-v2.txt`에서 관리하며 지침 버전과 검증 이력을 계속 늘리지 않습니다.
v2는 공용·비공개 질문 분리, 모든 하위 질문의 답변, 주장별 근거, 미확인 사실 보류, 실제 도구 권한·결과 확인을 구체화했습니다.

L08에서는 같은 질문 3개를 같은 모델·문맥·출력 형식·체크리스트로 지침별 한 번씩 비교합니다.
반복 검증·holdout·Hosted 재배포·Optimizer는 필수가 아닙니다. **실제 점수 상승을 미리 보장하거나 결과를 작성하지 않습니다.**
동점·하락·오류·미완료도 원문 그대로 남깁니다.

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

- 기준선: `data/prompts/agent-v1.txt`와 `data/en/prompts/agent-v1.txt`. 비교를 위해 약화하지 않았습니다.
- 현재 지침: 같은 폴더의 `agent-v2.txt`. Prompt/Hosted 기본값도 v2입니다.
- 한 번 비교: `samples/instruction_lab.py`. 별도 승인 후 `--live`를 주기 전에는 계획만 표시합니다.
- [현재 상태](validation/current/instructions.json), [최신 실제 Azure 원본](validation/current/report.json), [최신 문서 검사](validation/docs/structure.json).

수정한 v2는 **새 Azure 비교를 실행하지 않았습니다.** 가장 최근 실제 원본은 수정 전 지침의 dev 39/40·critical access 근거 실패와 Optimizer 오류를 그대로 유지하며, holdout은 실행하지 않았습니다. 이 기록을 현재 v2의 통과 결과로 바꾸지 않습니다.
이전 검증 파일은 현재 목록에서 정리하고 [고정된 Git 이력](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/tree/6fddd4642be0d0ac9dfee9b9b51e7b00b5cf1cde/validation)에 원본을 보존했습니다.
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
