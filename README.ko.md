# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)

합성 Contoso 구매 에이전트를 만들며 배우는 **20개 실습 모듈과 5개 참고 절(총 25개 문서)**입니다. 두 언어가 같은 구현과 각각의 합성 데이터·지침을 사용합니다.

## 처음 시작하는 분

**실습 참여자가 자신의 환경을 만들고 처음부터 끝까지 진행합니다.** L01에서 PC·구독·권한·예산을 확인하고 전용 Foundry 프로젝트·모델·로그를 만든 뒤 에이전트·검색·도구·평가·추적을 경험합니다. 실제 작업에는 해당 범위의 Azure 권한과 비용 승인이 필요합니다.

1. [L00: 기초부터 읽기](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l00-first-steps)에서 무엇을 만들지 확인합니다.
2. [실습 ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip)을 풀고 [L01](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l01)의 PC·프로젝트 준비를 진행합니다. Git 명령은 필수가 아닙니다.
3. 각 장의 **진행 방식 → 먼저 할 일 → 확인할 결과**를 따라갑니다. 기본 11개는 순서대로, 심화 8개는 선택하며 마지막에 공통 마무리 L19를 진행합니다.

웹 가이드는 **기본 11개 + 공통 마무리 1개 경로**로 시작하며 진도도 선택한 경로만 집계합니다. 제목은 할 일에 Responses API·File search·Function Calling·Evaluation·Tracing 같은 기능명을 함께 표시합니다. **용어가 낯설어요 / 진행이 막혔어요**에서 도움말을 읽고 원래 실습으로 돌아갈 수 있습니다.

블록에는 **터미널 명령 / 포털 Chat / .env 설정 / 정상 출력 예**를 구분해 표시합니다. 좁은 화면에서는 명령 해설을 세로로 읽을 수 있습니다. L01에는 새 터미널·Windows Python 경로 확인이 있고, L06의 `read-result --input`은 저장된 답·함수 결과·인용을 **새 Azure 호출 없이** 보여 줍니다. 원본이나 평가 판정을 바꾸지 않습니다.

계정이 없어도 로컬 함수와 L08의 지침·질문을 읽을 수 있지만 Azure 실습 완료와는 구분합니다. 기본 경로는 자신의 응답을 수집·평가하고 로그를 읽는 흐름입니다. 통합 점검은 L06 후반부, 게시·버전 관리는 선택 L18에서 진행합니다. 별도 Capstone·Teams 게시·Hosted·Optimizer는 기본 완주 조건이 아닙니다.

심화마다 시작 경로·설정값 출처·결과 확인 위치를 안내합니다. L11 Search와 L12 Hosted도 직접 자원을 준비·실행합니다. Agent Framework는 L13 순차·동시와 L14 그룹 채팅·핸드오프로 나눕니다. L17 권한·L18 CI/CD는 로컬 결함 수정과 설계이며 실제 Azure 검증·게시와 구분합니다.

<details>
<summary>학습 지침과 모델 조건</summary>

**학습 흐름은 초기 v1 → 평가 → 이유 분석·개선 → v2 재평가입니다.** `agent-v1.txt`와 `agent-v2.txt`를 같은 조건에서 비교합니다.
v2는 공용·비공개 질문 분리, 모든 하위 질문의 답변, 주장별 근거, 미확인 사실 보류, 실제 도구 권한·결과 확인을 구체화했습니다.

키트는 **`gpt-6-sol` / `2026-09-22`**를 고정하고 L01이 만드는 호출 이름은 `contoso-chat`입니다. 실제 모델·지역 가용성은 자신의 구독에서 확인합니다. L08은 같은 질문 12개의 v1/v2 원문을 한 번 수집해 Foundry로 평가합니다. Holdout·Hosted 재배포·Optimizer는 필수가 아니며 점수 향상을 미리 보장하지 않습니다.

</details>

## 읽기와 다운로드

| 형식 | 경로 |
| --- | --- |
| 한국어 웹 | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| 영어 웹 | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Markdown | [한국어](downloads/GUIDE.ko.md) · [English](downloads/GUIDE.en.md) |
| PDF | [한국어](downloads/Contoso-Foundry-Hands-on-2026-09-30.pdf) · [English](downloads/Contoso-Foundry-Hands-on-2026-09-30.en.pdf) |
| 전체 실습 패키지 | [두 언어 ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip) |
| 합성 영수증 | [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) |

실습 코드 파일별 역할은 [한국어 안내](samples/README.ko.md) · [English](samples/README.md)에서 확인할 수 있습니다.

ZIP은 먼저 풀고 폴더 구조를 유지합니다. `index.ko.html` 또는 `index.html`을 열고, 코드는 편집기에서 확인합니다.
Markdown도 ZIP 안의 `downloads/`에서 열면 상대 경로의 그림·코드를 함께 볼 수 있습니다. PDF에는 접힌 선택·참고 절까지 포함됩니다.
기본 코스는 **L00–L10, 약 4시간 45분**입니다. 심화는 **L11–L18**, 공통 마무리는 **L19(10분)**이며 실습 번호는 00–19로 이어집니다. 기본만 진행하면 L10에서 L19로, 심화를 선택하면 선택한 장을 마친 뒤 L19로 이동합니다. 읽기에는 로그인이 필요하지 않습니다.

각 실습은 **확인할 화면·파일 → 값에 근거한 판단 → 실패 시 다음 행동**으로 진행합니다. 후반부의 trace·오케스트레이션·권한·릴리스 과제에는 판독 예시를, 설계형 장에는 Contoso 작성 예를 제공합니다. 예시는 실제 Azure 결과가 아니며, 설계 완료와 실제 실행 완료를 따로 기록합니다. L18의 기본 CI/릴리스 설계에는 Hosted 배포가 필요하지 않습니다.

## 지침 비교 실습

`agent-v1.txt`는 역할·목표 중심의 기준선이고 `agent-v2.txt`는 절차형 지침입니다. Prompt/Hosted 기본값은 v2입니다.

L08의 수집은 `samples/instruction_prompt_agent_lab.py`, 원문 평가는 `samples/instruction_evaluation.py`를 사용하며 둘 다 명시적 `--live`가 필요합니다. 비용 범위를 확인해 실행하고 응답·평가 파일을 자신의 `results/`에 함께 보관합니다. 읽기만 했다면 평가 미실행으로 기록합니다.

## 내레이션 실습 요약영상

[장별 재생 페이지](downloads/replay/index.html) · [한국어 MP4](downloads/replay/Contoso-Foundry-Replay.ko.mp4) · [English MP4](downloads/replay/Contoso-Foundry-Replay.en.mp4). 두 영상 모두 음성·자막·20개 모듈 챕터를 포함합니다. 실시간 포털 녹화가 아니라 명령과 도식으로 재구성한 학습 영상입니다.

FFmpeg·시스템 음성과 선언된 Playwright가 설치된 macOS에서 `python scripts/build_replay.py`로 다시 만듭니다. 내레이션과 장면 원본은 `content/replay.json`입니다.

## 안전한 실행

합성 Contoso 데이터만 사용합니다. 실제 주문·결제·업무 승인을 수행하지 않습니다.
개인 `.env`, `.azure/`, 자격 증명과 원시 실행 파일은 Git·패키지에 넣지 않습니다.
영어 환경은 별도로 `FOUNDRY_LAB_LANGUAGE=en`을 선택하며 한국어가 기본값입니다. 환경과 소유권 기록을 섞지 않습니다.
새 Azure 호출·권한 변경·리소스 삭제에는 범위와 승인이 필요합니다.

## 소스에서 다시 생성하기

`docs/`, `docs/en/`, `content/`와 공통 소스를 수정하며 생성물을 직접 편집하지 않습니다.
학습자 본문·캡션에는 행동, 확인할 결과, 필요한 사용 조건을 적습니다. 촬영 내역은 `content/portal-screenshots*.json`, 공식 출처의 확인일·검토 메모는 `content/sources*.json`에 보존하며 본문에 반복하지 않습니다. 스크린샷 원본·해시·과거 검증 기록은 변경하지 않습니다.
`microsoft-foundry` skill은 개발 지침이지 학습자·런타임·문서 빌드 의존성이 아닙니다.
학습자 표시 번호는 `content/chapters.json`의 `number`입니다. 기존 `id`·원문 파일명은 링크·진도·과거 기록의 식별자로 유지하므로 표시 번호와 다를 수 있습니다. 통합된 옛 `#l11` 링크는 L06의 통합 점검으로 이동하며 과거 검증 번호·원본은 바꾸지 않습니다.
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

같은 체크인 소스로 두 언어의 HTML/Markdown/PDF와 ZIP을 만듭니다. 로컬 검사 기록은 비공개 `results/documentation/`에 두고 패키지에 넣지 않습니다.
이를 Azure 실행이나 모델 점수 향상 증거로 기록하지 않습니다.

## GitHub Pages

Pages는 **`main` 브랜치의 루트(`/`)**를 게시합니다. `main`에 push하면 체크인된 HTML과 다운로드 파일이 자동 게시되며 별도의 `gh-pages` 갱신은 필요하지 않습니다.
main 병합은 여전히 승인이 필요하며 이제 사이트 게시도 함께 발생합니다. 병합 전에 HTML/Markdown/PDF/ZIP을 다시 생성하고 확인합니다. Pages가 가이드 생성 스크립트를 대신 실행하지는 않습니다.
기존 자동 검사와 Pages 배포는 독립적으로 실행됩니다. **Pages는 자동 검사가 끝나기를 기다리지 않습니다.**
`.nojekyll`을 유지하고 기존 `gh-pages` 브랜치는 이력으로 보존합니다. 강제 push나 브랜치 삭제는 하지 않으며, 공개 범위 변경과 Azure 작업은 별도 승인이 필요합니다.
배포 후 `python scripts/check_pages.py`로 공개 HTML·자산과 병합된 원본을 대조합니다.

Microsoft 공식 교육과정이 아닙니다. 출처와 사용 조건은 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)를 확인합니다.
