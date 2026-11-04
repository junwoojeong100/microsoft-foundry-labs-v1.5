# Microsoft Foundry 실습 가이드

[English](README.md) | **한국어**

**[한국어 온라인 가이드](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html)** · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/)

**Azure portal·Foundry portal에서 한 단계씩 진행하는 20개 모듈과 5개 참고 절**입니다. 학습자에게 CLI·Python·SDK·Codespaces·개발 skill 설치를 요구하지 않습니다. 합성 Contoso 정책과 구매 사례만 사용합니다.

## 처음 시작하기

1. [L00](docs/00-start.md)에서 자원·요청·비용 범위를 정합니다. 기본 경로는 **L00–L10 → L19**, 기본 실습 약 **4시간 45분**과 마무리 10분이며 승인·생성 대기는 별도입니다.
2. [L01](docs/01-setup.md)을 따라 새 창에서 로그인하고 전용 그룹·account·project·로그를 만듭니다. 모델은 L02에서 정확한 버전·SKU·TPM·처리 위치를 읽고 배포합니다.
3. 매 장의 **준비 → 실행 표의 한 행 → 화면·값 확인 → 실패 시 행동**을 따릅니다. 다음 행으로 넘어가기 전에 성공 여부를 확인합니다.

| 필요한 것 | 사용 방법 |
| --- | --- |
| 정책·지침·평가 입력 | [포털 업로드 전용 ZIP](downloads/Contoso-Portal-Inputs.zip)을 풀어 `ko/`를 사용합니다. 정책 3파일, v1/v2 Instructions, 고정 12행 JSONL·열람용 CSV, 수동 checklist입니다. |
| 화면 실습 | Azure portal에서 자원·비용, Foundry portal에서 모델·agent·파일·평가·trace를 다룹니다. 입력 위치는 버튼·필드 이름으로 안내합니다. |
| 실제 영상 | [실제 포털 녹화·수행 범위](downloads/portal/index.html). 영상에 없는 단계는 실행 성공으로 간주하지 않습니다. |
| 설치·로그인 없이 읽기 | 웹 목차의 **실행 없이 읽기** 또는 전체 ZIP의 HTML/Markdown을 사용합니다. 읽기는 Microsoft Azure 실행 증거가 아닙니다. |

기본 대상은 포털 정책 agent와 **도구 없는 평가용 v1/v2 Prompt Agent**입니다. L06은 함수 backend가 없는 포털에서 재고 조회·초안 저장·승인을 실행했다고 가장하지 않습니다. L07의 읽기 전용 MCP는 포털·권한 지원 시에만 시험합니다.

L08의 새 포털 평가는 기존 SDK 실험과 별개입니다. 동일한 합성 문맥·모델, 고정 12문항, v1/v2 지침만 다른 조건을 유지합니다. 실제 생성 응답을 평가하며 예상 답을 만들어 넣지 않습니다. **품질 ≥90%, 안전/access 실패 0** 기준과 오류·누락은 그대로 보존합니다. Holdout이 없어 운영 release의 일반화 증거는 아닙니다.

심화 L11–L18은 조건을 먼저 읽습니다. 추가 Search는 별도 자원·비용 승인, Hosted는 관찰, L13–L14는 **사람의 수동 역할 전달 비교**입니다. Memory는 생성 폼·runtime 권한 경고를 관찰하고 취소합니다. 기존 승인 store의 조건부 회상도 CRUD/격리 검증은 아닙니다. Routines는 제출 전 취소, 거버넌스·배포 판단은 읽기 전용입니다. 실제 SDK 병렬·자동 handoff·게시·rollback으로 표시하지 않습니다.

**이번 실제 실행:** 전용 RG·Microsoft Foundry account/project·로그 자원, 수동 모델 2개와 관찰된 자동 embedding, 정책 파일 3개를 만들었습니다. 직접 Chat 11회와 한국어 12행 평가 2회를 녹화했습니다. 두 평가 모두 응답 12개를 생성했지만 **v2 Relevance 1행은 APIConnectionError**이므로 native 비교 미완료·출시 보류입니다. [식별자를 제거한 실제 응답·오류](downloads/portal/evaluation-summary.json)와 영상의 20모듈 수행 범위를 함께 읽습니다. 기본 화면 예시나 로컬 검사를 새 Microsoft Azure 성공으로 세지 않습니다.

## 자료

| 형식 | 경로 |
| --- | --- |
| 한국어·영어 웹 | [한국어](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/index.ko.html) · [English](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/) |
| Markdown | [한국어](downloads/GUIDE.ko.md) · [English](downloads/GUIDE.en.md) |
| 브라우저 업로드 자료 | [가벼운 입력 ZIP](downloads/Contoso-Portal-Inputs.zip) |
| 전체 오프라인 패키지 | [한·영 HTML·Markdown·그림·자료 ZIP](downloads/Contoso-Foundry-Hands-on-2026-10-15.zip) |
| 실제 화면 녹화 | [영상·자막·실행/차단 범위](downloads/portal/index.html) |
| 선택 문서 분석 예시 | [한국어 영수증](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/receipt.html) · [English receipt](https://junwoojeong100.github.io/microsoft-foundry-labs-v1.5/data/en/receipt.html); 필수 업로드 아님 |
| 과거 재구성 영상 | [기존 요약영상](downloads/replay/index.html): 명령·도식·내레이션 재구성이며 **실제 포털 녹화가 아닙니다**. 현재 실습 절차로 사용하지 않습니다. |

전체 ZIP은 폴더 구조를 유지하고 `index.ko.html`을 엽니다. 업로드에는 전체 ZIP 대신 `ko/policies/`의 Markdown 3파일 또는 L08의 `evaluation-12.jsonl`만 선택합니다. CSV는 사람이 읽는 보조 자료입니다. 로그인 화면·키·메일·사람 목록·원시 로그를 공개하지 않습니다.

온라인 사이트는 `main` 게시본입니다. 작업 브랜치의 변경은 승인된 main 반영 전까지 로컬 HTML/Markdown/ZIP에서 확인합니다.

## 비용과 안전

모델은 원본 기준 **`gpt-6-sol / 2026-09-22`**, 배포 `contoso-chat`, judge는 `gpt-4.1 / 2025-04-14`, `contoso-judge`입니다. 실제 구독에서 해당 버전·지역을 확인합니다. 없으면 차단으로 기록하며 다른 모델로 몰래 대체하지 않습니다.

전용 scope와 비공개 소유 기록, 자원·요청 상한을 먼저 정합니다. 요청 수는 금액 상한이 아니며 Budget 알림도 지출 차단이 아닙니다. 실제 주문·결제·업무 승인은 없습니다. 권한 확대·정기 실행·게시·삭제에는 별도 승인이 필요합니다.

**브라우저 종료는 자원·일정 종료가 아닙니다.** 삭제 승인 전에는 자원을 보존하므로 로그·파일·Search·compute 등의 비용이 남을 수 있습니다. [L19](docs/12-cleanup.md)에서 실제 자원·보존·다음 비용 확인을 인계합니다.

## 저장소를 수정하는 분

학습자에게 아래 개발 명령은 필요 없습니다.

<details>
<summary>소스·생성·검증·GitHub Pages</summary>

`docs/`, `docs/en/`, `content/`가 원문입니다. 생성 HTML/Markdown을 직접 수정하지 않습니다. 표시 번호는 `number`이고 기존 `id`·파일명·옛 `#l11` 연결은 유지합니다. 포털 개정에서도 한국어 20모듈과 두 언어 구조를 보존합니다.

`microsoft-foundry` skill은 **개발 지침**이지 학습자·런타임·빌드 의존성이 아닙니다. 개발자가 Microsoft Foundry 관련 코드를 바꿀 때 읽으며 문서 빌드가 이를 다운로드·실행하지 않습니다.

기존 Python/Node 의존성이 준비된 환경에서:

```bash
python scripts/build_guide.py
FOUNDRY_LAB_LANGUAGE=ko python -m unittest discover -s tests -q
python scripts/check_guide.py
npm run guide:browser
python scripts/package_guide.py
python scripts/package_guide.py --check
```

`build_guide.py`는 고정 합성 원본에서 포털 입력과 두 언어 HTML/Markdown, 검토된 실제 영상의 해시·20모듈 수행 범위를 검사한 영상 색인을 만듭니다. 영상 재촬영·Microsoft Azure 호출은 하지 않습니다. ZIP은 고정 시각·정렬로 생성하며 링크·무결성·비공개/유지보수 자료 제외 검사를 통과해야 교체합니다. 로컬 검사 결과는 비공개 `results/documentation/`에 두며 Microsoft Azure 실행 증거로 부르지 않습니다.

기존 screenshot 원본·해시·촬영 이력과 `validation/`의 과거 증거는 변경하지 않습니다. 새 실제 영상은 별도 provenance와 수행/미실행 범위를 갖습니다. 로그인·계정·키·구독·사람 목록이 있는 raw 영상은 패키지에 넣지 않습니다.

유지보수 전용 평가 v2–v5, 저작/라이브 CI 스크립트와 관련 테스트는 `content/maintainer-only.json`에 따라 ZIP에서 제외합니다. 동결 데이터·기준·과거 결과를 고쳐 통과시키지 않습니다. 학습용 포털 입력은 `instruction-comparison.json`의 12문항을 사용합니다. 기존 SDK/Hosted 샘플과 [코드 참고](samples/README.ko.md)는 개발자용이며 새 학습 경로의 실행 요구가 아닙니다.

기존 재구성 영상은 macOS의 FFmpeg·음성·선언된 Playwright로 `python scripts/build_replay.py`에서 생성합니다. `content/replay.json`의 과거 장면을 실제 포털 footage로 재분류하지 않습니다.

Pages는 **`main` 브랜치의 루트(`/`)**를 게시합니다. main에 push하면 체크인 HTML·다운로드가 자동 게시됩니다. main 병합에는 명시적 승인이 필요하며 Pages는 자동 검사가 끝나기를 기다리지 않습니다. 생성 스크립트를 대신 실행하지도 않습니다. `.nojekyll` 유지, 강제 push·무승인 병합/공개 범위 변경 금지입니다.

승인된 게시 후 `python scripts/check_pages.py`로 공개 자산·ZIP과 원본을 비교합니다. `python scripts/check_links.py`는 기록된 검토일 이후 공식 문서 변경을 알려 줍니다. 이 포털 개정은 과거 검토일·라이브 검증 결과를 갱신하지 않습니다.

</details>

Microsoft 공식 교육과정이 아닙니다. [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES)와 [MIT 라이선스](LICENSE)를 확인합니다. Microsoft 제품 이름·아이콘·포털 화면은 해당 권리에 따릅니다. [가이드 이슈](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5/issues/new/choose)에 자격 증명·개인정보를 붙이지 않습니다.
