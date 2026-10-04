# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)

합성 Contoso 구매 도우미를 만들며 배우는 **20개 실습 모듈과 5개 참고 절(총 25개 문서)**입니다. 두 언어가 같은 구현과 각각의 합성 데이터·지침을 사용합니다.

## 처음 시작하는 분

**Azure는 클라우드 서비스, Foundry는 그 안에서 AI를 만들고 관리하는 작업 공간입니다.** 사전 사용 경험 없이 개념부터 읽을 수 있습니다. 실제 호출에는 강사가 준비한 프로젝트·권한과 비용 승인이 필요합니다.

1. [L00: 기초부터 읽기](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l00-first-steps)에서 무엇을 만들지 확인합니다.
2. [실습 ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip)을 풀고 [L01](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l01)의 PC·프로젝트 준비를 진행합니다. Git 명령은 필수가 아닙니다.
3. 각 장의 **진행 방식 → 먼저 할 일 → 확인할 결과**를 따라갑니다. 기본 11개는 순서대로, 심화 8개는 선택하며 마지막에 공통 마무리 L19를 진행합니다.

웹 가이드는 **기본 11개 + 공통 마무리 1개 경로**로 시작하며 진도도 선택한 경로만 집계합니다. 제목은 할 일에 Responses API·File search·Function Calling·Evaluation·Tracing 같은 기능명을 함께 표시합니다. **용어가 낯설어요 / 진행이 막혔어요**에서 도움말을 읽고 원래 실습으로 돌아갈 수 있습니다.

블록에는 **터미널 명령 / 포털 Chat / .env 설정 / 정상 출력 예**를 구분해 표시합니다. 좁은 화면에서는 명령 해설을 세로로 읽을 수 있습니다. L01에는 새 터미널·Windows Python 경로 확인이 있고, L06의 `read-result --input`은 저장된 답·함수 결과·인용을 **새 Azure 호출 없이** 보여 줍니다. 원본이나 평가 판정을 바꾸지 않습니다.

계정이 없어도 로컬 함수와 L08의 **지침·평가 질문 읽기**를 할 수 있습니다. 자신의 응답 수집과 유료 평가는 선택입니다. **기존 L11의 통합 점검은 L06 후반부에 합쳤고**, 게시·버전 관리는 L18 CI/CD에 통합했습니다. 기본 코스에 별도 Capstone·Teams 게시·Hosted·Optimizer는 필요하지 않습니다.

심화마다 **시작 경로·설정값 출처·결과 확인 위치**를 안내합니다. Agent Framework는 L13 순차·동시와 L14 그룹 채팅·핸드오프로 나눠 각 흐름을 충분히 비교합니다. L17 권한·L18 CI/CD는 로컬 결함 복사본을 고치는 과제이며 실제 Azure 검증과 구분합니다. L18은 배포·운영 담당자를 위한 선택 과정입니다.

<details>
<summary>학습 지침과 모델 조건</summary>

**학습 흐름은 교육용 초기 v1 → 평가 → 이유 분석·개선 → v2 재평가입니다.** 현재 개선은 `agent-v2.txt`에서 관리하며 지침 버전과 검증 이력을 계속 늘리지 않습니다.
v2는 공용·비공개 질문 분리, 모든 하위 질문의 답변, 주장별 근거, 미확인 사실 보류, 실제 도구 권한·결과 확인을 구체화했습니다.

L02에 **`gpt-6-sol` / `2026-09-22`**, 배포 이름 `contoso-gpt-6-sol`을 명시했습니다. L08에서는 같은 복합 질문 12개를 두 언어에서 지침별 한 번씩 호출한 뒤 그 원문을 Foundry로 평가합니다. Holdout·Hosted 재배포·Optimizer는 필수가 아니며 **실제 점수 상승을 미리 보장하거나 결과를 작성하지 않습니다.**

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

ZIP은 먼저 풀고 폴더 구조를 유지합니다. `index.ko.html` 또는 `index.html`을 열고, 코드는 편집기에서 확인합니다.
Markdown도 ZIP 안의 `downloads/`에서 열면 상대 경로의 그림·코드를 함께 볼 수 있습니다. PDF에는 접힌 참고·관리자 절까지 포함됩니다.
기본 코스는 **L00–L10, 약 4시간 45분**입니다. 심화는 **L11–L18**, 공통 마무리는 **L19(10분)**이며 실습 번호는 00–19로 이어집니다. 기본만 진행하면 L10에서 L19로, 심화를 선택하면 선택한 장을 마친 뒤 L19로 이동합니다. 읽기에는 로그인이 필요하지 않습니다.

각 실습은 **확인할 화면·파일 → 값에 근거한 판단 → 실패 시 다음 행동**으로 진행합니다. 후반부의 trace·오케스트레이션·권한·릴리스 과제에는 판독 예시를, 설계형 장에는 Contoso 작성 예를 제공합니다. 예시는 실제 Azure 결과가 아니며, 설계 완료와 실제 실행 완료를 따로 기록합니다. L18의 기본 CI/릴리스 설계에는 Hosted 배포가 필요하지 않습니다.

## 지침과 실행 경계

`agent-v1.txt`는 역할·목표 중심의 기준선이고 `agent-v2.txt`는 현재 절차형 지침입니다. Prompt/Hosted 기본값은 v2입니다. 향상을 연출하기 위해 기준선을 약화하거나 평가 게이트를 낮추지 않습니다.

L08의 선택 수집은 `samples/instruction_prompt_agent_lab.py`, 같은 원문의 평가는 `samples/instruction_evaluation.py`를 사용하며 둘 다 명시적 `--live`가 필요합니다. 응답·점수·실패·소유 기록·비용은 비공개 `results/`에 보관하고 가이드와 패키지에 넣지 않습니다. 가이드는 제작자의 완료 기록이나 보장된 점수가 아니라 절차와 판단 기준을 설명합니다.

## 내레이션 실습 요약영상

[장별 재생 페이지](downloads/replay/index.html) · [한국어 MP4](downloads/replay/Contoso-Foundry-Replay.ko.mp4) · [English MP4](downloads/replay/Contoso-Foundry-Replay.en.mp4). 두 영상 모두 음성·자막·20개 모듈 챕터를 포함합니다. 명령과 도식으로 재구성한 학습 영상이며 실시간 포털 녹화나 검증 보고서가 아닙니다.

FFmpeg·시스템 음성과 선언된 Playwright가 설치된 macOS에서 `python scripts/build_replay.py`로 다시 만듭니다. 내레이션과 장면 원본은 `content/replay.json`입니다.

## 안전한 실행

합성 Contoso 데이터만 사용합니다. 실제 주문·결제·업무 승인을 수행하지 않습니다.
개인 `.env`, `.azure/`, 자격 증명과 원시 실행 파일은 Git·패키지에 넣지 않습니다.
영어 환경은 별도로 `FOUNDRY_LAB_LANGUAGE=en`을 선택하며 한국어가 기본값입니다. 환경과 소유권 기록을 섞지 않습니다.
`microsoft-foundry` skill은 개발 지침이지 학습자·런타임 의존성이 아닙니다. 새 Azure 호출·권한 변경·리소스 삭제에는 범위와 승인이 필요합니다.

## 소스에서 다시 생성하기

`docs/`, `docs/en/`, `content/`와 공통 소스를 수정하며 생성물을 직접 편집하지 않습니다.
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

Pages는 `gh-pages` branch의 루트를 게시합니다. `.nojekyll`을 유지하고 승인된 생성물만 게시하며 강제 push나 branch 삭제를 하지 않습니다.
main 병합·Pages 게시·공개 범위 변경은 지침 수정과 별도로 승인받습니다.
승인된 게시 후 `python scripts/check_pages.py`로 공개 HTML·자산과 원본을 대조합니다.

Microsoft 공식 교육과정이 아닙니다. 출처와 사용 조건은 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)를 확인합니다.
