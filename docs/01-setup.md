> **완성할 결과:** 내가 만든 실습 전용 리소스 그룹·Microsoft Foundry 프로젝트·모델 배포·로그 연결과, 실행할 Python 환경.

<div class="lab-brief" markdown="1">

**진행 방식:** 실행 환경 준비 → 로그인·권한 확인 → 전용 환경 생성 → 설정·로그 연결.

**먼저 할 일:** 내 PC 또는 [GitHub Codespaces](#l01-codespaces) 중 실행할 환경 하나를 고르고, 사용할 Microsoft Azure 구독·지역·예산을 확인합니다.

**확인할 결과:** `results/azure-environment.json`의 내 프로젝트와 포털의 자원이 일치합니다. 첫 모델 요청은 L03에서 보냅니다.

</div>

## 목표

**실습 참여자가 필요한 환경을 직접 만듭니다.** 이후 장은 이 프로젝트와 소유 기록을 이어 사용합니다. 생성·조회·역할 부여 각각에 필요한 권한을 확인하고, 없는 권한은 확보하기 전까지 해당 작업을 보류합니다.

## 개념과 실습 지도

**경험할 기능:** Microsoft Foundry 프로젝트·모델·권한·로그와 로컬 Python 환경을 준비합니다.

**무엇이며 왜 중요한가요?** 구독은 비용 범위, 리소스 그룹은 자원 묶음, 프로젝트는 에이전트 작업 공간입니다. 로그인은 신원, RBAC는 허용 작업, quota는 사용 가능한 용량입니다.

**어떻게 사용하나요?** 전용 환경을 만들고 포털의 실제 이름·주소를 `.env`와 소유 기록에 대조합니다. 주소를 안다고 권한이 생기지는 않습니다.

**어디서 실행하나요?** 선택한 환경(PC 또는 Codespaces)의 VS Code 터미널에서 명령을 실행하고 Microsoft Azure·Microsoft Foundry 포털에서 결과를 확인합니다. [환경 생성 코드](../scripts/azure_environment.py)와 [Bicep](../infra/main.bicep)이 실제 생성 범위를 정의합니다.

## 준비

| 준비할 것 | 확인할 내용 |
| --- | --- |
| Microsoft Azure 계정·사용 가능한 구독 | 자신의 계정으로 로그인할 수 있고 구독이 Enabled인지 |
| 생성 권한 | 리소스 그룹 생성과 그 안의 Microsoft Foundry·로그 자원 배포 권한 |
| 역할 부여 권한 | 대상 범위의 `Microsoft.Authorization/roleAssignments/write`. `Contributor`만으로는 역할을 부여할 수 없음 |
| quota 조회 권한 | 구독의 `Cognitive Services Usages Reader` 등 모델 사용량 조회 권한 |
| 지역·예산 | 모델 지원 지역, 허용된 처리 범위, 지출 한도·중단 기준·보존 기한 |
| 실행 환경 | 내 PC의 Python 3.13·Microsoft Azure CLI 2.86.0 기준·VS Code, 또는 아래 GitHub Codespaces 구성. 인터넷·허용된 패키지 저장소 필요 |

자신의 구독이라도 실제 권한을 먼저 확인합니다. 조직 구독에서는 필요한 범위의 권한·비용 승인을 확보한 뒤 진행합니다. 권한이 없으면 해당 작업을 보류하며, 오류를 우회하려고 보안을 끄거나 구독 전체 권한을 확대하지 않습니다. 계정·권한 없이도 로컬 연습은 가능하지만 **Microsoft Foundry 실행 완료와는 별도**입니다.

<a id="l01-pc"></a>

## 실행

### 1. PC와 실습 파일 준비하기

**두 경로 중 하나만 선택합니다.** 이미 PC 도구가 있다면 아래 버전 확인을, 설치를 줄이고 싶다면 **GitHub Codespaces**를 사용합니다. Codespaces는 GitHub가 제공하는 원격 Linux 개발 환경이며 Microsoft Foundry 프로젝트 자체는 아닙니다.

<details class="optional-path codespaces-path" markdown="1">
<summary>설치 최소화: 브라우저에서 GitHub Codespaces로 시작하기</summary>

<a id="l01-codespaces"></a>

#### Codespaces 생성 → 준비 확인 → 같은 실습 계속하기

**필요한 것:** GitHub 계정·이 저장소의 읽기 권한·조직의 Codespaces 사용 허용과 비용 범위입니다. Microsoft Azure 구독·권한은 실제 클라우드 실습을 할 때 별도로 필요합니다. 회사의 private endpoint/VNet에 Codespaces가 자동 연결되는 것은 아닙니다. 허용된 네트워크 경로가 없다면 로컬 연습까지만 진행하며 보안 설정을 바꾸지 않습니다.

1. [현재 실습 저장소](https://github.com/junwoojeong100/microsoft-foundry-labs-v1.5)를 열고 `.devcontainer/devcontainer.json`이 있는 실습 브랜치를 선택합니다. **Code → Codespaces → … → New with options**를 엽니다. ZIP을 다시 받거나 `git clone`을 할 필요는 없습니다.
2. **비용 부담 주체·허용량·Region·Machine type**을 확인합니다. 기본 실습은 작은 2-core 구성을 출발점으로 삼을 수 있으며 조직이 허용한 구성을 선택합니다. 이 Region은 개발 환경의 위치이며 이후 Microsoft Azure의 리전·모델 처리 범위를 정하지 않습니다. [GitHub 사용량·비용](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces)은 Microsoft Azure 비용과 별도입니다. 무료라고 가정하지 말고 확인한 뒤 **Create codespace**를 선택합니다.
3. 브라우저의 VS Code가 열려도 **post-create 설치가 끝날 때까지 기다립니다.** 터미널에 `Lab tools ready.`가 보여야 합니다. 저장소 설정이 Python 3.13·Microsoft Azure CLI·Bicep·Python 확장·`.venv`·기본/MCP 패키지를 준비하고 `.env`가 없을 때만 템플릿을 복사합니다. Microsoft Azure 로그인·자원 생성·역할 부여는 하지 않습니다.
4. **Terminal → New Terminal**을 열고 `samples`·`data`·`requirements.txt`가 보이는 실습 루트에서 아래를 실행합니다. **PC가 Windows여도 이 터미널은 Linux/Bash**이므로 PowerShell 명령으로 바꾸지 않습니다.

```bash
python --version
python -c "import sys; print(sys.executable)"
az version
python samples/workshop.py doctor
python samples/workshop.py validate-data
```

<div class="command-explanation" markdown="1">

**명령 해설 — Codespaces 준비 확인**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python --version` | 선택된 Python 버전을 확인합니다. | `Python 3.13.x`. Microsoft Azure 요청 없음. |
| 2. `python -c` | 실제 실행기 경로를 읽습니다. | 이 실습 폴더의 `.venv/bin/python`이어야 합니다. |
| 3. `az version` | 준비된 CLI 버전을 읽습니다. | `azure-cli` 2.86.0 기준. 로그인 검사가 아닙니다. |
| 4. `doctor` | SDK와 `.env` 준비 상태를 확인합니다. | 기본 SDK가 설치되어 있어야 하며 endpoint 연결 검사는 아닙니다. |
| 5. `validate-data` | 동봉 합성 데이터의 구조를 검사합니다. | 20건·dev 10·holdout 10·재고 3건. 모델 평가가 아닙니다. |

</div>

**다음:** 위 결과가 맞으면 PC 설치·가상환경 생성은 건너뛰고 **[2. 로그인·구독·권한·비용 확인](#l01-sign-in)**으로 갑니다. Microsoft Azure 준비가 없다면 [L06 로컬 함수](#l06)로 이동합니다. `.env`의 프로젝트 값은 자원을 만든 뒤 이 장의 5단계에서 채웁니다.

| 막힌 곳 | 다음 행동 |
| --- | --- |
| Codespaces 메뉴 없음·생성 거절 | 저장소 접근·조직 허용·GitHub 사용량을 확인합니다. 허용되지 않으면 PC 경로를 사용합니다. |
| `Lab tools ready.`가 안 나옴·패키지 설치 실패 | 생성 로그의 첫 오류와 승인된 패키지 접근을 확인합니다. 해결한 뒤 같은 터미널에서 `bash .devcontainer/post-create.sh`를 재실행할 수 있습니다. 기존 `.env`·소유 기록은 보존합니다. |
| 실행기 경로가 다름 | 새 터미널을 열거나 `source .venv/bin/activate` 후 재확인합니다. Microsoft Azure 환경을 다시 만들지 않습니다. |

다음 날에는 [내 Codespaces](https://github.com/codespaces)에서 **같은 Codespace를 다시 시작**합니다. `.env`·`results/`는 같은 환경의 기록이며 새 Codespace에 자동 이전된다고 가정하지 않습니다. 언어별로 다른 Codespace를 사용하고 결과·인증 정보를 Git에 올리지 않습니다. **[L19에서 Codespace도 중지](#l12-codespaces)**해야 하며 브라우저 탭을 닫는 것만으로 중지되지 않습니다. 심화용 azd·`.venv-live`·`.venv-advanced`는 해당 장을 선택할 때만 준비합니다.

[공식 생성 안내](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository) · [개발 컨테이너 구성](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers)

</details>

**이미 설치했다면 설치 설명을 다시 따라 하지 않습니다.** 자기 OS의 버전 확인 → [실습 파일·가상환경](#l01-local) → [Python 선택](#l01-interpreter) 순으로 갑니다. 처음이라면 아래에서 **자기 OS의 절만** 따라 설치합니다. Microsoft Azure 계정이 없다면 PC·로컬 검사까지 진행하고 2단계 이후는 보류합니다.

조직이 허용한 경로로 Python, Microsoft Azure CLI, VS Code를 준비합니다. **설치되어 있으면 아래 확인부터 하고, 필요한 도구만 설치합니다.** 조직의 소프트웨어 배포 포털·승인된 설치 파일·패키지 저장소를 우선 사용합니다. 아래 공식 다운로드 절차도 조직이 허용한 경우에만 따릅니다. 설치나 다운로드가 차단되면 승인된 배포 경로를 확보하고 진행하며, 보안 경고·인증서 검증·실행 정책을 우회하지 않습니다.

| 도구 | 이 실습에서 하는 일 | 준비 완료 기준 |
| --- | --- | --- |
| Python 3.13 | PC에서 실제 Python 코드와 Microsoft Foundry SDK를 실행합니다. | 버전 확인에 `Python 3.13.x`가 출력됩니다. |
| Microsoft Azure CLI | Microsoft Azure 로그인과 실습 자원 생성·조회를 수행합니다. | `az version`에 `azure-cli` 버전이 출력됩니다. 이 키트 기준은 2.86.0입니다. |
| VS Code | 코드를 읽고 수정하고 PC 터미널을 엽니다. | 실습 폴더와 Python 파일을 열 수 있습니다. Python 확장은 아래에서 준비합니다. |

<a id="l01-python"></a>

#### Python 3.13 설치·확인

**Windows**

<details class="setup-detail" markdown="1">
<summary>Python 3.13이 없을 때만: Windows 설치 방법</summary>

1. [Python 다운로드](https://www.python.org/downloads/windows/)에서 **3.13.x 릴리스**를 선택하고 PC에 맞는 설치 파일을 받습니다. 기본 화면의 최신 버전이 3.13이라는 뜻은 아닙니다. `embeddable package`가 아닌 일반 설치 파일을 사용합니다.
2. 승인된 설치 파일을 실행합니다. 일반 설치 파일에서는 **Add python.exe to PATH**를 선택하고, `pip`와 Python launcher (`py`)를 포함해 설치합니다. 설치 화면의 **Install Now** 또는 조직이 정한 설치 옵션을 따릅니다.
3. 설치 후 열려 있던 터미널을 닫고 새 **PowerShell**을 엽니다. 다음 명령으로 3.13을 직접 선택합니다.

</details>

```powershell
py -3.13 --version
```

<div class="command-explanation" markdown="1">

**명령 해설 — Windows**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `py -3.13 --version` | 설치된 Python 3.13의 버전을 출력합니다. | 로컬 확인. 설치·로그인·Microsoft Azure 요청 없음. |

</div>

<details class="setup-detail" markdown="1">
<summary>Python 3.13이 없을 때만: macOS/Linux 설치 방법</summary>

**macOS**

1. [Python 다운로드](https://www.python.org/downloads/macos/)에서 설치 파일이 제공되는 **3.13.x 릴리스**를 선택합니다. **macOS 64-bit universal2 installer** (`.pkg`)는 Apple Silicon·Intel Mac용입니다.
2. 승인된 `.pkg`를 열고 설치 화면의 버전·설치 위치를 확인해 진행합니다. macOS가 기본 제공하는 Python을 삭제하거나 교체하지 않습니다.
3. python.org 배포판은 **응용 프로그램 → Python 3.13 → Install Certificates.command**로 기본 인증서 설정을 마칩니다. 조직이 별도 인증서·프록시 설정을 요구하면 승인된 설정을 따르며, 인증서 검증을 끄지 않습니다.

**Linux — Ubuntu/Debian 예시**

조직이 허용한 패키지 저장소에서 `python3.13`과 `python3.13-venv`를 제공하는 경우에만 다음을 실행합니다. 배포판에 따라 패키지 제공 여부가 다릅니다. 제공하지 않으면 임의의 외부 저장소를 추가하지 말고 승인된 Python 3.13 배포본을 준비합니다.

```bash
sudo apt install python3.13 python3.13-venv
```

<div class="command-explanation" markdown="1">

**명령 해설 — Ubuntu/Debian**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `apt install ...` | Python 3.13과 가상환경 생성 지원을 설치합니다. | 승인된 저장소의 패키지 다운로드·PC 변경. Microsoft Azure 요청 없음. |

</div>

</details>

macOS/Linux에서는 새 터미널에서 다음을 확인합니다.

```bash
python3.13 --version
```

<div class="command-explanation" markdown="1">

**명령 해설 — macOS/Linux**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python3.13 --version` | 실행할 Python 3.13의 버전을 출력합니다. | `Python 3.13.x`의 `x`는 실제 패치 번호입니다. Microsoft Azure 요청 없음. |

</div>

3.12·3.14 등 다른 버전만 보이면 준비 완료가 아닙니다. 다른 프로그램의 Python은 그대로 두고, 이 실습에 사용할 3.13을 별도로 준비합니다.

<a id="l01-azure-cli"></a>

<a id="l01-azure-cli-설치확인"></a>

#### Microsoft Azure CLI 설치·확인

<details class="setup-detail" markdown="1">
<summary>az 명령이 없을 때만: OS별 Microsoft Azure CLI 설치 방법</summary>

**Windows**

1. [공식 Windows 설치 안내](https://learn.microsoft.com/cli/azure/install-azure-cli-windows)의 **Microsoft Installer (MSI)** 절을 엽니다. 일반적인 x64 PC는 64-bit MSI를 사용하며, 다른 아키텍처는 공식 지원 범위와 조직 배포본을 확인합니다.
2. 키트 기준 2.86.0이 필요하면 같은 안내의 **Specific version** 절 또는 [공식 2.86.0 x64 MSI](https://azcliprod.blob.core.windows.net/msi/azure-cli-2.86.0-x64.msi)를 사용합니다. 승인된 MSI를 실행하고 설치를 마칩니다. PC 변경 승인이 필요하면 조직의 승인 절차를 따릅니다.
3. 설치 후 PowerShell과 VS Code를 완전히 닫았다가 다시 엽니다.

**macOS**

조직이 허용한 [Homebrew](https://docs.brew.sh/Installation)가 **이미 준비된 경우**, [공식 macOS 설치 안내](https://learn.microsoft.com/cli/azure/install-azure-cli-macos)에 따라 다음을 실행합니다. Homebrew가 없거나 허용되지 않으면 먼저 승인된 설치 경로를 확보합니다.

Homebrew부터 필요한 경우에는 조직 소프트웨어 포털의 승인 배포본을 사용합니다. 공식 다운로드가 허용된 Apple Silicon Mac에서는 위 Homebrew 설치 안내에 연결된 공식 릴리스의 `.pkg`를 받아 설치할 수도 있습니다. OS·CPU 지원 조건과 설치 후 PATH 설정을 확인하고 새 터미널의 `brew --version`이 정상 출력되는지 확인한 뒤 아래로 진행합니다.

```bash
brew install azure-cli
```

<div class="command-explanation" markdown="1">

**명령 해설 — macOS**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `brew install azure-cli` | Homebrew에서 제공하는 Microsoft Azure CLI와 필요한 의존성을 설치합니다. | 다운로드·PC 변경. 실습용 Python 3.13 준비와는 별도이며 Microsoft Azure 요청 없음. |

</div>

**Linux — Ubuntu/Debian 예시**

[공식 Linux 설치 안내](https://learn.microsoft.com/cli/azure/install-azure-cli-linux?pivots=apt)에서 지원 배포판을 확인합니다. Microsoft 패키지 저장소 또는 조직 미러가 **이미 승인·설정되어 있고** `azure-cli`를 제공할 때 다음을 실행합니다. 저장소가 없으면 먼저 승인된 저장소 설정을 완료하며, 내려받은 스크립트를 무조건 실행하지 않습니다.

```bash
sudo apt install azure-cli
```

<div class="command-explanation" markdown="1">

**명령 해설 — Ubuntu/Debian**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `apt install azure-cli` | 설정된 승인 저장소에서 Microsoft Azure CLI를 설치합니다. | 다운로드·PC 변경. Microsoft Azure 로그인·자원 생성 없음. |

</div>

</details>

**모든 OS에서 확인:** 새 PC 터미널에서 다음을 실행합니다. PowerShell에서도 같은 명령입니다.

```bash
az version
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az version` | 로컬 Microsoft Azure CLI와 설치된 확장 버전을 출력합니다. | 로그인·권한·Microsoft Azure 연결 확인은 아닙니다. 모델 호출·자원 생성 없음. |

</div>

결과의 `azure-cli` 값을 기록합니다. 최신 MSI·Homebrew·apt는 키트 기준 2.86.0과 다른 버전을 제공할 수 있습니다. 다른 승인 버전을 사용하면 이후 명령의 동작을 확인하며, 임의로 업그레이드·다운그레이드하지 않습니다. **Microsoft Azure 로그인은 아래 2단계에서 합니다.**

<a id="l01-vscode"></a>

#### VS Code 설치·실습 폴더 열기

<details class="setup-detail" markdown="1">
<summary>VS Code가 없을 때만: OS별 설치 방법</summary>

**Windows:** [VS Code 다운로드](https://code.visualstudio.com/download)에서 PC에 맞는 **User Installer**를 받아 승인된 설치 옵션으로 설치합니다. 조직 배포본이 있으면 그것을 사용합니다. 시작 메뉴에서 **Visual Studio Code**를 엽니다.

**macOS:** 같은 다운로드 화면에서 Apple Silicon·Intel에 맞는 배포본 또는 Universal을 받습니다. 배포본의 `.dmg` 또는 `.zip`을 열고 **Visual Studio Code.app → 응용 프로그램(Applications)**으로 옮긴 뒤 실행합니다.

**Linux:** 다운로드 화면에서 배포판에 맞는 `.deb` 또는 `.rpm`을 선택하고, 승인된 소프트웨어 설치 프로그램으로 설치합니다. 패키지 저장소 추가를 요청하면 조직이 허용한 설정만 적용합니다.

</details>

VS Code 창이 열리면 **도움말 → 정보**(macOS는 **Code → About Visual Studio Code**)에서 설치 버전을 확인합니다. `code` 터미널 명령이 없어도 다음 폴더 열기로 진행할 수 있습니다.

ZIP을 풀고 **VS Code → 파일 → 폴더 열기**로 `samples`·`data`·`requirements.txt`가 함께 있는 폴더를 엽니다. **터미널 → 새 터미널**을 선택합니다. 여기서 터미널은 내 PC의 셸이며, 브라우저 주소창·Cloud Shell·Python `>>>` 입력창이 아닙니다. `>>>`가 보이면 `exit()`로 나옵니다.

왼쪽 **확장(Extensions)**에서 `Python`을 검색하고 게시자가 **Microsoft**, 확장 ID가 **`ms-python.python`**인 항목을 확인합니다. 이미 있으면 다시 설치하지 않으며, 없으면 조직이 허용한 확장 배포 경로로 설치합니다. 이 확장은 Python 실행기 자체를 설치하지 않습니다. 확장 설치가 허용되지 않아도 아래 PC 터미널 명령으로 실습할 수 있습니다.

**준비가 막혔을 때**

| 증상 | 확인·조치 |
| --- | --- |
| `py`·`python3.13`을 찾을 수 없음 | 새 터미널에서 다시 확인하고 승인된 설치 경로·launcher·PATH 설정을 점검합니다. Windows의 `python`이 Store를 여는 경우에는 위 `py -3.13`으로 확인합니다. |
| `az`를 찾을 수 없음 | 설치 완료 후 VS Code까지 다시 열고 승인된 CLI 설치 경로가 PATH에 있는지 확인합니다. |
| 다운로드·인증서·프록시 오류 | 조직이 허용한 저장소·프록시·인증서 설정을 확인합니다. SSL 검증 해제나 보안 정책 변경으로 넘기지 않습니다. |
| 확장을 설치할 수 없음 | 승인된 확장 배포본을 사용하거나 터미널 실습 경로로 진행합니다. |

<a id="l01-local"></a>

#### 실습 파일 검사·가상환경 만들기

먼저 표준 라이브러리만 사용하는 두 검사를 실행합니다. Windows에서는 `python3.13` 대신 `py -3.13`을 사용합니다.

```bash
python3.13 samples/workshop.py doctor
python3.13 samples/workshop.py validate-data
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `doctor` | Python·SDK 설치 상태와 `.env` 존재 여부를 출력합니다. | 로컬 검사. CLI 로그인이나 Microsoft Azure 연결을 검사하지 않습니다. |
| 2. `validate-data` | 합성 데이터 형식·시나리오 분리·재고를 검사합니다. | 데이터 구조 확인이며 모델 품질 평가는 아닙니다. |

</div>

```output
Validated 20 cases: dev=10, holdout=10; scenario overlap=0; inventory=3.
```

`doctor`의 `not installed (needed only for --live)`는 아래 설치 단계가 남았다는 뜻입니다. 여기의 20건은 기존 dev/holdout 자료이고, L08의 고정 12문항 비교와는 다릅니다.

아래 가상환경 생성·설치는 처음 한 번만 합니다. 이 폴더에 준비된 `.venv`가 이미 있으면 [새 터미널에서 재개](#l01-new-terminal)로 이동합니다.

macOS/Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

<div class="command-explanation" markdown="1">

**명령 해설 — macOS/Linux**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `venv .venv` | 이 폴더 전용 Python 환경을 만듭니다. | 로컬 폴더 생성. |
| 2. `source .../activate` | 현재 터미널의 Python을 선택합니다. | 새 터미널에서는 다시 선택합니다. |
| 3. `pip install -r ...` | 선언된 SDK 의존성을 설치합니다. | 패키지 다운로드·로컬 설치. Microsoft Azure 요청 없음. |
| 4. `cp -n ...` | 없는 경우에만 설정 템플릿을 복사합니다. | 기존 `.env`를 보존합니다. |

</div>

Windows PowerShell에서는 위 블록 **대신** 실행합니다.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

<div class="command-explanation" markdown="1">

**명령 해설 — Windows**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `py -3.13 -m venv` | Python 3.13으로 가상환경을 만듭니다. | 로컬 폴더 생성. |
| 2. `.venv\Scripts\python.exe -m pip ...` | 해당 환경에 SDK를 설치합니다. | 활성화나 실행 정책 변경이 필요 없습니다. |
| 3. `if ... Copy-Item` | `.env`가 없을 때만 복사합니다. | 기존 설정을 덮어쓰지 않습니다. |

</div>

이후 `python`은 이 가상환경의 Python입니다. Windows는 `.\.venv\Scripts\python.exe`로 바꿉니다. 한국어 데이터가 기본값이며, 영어 실습은 별도 폴더에서 해당 언어의 L01을 따릅니다.

<a id="l01-interpreter"></a>

#### VS Code에서 실습용 Python 선택하기

Python 확장을 준비한 경우, 위에서 만든 `.venv`를 편집기의 실행·디버깅에도 사용합니다.

1. `samples/first_response.py`를 열어 Python 파일을 표시합니다.
2. **Ctrl+Shift+P**(macOS **Cmd+Shift+P**)로 명령 팔레트를 열고 **Python: Select Interpreter**를 선택합니다.
3. 이 실습 폴더의 **Python 3.13 (`.venv`)**를 선택합니다. 목록에 없으면 **Enter interpreter path**로 macOS/Linux는 `.venv/bin/python`, Windows는 `.venv\Scripts\python.exe`를 직접 선택합니다.
4. 창 아래 상태 표시줄에서 선택한 환경을 확인합니다. 편집기의 선택이 기존 터미널의 실행기를 바꿨다고 가정하지 말고, 아래 경로 검사도 수행합니다. Windows 터미널 명령은 계속 `.\.venv\Scripts\python.exe`를 사용합니다.

<a id="l01-new-terminal"></a>

#### 새 터미널이나 다음 날 다시 시작하기

VS Code에서 **같은 실습 폴더 → 터미널 → 새 터미널**을 엽니다. 가상환경을 다시 만들거나 패키지를 재설치하지 않습니다. L07의 두 터미널에서도 각각 아래의 **자기 OS 블록 하나만** 실행하세요.

**macOS/Linux**

```bash
source .venv/bin/activate
python -c "import sys; print('Python', sys.version.split()[0]); print(sys.executable)"
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `source .venv/bin/activate` | 이 터미널에서 기본 실습의 Python을 선택합니다. | 로컬 셸만 변경합니다. |
| 2. `python -c` | 현재 실행기의 **버전과 경로**를 출력합니다. | `Python 3.13.x`와 이 폴더의 `.venv/bin/python`이 함께 맞아야 합니다. Microsoft Azure 요청 없음. |

</div>

**Windows PowerShell**

```powershell
.\.venv\Scripts\python.exe -c "import sys; print('Python', sys.version.split()[0]); print(sys.executable)"
```

<div class="command-explanation" markdown="1">

**명령 해설 — Windows**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `.venv\Scripts\python.exe -c` | 가상환경의 실행기를 직접 선택하고 **버전과 경로**를 출력합니다. | `Python 3.13.x`와 이 폴더의 `.venv\Scripts\python.exe`가 함께 맞아야 합니다. 활성화·실행 정책 변경·Microsoft Azure 요청 없음. |

</div>

이후 기본 명령의 `python`도 Windows에서는 `.\.venv\Scripts\python.exe`로 바꿉니다. 경로가 없으면 현재 폴더를 확인하고, 실제로 가상환경을 만들지 않은 경우에만 위 생성 단계로 돌아갑니다.

**기존 `.venv`가 3.12·3.14 등이라면 재사용하지 않습니다.** 기존 환경을 삭제하거나 덮어쓰지 말고, Python 3.13으로 `.venv-core313` 같은 새 이름의 환경을 준비합니다. 선택한 경우 이 가이드의 `.venv` 경로를 그 이름으로 일관되게 바꾸고 VS Code에서도 같은 실행기를 선택합니다. 가상환경 변경 때문에 기존 Microsoft Azure 환경이나 소유 기록을 다시 만들지는 않습니다.

<a id="l01-sign-in"></a>

### 2. 로그인·구독·권한·비용 확인하기

**로그인 명령은 실행 환경에 맞는 하나만 선택합니다.** 포털 로그인이나 GitHub 로그인만으로 CLI에 로그인된 것은 아닙니다.

**내 PC 터미널:**

```bash
az login
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az login` | 내 PC의 CLI 인증을 시작합니다. | 비밀번호·MFA는 인증 화면에 직접 입력합니다. 자원 생성 없음. |

</div>

**GitHub Codespaces 터미널:** [device-code 로그인](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively#sign-in-with-a-browser)을 사용합니다.

```bash
az login --use-device-code
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az login --use-device-code` | Codespaces의 CLI 인증을 시작합니다. | 터미널이 안내한 Microsoft 로그인 페이지에서 **자신이 방금 발급한 코드**를 직접 입력하고 MFA를 완료합니다. 코드·토큰·비밀번호를 공유하지 않습니다. 자원 생성 없음. |

</div>

조직 정책이 device-code 로그인을 막으면 허용된 실행·인증 경로를 확인합니다. MFA·Conditional Access를 끄거나 장기 secret으로 우회하지 않습니다.

**두 경로 공통:** 로그인 후 아래를 한 줄씩 실행합니다. 목록에서 사용할 구독 ID를 찾은 뒤 자리표시자를 바꿉니다.

```bash
az account list --query "[].{subscription:name,id:id,tenant:tenantId,state:state}" -o table
az account set --subscription "실제-구독-ID"
az account show --query "{subscription:name,id:id,tenant:tenantId,state:state}" -o table
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az account list` | 내 계정으로 접근 가능한 구독·테넌트·상태를 나열합니다. | 사용할 Enabled 구독의 ID를 찾습니다. 모델 호출·자원 생성 없음. |
| 2. `az account set` | `실제-구독-ID`를 자신의 값으로 바꿔 기본 대상을 선택합니다. | 로컬 CLI 대상 변경. 권한을 부여하지 않습니다. |
| 3. `az account show` | **선택 후** 현재 대상의 구독·테넌트·상태를 다시 읽습니다. | 선택한 ID와 Enabled 상태가 맞아야 생성 단계로 갑니다. |

</div>

Microsoft Azure 포털의 **구독 → Access control (IAM) → View my access**에서 위 준비표의 권한을 확인합니다. 생성 권한과 역할 부여 권한을 구분하세요. 이후 역할은 자신의 실습 프로젝트·리소스에만 부여합니다.

화면에 예전 이름 **Azure AI User**가 보일 수 있습니다. 현재 **Foundry User**와 역할 ID·핵심 권한이 같은 이름 변경이며, 새 역할을 중복 부여할 이유는 아닙니다.

예산에는 **금액·사용할 서비스·중단 시점·보존 기한**을 적습니다. 예산 알림, TPM/RPM, 로그 수집 제한은 총 과금을 강제로 차단하는 장치가 아닙니다. 한도를 넘으면 새 요청·예약을 중지하고 [L19](#l12)에서 남은 자원을 확인합니다.

### 3. 내 실습 전용 리소스 그룹 만들기

기본 경로는 동봉 코드로 **새 전용 환경**을 만들고 포털에서 확인하는 방식입니다. 기존 공용 환경에 손대지 않으며, 자동 생성한 이름과 소유 태그를 `results/azure-environment.json`에 기록합니다. 이 기록은 이후 평가·검색·배포의 대상 확인에 필요합니다.

아래 명령의 세 자리표시자를 먼저 바꿉니다.

| 자리표시자 | 넣을 값 | 확인할 곳 |
| --- | --- | --- |
| `실제-구독-ID` | 사용할 구독의 ID | 위 `az account show`의 `id`. 표시 이름이나 tenant ID가 아님 |
| `허용-리전` | 승인받은 Microsoft Azure 지역 **코드** | 예: `eastus`. 포털의 번역된 표시 이름을 넣지 않으며, 예시 지역의 모델 가용성을 보장하지 않음 |
| `"승인된 금액·사용 범위·보존 기한"` | 자신이 승인받은 금액·서비스 범위·종료/보존 기한 | 2단계의 실제 비용 승인 기록. 이 문자열을 입력한다고 승인이나 권한이 생기지 않음 |

```bash
python scripts/azure_environment.py create
```

<div class="command-explanation" markdown="1">

**명령 해설 — 먼저 계획만 읽습니다.**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `create` | 전용 환경 생성 계획을 출력합니다. | `PLAN ONLY`. 로그인·권한 검증이나 Microsoft Azure 요청 없음. |

</div>

**실제 생성:** 위 세 값을 바꿨고 해당 구독·지역·비용 범위를 승인받았다면 다음 한 줄을 실행합니다.

```bash
python scripts/azure_environment.py create --subscription 실제-구독-ID --location 허용-리전 --cost-authorization "승인된 금액·사용 범위·보존 기한" --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `create ... --live` | 구독·지역·비용 범위를 기록하고 고유 RG를 만듭니다. | 실제 Microsoft Azure 생성. 기존 RG나 소유 기록을 덮어쓰지 않습니다. |

</div>

**여기서 멈춰 확인:** `results/azure-environment.json`의 `resource_group`·`location`을 Microsoft Azure 포털 **Resource groups**의 이름·지역·소유 태그와 대조합니다. 일치해야 4단계로 갑니다. `.env`나 소유 기록을 공유·커밋하지 않습니다. 기록이 이미 있다면 지우고 재시작하지 말고 해당 자원의 상태를 먼저 확인합니다.

<a id="l01-4-foundry-프로젝트모델필요한-역할-만들기"></a>

### 4. Microsoft Foundry 프로젝트·모델·필요한 역할 만들기

아래 `foundation`은 [main.bicep](../infra/main.bicep)로 **Microsoft Foundry 리소스·프로젝트·chat/judge/embedding 배포 3개**를 만듭니다. chat은 기본 실습, judge는 L08 평가, embedding은 선택 L11/L15용입니다. 모델 호출은 아직 보내지 않습니다.

이 키트의 모델 구성은 `gpt-6-sol / 2026-09-22`, `gpt-4.1 / 2025-04-14`, `text-embedding-3-small / 1`로 고정되어 있습니다. 자신의 지역·구독에서 지원되는지 확인하세요. 지원되지 않으면 해당 조건을 기록하고 중단합니다. 다른 모델로 바꿔 같은 검증이라고 기록하지 않습니다.

```bash
python scripts/azure_environment.py foundation --learners 1 --max-capacity 100
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `foundation` | 1인 기준 권장 TPM/RPM과 capacity 산정 계획을 표시합니다. | 로컬 계산. 지역 가용성·quota 검증은 아직 하지 않습니다. |

</div>

**실제 배포:** 모델·처리 범위·처리량 계획이 승인된 범위와 맞을 때 실행합니다.

```bash
python scripts/azure_environment.py foundation --chat-model gpt-6-sol --chat-version 2026-09-22 --judge-model gpt-4.1 --judge-version 2025-04-14 --embedding-model text-embedding-3-small --embedding-version 1 --model-sku GlobalStandard --learners 1 --max-capacity 100 --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `foundation ... --live` | 실제 카탈로그·quota를 확인하고 전용 RG에 프로젝트·모델을 배포합니다. | 실제 생성. 배포당 capacity 상한 100이며 비용 금액 상한이 아닙니다. 모델별 단위로 환산하고 실제 한도를 재조회합니다. |

</div>

**여기서 멈춰 확인:** 명령이 오류 없이 끝났고 소유 기록의 `operations`에 `step=foundation`, `status=Succeeded`가 함께 있는지 확인합니다. 부분 실패·시간 초과라면 역할 부여로 넘어가지 말고 아래 복구 안내를 읽습니다.

**역할 부여:** 배포가 완료됐고 대상 프로젝트·부모 리소스의 역할 부여 권한이 있을 때만 실행합니다.

```bash
python scripts/azure_environment.py roles --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `roles --live` | 현재 사용자와 프로젝트 관리 ID에 소유 프로젝트·부모 리소스의 필요한 데이터 역할을 부여합니다. | 실제 접근 권한 변경. `roleAssignments/write`가 필요하며 구독 전체 역할을 생성하지 않습니다. |

</div>

**포털 확인:** [Microsoft Foundry](https://ai.azure.com)의 **New Foundry**에서 자신의 프로젝트를 열고 **Manage → Project details**의 Name·Parent resource·Location을 소유 기록과 대조합니다. **Build → Models → Deployments**에 `contoso-chat`, `contoso-judge`, `contoso-embedding`이 준비됐는지 확인합니다. 포털에서 같은 프로젝트나 모델을 다시 만들지 않습니다.

| 생성 코드 | 포털에서 확인할 결과 |
| --- | --- |
| `create`의 RG 생성 | Microsoft Azure Resource groups의 고유 이름·소유 태그 |
| `foundation`의 Microsoft Foundry account/project | Microsoft Foundry 프로젝트 이름·부모 리소스·지역 |
| Bicep의 모델 deployments | Model ID·version과 배포 이름 `contoso-chat` 등 |
| `roles`의 scope별 role assignment | 대상 자원의 IAM에서 사용자/관리 ID와 범위 |

부분 실패는 원본 오류와 deployment operation을 보존합니다. 같은 소유 자원의 부분 배포를 재개할 때만 `foundation --resume --live`를 **동일 모델·SKU 인수와 함께** 사용합니다. 새 환경으로 바꾸거나 기록을 덮어쓰는 옵션이 아닙니다.

### 5. 로그 연결과 로컬 설정 완성하기

L04 이후 실행을 L10에서 다시 보기 위해 **첫 agent 호출 전에** 로그를 연결합니다.

```bash
python scripts/azure_environment.py monitoring
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `monitoring` | 로그 자원·프로젝트 연결 계획을 표시합니다. | Microsoft Azure 요청 없음. |

</div>

**실제 연결:** 기존 연결이 없고 로그 수집·보관 비용까지 승인된 범위라면 실행합니다.

```bash
python scripts/azure_environment.py monitoring --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `monitoring --live` | 소유 RG에 Log Analytics·Application Insights와 프로젝트 연결을 만듭니다. | 로그 수집·보관 비용 가능. 기록된 기존 연결을 덮어쓰지 않습니다. |

</div>

**Agents → Traces** 또는 **Manage → Project details → Connected resources**에서 연결을 확인합니다. 로그 조회에는 대상 Application Insights/Log Analytics의 읽기 권한이 필요합니다. 필요할 경우 자신의 자원 IAM에서 `Log Analytics Reader` 등 필요한 최소 역할을 설정합니다. 보호된 테이블에는 추가 권한이 필요할 수 있습니다.

모델·에이전트 SDK 호출은 Entra 인증을 사용합니다. 동봉 로그 연결은 [observability.bicep](../infra/observability.bicep)이 Microsoft Azure 내부의 연결 문자열을 참조하며 화면·출력에 비밀을 노출하지 않습니다. Entra 기반 로그 수집을 설정했다고 주장하지 않습니다.

![프로젝트 설정 예시. Manage → Project details에서 프로젝트·상위 리소스·리전과 Connected resources를 확인한다.](../assets/portal/13-project-settings.png)

VS Code에서 `.env`를 열고 자신의 값으로 저장합니다. 아래는 **파일 설정**이며 터미널 명령이 아닙니다.

```env
FOUNDRY_PROJECT_ENDPOINT=https://실제-리소스.services.ai.azure.com/api/projects/실제-프로젝트
FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat
FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge
FOUNDRY_EMBEDDING_DEPLOYMENT_NAME=contoso-embedding
```

`FOUNDRY_PROJECT_ENDPOINT`는 소유 기록의 `project_endpoint` 또는 포털 Home의 **Project endpoint**에서 가져옵니다. `/openai/v1`을 덧붙이지 않습니다. 실제 배포 이름은 소유 기록의 `model_deployments`와 대조합니다. `.env`와 가상환경 `.venv`는 다른 파일/폴더이며, API key를 넣지 않습니다.

**저장 전 확인:** 기존 `.env`의 같은 이름 항목을 **수정**합니다. 예시 블록을 끝에 중복 추가하지 않습니다. `실제-리소스`·`실제-프로젝트`를 자신의 값으로 바꾸고 파일 이름이 `.env.txt`가 아닌 **`.env`**인지 확인합니다. L11을 선택하기 전까지 Search 설정은 비워 둡니다. 셸에 같은 이름의 환경 변수가 있으면 `.env`보다 우선하므로 이전 실습 값이 남아 있지 않은지도 확인합니다.

<details class="implementation-detail" markdown="1">
<summary>구현 참고: 프로젝트에 연결하는 Python — 실행하지 않아도 다음 장으로 진행할 수 있습니다</summary>

다음 연결 코드는 이미 만든 프로젝트를 **사용**합니다. 자원 생성이나 역할 부여 코드는 아닙니다.

```python
from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential

with (
    AzureCliCredential(process_timeout=30) as credential,
    AIProjectClient(endpoint=project_endpoint, credential=credential, retry_total=0) as project,
    project.get_openai_client(max_retries=0, timeout=60.0) as client,
):
    print("Client configured; no model request sent.")
```

</details>

## 성공 기준

내 전용 RG·프로젝트·세 모델·로그 연결을 만들고, 역할·지역·예산을 확인했습니다. 로컬 데이터 검사가 통과하며 포털·`.env`·`results/azure-environment.json`이 같은 환경을 가리킵니다. 계획 출력이나 client 생성만으로 모델 호출 성공이라고 기록하지 않습니다. [L02](#l02)에서 내가 만든 배포를 확인합니다.

## 막혔을 때

401은 CLI 인증, 403은 작업별 권한과 네트워크, 배포 실패는 모델·지역·quota·capacity부터 확인합니다. Private endpoint 환경은 승인된 VPN/VNet 경로에서 접근하며 public access를 임의로 켜지 않습니다. 설치 실패는 현재 Python과 허용된 패키지 저장소를 확인합니다.

## 정리

아직 자원을 삭제하지 않습니다. 소유 기록과 보존 기한을 유지하고 L19에서 반복 실행·남은 비용을 확인합니다. 이 장은 환경 생성이며 답변 품질 검증이 아닙니다.

<div class="lab-handoff" markdown="1">

**이 장에서 남길 것:** `results/azure-environment.json`, 내 `.env`, `.venv` 경로와 권한·예산·보존 기한. 이후 장에서 같은 환경을 사용합니다.

**다음:** 환경을 만들었다면 [L02 배포 확인](#l02). Microsoft Azure 조건이 아직 없다면 [L06 로컬 함수](#l06)까지만 연습하고 실제 환경 생성은 미실행으로 기록합니다.

</div>
