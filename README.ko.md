# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)

합성 Contoso 구매 에이전트를 만들며 배우는 **20개 실습 모듈과 5개 참고 절(총 25개 문서)**입니다. 두 언어가 같은 구현과 각각의 합성 데이터·지침을 사용합니다.

## 처음 시작하는 분

**처음이라면 기본 L00–L10 → 공통 마무리 L19 순서로 진행합니다.** L01에서 자신의 환경을 만들며, 실제 Microsoft Azure 작업 전에는 해당 범위의 권한·비용 승인을 확인합니다. 심화 L11–L18은 기본 완주의 필수 조건이 아닙니다.

1. [L00: 기초부터 읽기](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l00-first-steps)에서 무엇을 만들지 확인합니다.
2. **설치를 줄이려면 [GitHub Codespaces 경로](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l01-codespaces)**를 선택합니다. 내 PC에서 진행하려면 [실습 ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip)을 풀고 [L01](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l01)을 따릅니다. 둘 중 한 환경만 사용하며 Git 명령은 필수가 아닙니다.
3. 각 장의 시작 카드에서 할 일과 결과를 확인하고 **준비 → 실행 → 성공 기준 → 정리**를 따라갑니다. 마지막 **이 장에서 남길 것 / 다음**을 확인한 뒤 페이지 맨 아래 **다음**으로 이동합니다.

| 진행 중 필요한 안내 | 읽는 방법 |
| --- | --- |
| 설치·재개 | L01에서 버전을 확인하고 없는 도구의 설치 설명만 펼칩니다. 다음 날에는 **새 터미널에서 재개**를 사용합니다. |
| 명령·질문·설정 | **터미널 / 포털 Chat / .env / 정상 출력 예** 표시를 먼저 봅니다. 계획을 읽고 멈춘 뒤 실제 실행 명령을 따로 복사합니다. |
| 용어·오류 | **용어가 낯설어요 / 진행이 막혔어요**를 열고 **읽던 실습으로 돌아가기**로 같은 위치에 복귀합니다. |
| 완료·기록 | 실제 결과로 성공 기준을 확인합니다. 브라우저 진도는 학습 표시일 뿐 Microsoft Azure 실행 증거가 아닙니다. |

접힌 **구현 참고·선택 확장**은 모두 수행할 목록이 아닙니다. 기본 경로는 자신의 응답·근거·함수 결과·평가·로그를 확인하며, 별도 Capstone·Teams 게시·Hosted·Optimizer는 요구하지 않습니다.

**Microsoft Azure 준비가 안 됐다면** 웹 목차의 **Microsoft Azure 없이**를 고릅니다. 각 장에서 지정한 로컬·읽기·설계 단계만 진행하며 실제 Microsoft Azure 실습 완료와 구분합니다. 심화를 선택할 때도 장 앞의 선행 조건부터 확인합니다.

### GitHub Codespaces로 설치 최소화

브라우저와 GitHub 계정으로 **저장소 → Code → Codespaces → New with options**를 엽니다. `.devcontainer/devcontainer.json`이 있는 실습 브랜치, 비용 부담 주체·허용량·머신을 확인한 뒤 생성합니다. 설정이 Python 3.13·Microsoft Azure CLI·Bicep·Python 확장과 기본/MCP 의존성을 준비합니다. **내 PC에 Python·CLI·VS Code·Docker를 설치할 필요는 없습니다.**

생성 후 설치가 끝날 때까지 기다리고 L01의 준비 검사를 수행합니다. Microsoft Azure 로그인·권한·비용 승인은 별도이며 자원을 자동 생성하지 않습니다. Codespaces에서는 Windows PC를 쓰더라도 **Linux/Bash 명령**을 사용합니다. 종료할 때는 [L19](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html#l12)에서 Microsoft Azure 자원과 Codespace를 **각각** 확인합니다. Codespace를 중지해도 저장 비용과 Microsoft Azure 자원 비용은 남을 수 있습니다.

<details>
<summary>학습 지침과 모델 조건</summary>

**학습 흐름은 초기 v1 → 평가 → 이유 분석·개선 → v2 재평가입니다.** `agent-v1.txt`와 `agent-v2.txt`를 같은 조건에서 비교합니다.
v2는 공용·비공개 질문 분리, 모든 하위 질문의 답변, 주장별 근거, 미확인 사실 보류, 실제 도구 권한·결과 확인을 구체화했습니다.

키트는 **`gpt-6-sol` / `2026-09-22`**를 고정하고 L01이 만드는 호출 이름은 `contoso-chat`입니다. 실제 모델·지역 가용성은 자신의 구독에서 확인합니다. L08은 같은 질문 12개의 v1/v2 원문을 한 번 수집해 Microsoft Foundry로 평가합니다. Holdout·Hosted 재배포·Optimizer는 필수가 아니며 점수 향상을 미리 보장하지 않습니다.

</details>

## 읽기와 다운로드

| 형식 | 경로 |
| --- | --- |
| 한국어 웹 | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) |
| 영어 웹 | [GitHub Pages](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Markdown | [한국어](downloads/GUIDE.ko.md) · [English](downloads/GUIDE.en.md) |
| 전체 실습 패키지 | [두 언어 ZIP](downloads/Contoso-Foundry-Hands-on-2026-09-30.zip) |
| 합성 영수증 | [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html) |

실습 코드 파일별 역할은 [한국어 안내](samples/README.ko.md) · [English](samples/README.md)에서 확인할 수 있습니다.

ZIP은 먼저 풀고 폴더 구조를 유지합니다. `index.ko.html` 또는 `index.html`을 열고, 코드는 편집기에서 확인합니다.
Markdown도 ZIP 안의 `downloads/`에서 열면 상대 경로의 그림·코드를 함께 볼 수 있습니다.
기본 코스는 **L00–L10, 약 4시간 45분**입니다. 심화는 **L11–L18**, 공통 마무리는 **L19(10분)**이며 실습 번호는 00–19로 이어집니다. 기본만 진행하면 L10에서 L19로, 심화를 선택하면 선택한 장을 마친 뒤 L19로 이동합니다. 읽기에는 로그인이 필요하지 않습니다.

각 실습은 **확인할 화면·파일 → 값에 근거한 판단 → 실패 시 다음 행동**으로 진행합니다. 후반부의 trace·오케스트레이션·권한·릴리스 과제에는 판독 예시를, 설계형 장에는 Contoso 작성 예를 제공합니다. 예시는 실제 Microsoft Azure 결과가 아니며, 설계 완료와 실제 실행 완료를 따로 기록합니다. L18의 기본 CI/릴리스 설계에는 Hosted 배포가 필요하지 않습니다.

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
새 Microsoft Azure 호출·권한 변경·리소스 삭제에는 범위와 승인이 필요합니다.

## 소스에서 다시 생성하기

`docs/`, `docs/en/`, `content/`와 공통 소스를 수정하며 생성물을 직접 편집하지 않습니다.
학습자 본문·캡션에는 행동, 확인할 결과, 필요한 사용 조건을 적습니다. 촬영 내역은 `content/portal-screenshots*.json`, 공식 출처의 확인일·검토 메모는 `content/sources*.json`에 보존하며 본문에 반복하지 않습니다. 스크린샷 원본·해시·과거 검증 기록은 변경하지 않습니다.
`microsoft-foundry` skill은 개발 지침이지 학습자·런타임·문서 빌드 의존성이 아닙니다.
학습자 표시 번호는 `content/chapters.json`의 `number`입니다. 기존 `id`·원문 파일명은 링크·진도·과거 기록의 식별자로 유지하므로 표시 번호와 다를 수 있습니다. 통합된 옛 `#l11` 링크는 L06의 통합 점검으로 이동하며 과거 검증 번호·원본은 바꾸지 않습니다.
선언된 Python/Node 의존성이 설치된 환경에서 실행합니다.

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
npm run guide:browser
python scripts/package_guide.py
```

같은 체크인 소스로 두 언어의 HTML/Markdown과 ZIP을 만듭니다. 로컬 검사 기록은 비공개 `results/documentation/`에 두고 패키지에 넣지 않습니다.
이를 Microsoft Azure 실행이나 모델 점수 향상 증거로 기록하지 않습니다.

## GitHub Pages

Pages는 **`main` 브랜치의 루트(`/`)**를 게시합니다. `main`에 push하면 체크인된 HTML과 다운로드 파일이 자동 게시되며 별도의 게시 브랜치는 필요하지 않습니다.
main 병합은 여전히 승인이 필요하며 이제 사이트 게시도 함께 발생합니다. 병합 전에 HTML/Markdown/ZIP을 다시 생성하고 확인합니다. Pages가 가이드 생성 스크립트를 대신 실행하지는 않습니다.
기존 자동 검사와 Pages 배포는 독립적으로 실행됩니다. **Pages는 자동 검사가 끝나기를 기다리지 않습니다.**
`.nojekyll`을 유지하고 강제 push는 하지 않습니다. 브랜치 삭제·공개 범위 변경·Microsoft Azure 작업은 명시적 승인이 필요합니다.
배포 후 `python scripts/check_pages.py`로 공개 HTML·자산과 병합된 원본을 대조합니다.

Microsoft 공식 교육과정이 아닙니다. 출처와 사용 조건은 [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)를 확인합니다.
