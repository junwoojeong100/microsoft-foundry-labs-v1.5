> **완성할 결과:** 내가 만든 실습 전용 리소스 그룹·Foundry 프로젝트·모델 배포·로그 연결과, 실행할 Python 환경.

<div class="lab-brief" markdown="1">

**진행 방식:** PC 준비 → 로그인·권한 확인 → 전용 환경 생성 → 설정·로그 연결.

**먼저 할 일:** 실습 ZIP을 풀어 VS Code에서 열고, 사용할 Azure 구독·지역·예산을 확인합니다.

**확인할 결과:** `results/azure-environment.json`의 내 프로젝트와 포털의 자원이 일치합니다. 첫 모델 요청은 L03에서 보냅니다.

</div>

## 목표

**실습 참여자가 필요한 환경을 직접 만듭니다.** 이후 장은 이 프로젝트와 소유 기록을 이어 사용합니다. 생성·조회·역할 부여에 필요한 Azure 권한은 작업 조건이며, 가이드의 참여자를 별도 역할로 나누는 기준이 아닙니다.

## 개념과 실습 지도

**경험할 기능:** Foundry 프로젝트·모델·권한·로그와 로컬 Python 환경을 준비합니다.

**무엇이며 왜 중요한가요?** 구독은 비용 범위, 리소스 그룹은 자원 묶음, 프로젝트는 에이전트 작업 공간입니다. 로그인은 신원, RBAC는 허용 작업, quota는 사용 가능한 용량입니다.

**어떻게 사용하나요?** 전용 환경을 만들고 포털의 실제 이름·주소를 `.env`와 소유 기록에 대조합니다. 주소를 안다고 권한이 생기지는 않습니다.

**어디서 실행하나요?** PC의 VS Code 터미널에서 명령을 실행하고 Azure·Foundry 포털에서 결과를 확인합니다. [환경 생성 코드](../scripts/azure_environment.py)와 [Bicep](../infra/main.bicep)이 실제 생성 범위를 정의합니다.

## 준비

| 준비할 것 | 확인할 내용 |
| --- | --- |
| Azure 계정·사용 가능한 구독 | 자신의 계정으로 로그인할 수 있고 구독이 Enabled인지 |
| 생성 권한 | 리소스 그룹 생성과 그 안의 Foundry·로그 자원 배포 권한 |
| 역할 부여 권한 | 대상 범위의 `Microsoft.Authorization/roleAssignments/write`. `Contributor`만으로는 역할을 부여할 수 없음 |
| quota 조회 권한 | 구독의 `Cognitive Services Usages Reader` 등 모델 사용량 조회 권한 |
| 지역·예산 | 모델 지원 지역, 허용된 처리 범위, 지출 한도·중단 기준·보존 기한 |
| PC | Python 3.13, Azure CLI 2.86.0 기준, VS Code, 인터넷·허용된 패키지 저장소 |

자신의 구독이라도 실제 권한을 먼저 확인합니다. 조직 구독에서는 필요한 범위의 권한·비용 승인을 확보한 뒤 진행합니다. 권한이 없으면 해당 작업을 보류하며, 오류를 우회하려고 보안을 끄거나 구독 전체 권한을 확대하지 않습니다. 계정·권한 없이도 로컬 연습은 가능하지만 **Foundry 실행 완료와는 별도**입니다.

<a id="l01-pc"></a>

## 실행

### 1. PC와 실습 파일 준비하기

조직이 허용한 경로로 Python, Azure CLI, VS Code를 준비합니다. **설치되어 있으면 아래 확인부터 하고, 필요한 도구만 설치합니다.** 조직의 소프트웨어 배포 포털·승인된 설치 파일·패키지 저장소를 우선 사용합니다. 아래 공식 다운로드 절차도 조직이 허용한 경우에만 따릅니다. 설치나 다운로드가 차단되면 승인된 배포 경로를 확보하고 진행하며, 보안 경고·인증서 검증·실행 정책을 우회하지 않습니다.

| 도구 | 이 실습에서 하는 일 | 준비 완료 기준 |
| --- | --- | --- |
| Python 3.13 | PC에서 실제 Python 코드와 Foundry SDK를 실행합니다. | 버전 확인에 `Python 3.13.x`가 출력됩니다. |
| Azure CLI | Azure 로그인과 실습 자원 생성·조회를 수행합니다. | `az version`에 `azure-cli` 버전이 출력됩니다. 이 키트 기준은 2.86.0입니다. |
| VS Code | 코드를 읽고 수정하고 PC 터미널을 엽니다. | 실습 폴더와 Python 파일을 열 수 있습니다. Python 확장은 아래에서 준비합니다. |

<a id="l01-python"></a>

#### Python 3.13 설치·확인

**Windows**

1. [Python 다운로드](https://www.python.org/downloads/windows/)에서 **3.13.x 릴리스**를 선택하고 PC에 맞는 설치 파일을 받습니다. 기본 화면의 최신 버전이 3.13이라는 뜻은 아닙니다. `embeddable package`가 아닌 일반 설치 파일을 사용합니다.
2. 승인된 설치 파일을 실행합니다. 일반 설치 파일에서는 **Add python.exe to PATH**를 선택하고, `pip`와 Python launcher (`py`)를 포함해 설치합니다. 설치 화면의 **Install Now** 또는 조직이 정한 설치 옵션을 따릅니다.
3. 설치 후 열려 있던 터미널을 닫고 새 **PowerShell**을 엽니다. 다음 명령으로 3.13을 직접 선택합니다.

```powershell
py -3.13 --version
```

<div class="command-explanation" markdown="1">

**명령 해설 — Windows**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `py -3.13 --version` | 설치된 Python 3.13의 버전을 출력합니다. | 로컬 확인. 설치·로그인·Azure 요청 없음. |

</div>

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
| 1. `apt install ...` | Python 3.13과 가상환경 생성 지원을 설치합니다. | 승인된 저장소의 패키지 다운로드·PC 변경. Azure 요청 없음. |

</div>

macOS/Linux에서는 새 터미널에서 다음을 확인합니다.

```bash
python3.13 --version
```

<div class="command-explanation" markdown="1">

**명령 해설 — macOS/Linux**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python3.13 --version` | 실행할 Python 3.13의 버전을 출력합니다. | `Python 3.13.x`의 `x`는 실제 패치 번호입니다. Azure 요청 없음. |

</div>

3.12·3.14 등 다른 버전만 보이면 준비 완료가 아닙니다. 다른 프로그램의 Python은 그대로 두고, 이 실습에 사용할 3.13을 별도로 준비합니다.

<a id="l01-azure-cli"></a>

#### Azure CLI 설치·확인

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
| 1. `brew install azure-cli` | Homebrew에서 제공하는 Azure CLI와 필요한 의존성을 설치합니다. | 다운로드·PC 변경. 실습용 Python 3.13 준비와는 별도이며 Azure 요청 없음. |

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
| 1. `apt install azure-cli` | 설정된 승인 저장소에서 Azure CLI를 설치합니다. | 다운로드·PC 변경. Azure 로그인·자원 생성 없음. |

</div>

**모든 OS에서 확인:** 새 PC 터미널에서 다음을 실행합니다. PowerShell에서도 같은 명령입니다.

```bash
az version
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az version` | 로컬 Azure CLI와 설치된 확장 버전을 출력합니다. | 로그인·권한·Azure 연결 확인은 아닙니다. 모델 호출·자원 생성 없음. |

</div>

결과의 `azure-cli` 값을 기록합니다. 최신 MSI·Homebrew·apt는 키트 기준 2.86.0과 다른 버전을 제공할 수 있습니다. 다른 승인 버전을 사용하면 이후 명령의 동작을 확인하며, 임의로 업그레이드·다운그레이드하지 않습니다. **Azure 로그인은 아래 2단계에서 합니다.**

<a id="l01-vscode"></a>

#### VS Code 설치·실습 폴더 열기

**Windows:** [VS Code 다운로드](https://code.visualstudio.com/download)에서 PC에 맞는 **User Installer**를 받아 승인된 설치 옵션으로 설치합니다. 조직 배포본이 있으면 그것을 사용합니다. 시작 메뉴에서 **Visual Studio Code**를 엽니다.

**macOS:** 같은 다운로드 화면에서 Apple Silicon·Intel에 맞는 배포본 또는 Universal을 받습니다. 배포본의 `.dmg` 또는 `.zip`을 열고 **Visual Studio Code.app → 응용 프로그램(Applications)**으로 옮긴 뒤 실행합니다.

**Linux:** 다운로드 화면에서 배포판에 맞는 `.deb` 또는 `.rpm`을 선택하고, 승인된 소프트웨어 설치 프로그램으로 설치합니다. 패키지 저장소 추가를 요청하면 조직이 허용한 설정만 적용합니다.

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
| 1. `doctor` | Python·SDK 설치 상태와 `.env` 존재 여부를 출력합니다. | 로컬 검사. CLI 로그인이나 Azure 연결을 검사하지 않습니다. |
| 2. `validate-data` | 합성 데이터 형식·시나리오 분리·재고를 검사합니다. | 데이터 구조 확인이며 모델 품질 평가는 아닙니다. |

</div>

```output
Validated 20 cases: dev=10, holdout=10; scenario overlap=0; inventory=3.
```

`doctor`의 `not installed (needed only for --live)`는 아래 설치 단계가 남았다는 뜻입니다. 여기의 20건은 기존 dev/holdout 자료이고, L08의 고정 12문항 비교와는 다릅니다.

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
| 3. `pip install -r ...` | 선언된 SDK 의존성을 설치합니다. | 패키지 다운로드·로컬 설치. Azure 요청 없음. |
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

같은 폴더에서 가상환경을 선택하고 경로를 확인합니다. L07의 두 터미널에서도 각각 확인하세요.

```bash
python -c "import sys; print(sys.executable)"
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `python -c` | 현재 실행기의 경로를 출력합니다. | 이 폴더의 `.venv`가 아니면 환경을 다시 선택합니다. 패키지를 재설치하지 않습니다. |

</div>

### 2. 로그인·구독·권한·비용 확인하기

```bash
az login
az account show --query "{subscription:name,id:id,tenant:tenantId,state:state}" -o table
az account set --subscription "실제-구독-ID"
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `az login` | CLI 사용자 인증을 시작합니다. | 비밀번호·MFA는 인증 화면에 직접 입력합니다. 포털 로그인과 별개입니다. |
| 2. `az account show` | 현재 계정의 구독·테넌트·활성 상태를 표시합니다. | 읽기 확인. 모델 호출·자원 생성 없음. |
| 3. `az account set` | `실제-구독-ID`를 자신의 값으로 바꿔 기본 대상을 선택합니다. | 로컬 CLI 대상 변경. 권한을 부여하지 않습니다. |

</div>

Azure 포털의 **구독 → Access control (IAM) → View my access**에서 위 준비표의 권한을 확인합니다. 생성 권한과 역할 부여 권한을 구분하세요. 이후 역할은 자신의 실습 프로젝트·리소스에만 부여합니다.

예산에는 **금액·사용할 서비스·중단 시점·보존 기한**을 적습니다. 예산 알림, TPM/RPM, 로그 수집 제한은 총 과금을 강제로 차단하는 장치가 아닙니다. 한도를 넘으면 새 요청·예약을 중지하고 [L19](#l12)에서 남은 자원을 확인합니다.

### 3. 내 실습 전용 리소스 그룹 만들기

기본 경로는 동봉 코드로 **새 전용 환경**을 만들고 포털에서 확인하는 방식입니다. 기존 공용 환경에 손대지 않으며, 자동 생성한 이름과 소유 태그를 `results/azure-environment.json`에 기록합니다. 이 기록은 이후 평가·검색·배포의 대상 확인에 필요합니다.

```bash
python scripts/azure_environment.py create
python scripts/azure_environment.py create --subscription 실제-구독-ID --location 허용-리전 --cost-authorization "승인된 금액·사용 범위·보존 기한" --live
```

<div class="command-explanation" markdown="1">

**명령 해설 — 계획을 읽은 뒤 자신의 값으로 실행합니다.**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `create` | 전용 환경 생성 계획을 출력합니다. | `PLAN ONLY`. 로그인·권한 검증이나 Azure 요청 없음. |
| 2. `create ... --live` | 구독·지역·비용 범위를 기록하고 고유 RG를 만듭니다. | 실제 Azure 생성. 기존 RG나 소유 기록을 덮어쓰지 않습니다. |

</div>

Azure 포털 **Resource groups**에서 출력된 이름과 지역·태그를 확인합니다. `.env`나 소유 기록을 공유·커밋하지 않습니다. 기록이 이미 있다면 지우고 재시작하지 말고 해당 자원의 상태를 먼저 확인합니다.

### 4. Foundry 프로젝트·모델·필요한 역할 만들기

아래 `foundation`은 [main.bicep](../infra/main.bicep)로 **Foundry 리소스·프로젝트·chat/judge/embedding 배포 3개**를 만듭니다. chat은 기본 실습, judge는 L08 평가, embedding은 선택 L11/L15용입니다. 모델 호출은 아직 보내지 않습니다.

이 키트의 모델 구성은 `gpt-6-sol / 2026-09-22`, `gpt-4.1 / 2025-04-14`, `text-embedding-3-small / 1`로 고정되어 있습니다. 자신의 지역·구독에서 지원되는지 확인하세요. 지원되지 않으면 해당 조건을 기록하고 중단합니다. 다른 모델로 바꿔 같은 검증이라고 기록하지 않습니다.

```bash
python scripts/azure_environment.py foundation --learners 1 --max-capacity 100
python scripts/azure_environment.py foundation --chat-model gpt-6-sol --chat-version 2026-09-22 --judge-model gpt-4.1 --judge-version 2025-04-14 --embedding-model text-embedding-3-small --embedding-version 1 --model-sku GlobalStandard --learners 1 --max-capacity 100 --live
python scripts/azure_environment.py roles --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `foundation` | 1인 기준 권장 TPM/RPM과 capacity 산정 계획을 표시합니다. | 로컬 계산. 지역 가용성·quota 검증은 아직 하지 않습니다. |
| 2. `foundation ... --live` | 실제 카탈로그·quota를 확인하고 전용 RG에 프로젝트·모델을 배포합니다. | 실제 생성. 배포당 capacity 상한 100이며 비용 금액 상한이 아닙니다. 모델별 단위로 환산하고 실제 한도를 재조회합니다. |
| 3. `roles --live` | 현재 사용자와 프로젝트 관리 ID에 소유 프로젝트·부모 리소스의 필요한 데이터 역할을 부여합니다. | 실제 접근 권한 변경. `roleAssignments/write`가 필요하며 구독 전체 역할을 생성하지 않습니다. |

</div>

**포털 확인:** [Foundry](https://ai.azure.com)의 **New Foundry**에서 자신의 프로젝트를 열고 **Manage → Project details**의 Name·Parent resource·Location을 소유 기록과 대조합니다. **Build → Models → Deployments**에 `contoso-chat`, `contoso-judge`, `contoso-embedding`이 준비됐는지 확인합니다. 포털에서 같은 프로젝트나 모델을 다시 만들지 않습니다.

| 생성 코드 | 포털에서 확인할 결과 |
| --- | --- |
| `create`의 RG 생성 | Azure Resource groups의 고유 이름·소유 태그 |
| `foundation`의 Foundry account/project | Foundry 프로젝트 이름·부모 리소스·지역 |
| Bicep의 모델 deployments | Model ID·version과 배포 이름 `contoso-chat` 등 |
| `roles`의 scope별 role assignment | 대상 자원의 IAM에서 사용자/관리 ID와 범위 |

부분 실패는 원본 오류와 deployment operation을 보존합니다. 같은 소유 자원의 부분 배포를 재개할 때만 `foundation --resume --live`를 **동일 모델·SKU 인수와 함께** 사용합니다. 새 환경으로 바꾸거나 기록을 덮어쓰는 옵션이 아닙니다.

### 5. 로그 연결과 로컬 설정 완성하기

L04 이후 실행을 L10에서 다시 보기 위해 **첫 agent 호출 전에** 로그를 연결합니다.

```bash
python scripts/azure_environment.py monitoring
python scripts/azure_environment.py monitoring --live
```

<div class="command-explanation" markdown="1">

**명령 해설**

| 순서·명령 | 하는 일 | 결과·비용/변경 |
| --- | --- | --- |
| 1. `monitoring` | 로그 자원·프로젝트 연결 계획을 표시합니다. | Azure 요청 없음. |
| 2. `monitoring --live` | 소유 RG에 Log Analytics·Application Insights와 프로젝트 연결을 만듭니다. | 로그 수집·보관 비용 가능. 기록된 기존 연결을 덮어쓰지 않습니다. |

</div>

**Agents → Traces** 또는 **Manage → Project details → Connected resources**에서 연결을 확인합니다. 로그 조회에는 대상 Application Insights/Log Analytics의 읽기 권한이 필요합니다. 필요할 경우 자신의 자원 IAM에서 `Log Analytics Reader` 등 필요한 최소 역할을 설정합니다. 보호된 테이블에는 추가 권한이 필요할 수 있습니다.

모델·에이전트 SDK 호출은 Entra 인증을 사용합니다. 동봉 로그 연결은 [observability.bicep](../infra/observability.bicep)이 Azure 내부의 연결 문자열을 참조하며 화면·출력에 비밀을 노출하지 않습니다. Entra 기반 로그 수집을 설정했다고 주장하지 않습니다.

![프로젝트 설정 예시. Manage → Project details에서 프로젝트·상위 리소스·리전과 Connected resources를 확인한다.](../assets/portal/13-project-settings.png)

VS Code에서 `.env`를 열고 자신의 값으로 저장합니다. 아래는 **파일 설정**이며 터미널 명령이 아닙니다.

```env
FOUNDRY_PROJECT_ENDPOINT=https://실제-리소스.services.ai.azure.com/api/projects/실제-프로젝트
FOUNDRY_MODEL_DEPLOYMENT_NAME=contoso-chat
FOUNDRY_JUDGE_DEPLOYMENT_NAME=contoso-judge
FOUNDRY_EMBEDDING_DEPLOYMENT_NAME=contoso-embedding
```

`FOUNDRY_PROJECT_ENDPOINT`는 소유 기록의 `project_endpoint` 또는 포털 Home의 **Project endpoint**에서 가져옵니다. `/openai/v1`을 덧붙이지 않습니다. 실제 배포 이름은 소유 기록의 `model_deployments`와 대조합니다. `.env`와 가상환경 `.venv`는 다른 파일/폴더이며, API key를 넣지 않습니다.

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

## 성공 기준

내 전용 RG·프로젝트·세 모델·로그 연결을 만들고, 역할·지역·예산을 확인했습니다. 로컬 데이터 검사가 통과하며 포털·`.env`·`results/azure-environment.json`이 같은 환경을 가리킵니다. 계획 출력이나 client 생성만으로 모델 호출 성공이라고 기록하지 않습니다. [L02](#l02)에서 내가 만든 배포를 확인합니다.

## 막혔을 때

401은 CLI 인증, 403은 작업별 권한과 네트워크, 배포 실패는 모델·지역·quota·capacity부터 확인합니다. Private endpoint 환경은 승인된 VPN/VNet 경로에서 접근하며 public access를 임의로 켜지 않습니다. 설치 실패는 현재 Python과 허용된 패키지 저장소를 확인합니다.

## 정리

아직 자원을 삭제하지 않습니다. 소유 기록과 보존 기한을 유지하고 L19에서 반복 실행·남은 비용을 확인합니다. 이 장은 환경 생성이며 답변 품질 검증이 아닙니다.
