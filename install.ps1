###############################################################################
# Paper Reading Agent - Windows PowerShell 自动安装脚本
#
# 使用方法：
#   在 PowerShell 中运行（以管理员身份）：
#   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
#   .\install.ps1
#
# 或者右键选择 "使用 PowerShell 运行"
###############################################################################

# 设置错误时停止
$ErrorActionPreference = "Stop"

# 颜色函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Print-Info {
    param([string]$Message)
    Write-ColorOutput Cyan "[INFO] $Message"
}

function Print-Success {
    param([string]$Message)
    Write-ColorOutput Green "[SUCCESS] $Message"
}

function Print-Warning {
    param([string]$Message)
    Write-ColorOutput Yellow "[WARNING] $Message"
}

function Print-Error {
    param([string]$Message)
    Write-ColorOutput Red "[ERROR] $Message"
}

function Print-Step {
    param([string]$Message)
    Write-Host ""
    Write-ColorOutput Green "==> $Message"
}

# 检查管理员权限
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($user)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查 Python
function Check-Python {
    Print-Step "检查 Python 环境..."

    $pythonCmd = $null

    if (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    } else {
        Print-Error "未找到 Python，请先安装 Python 3.9 或更高版本"
        Print-Info "下载地址: https://www.python.org/downloads/"
        exit 1
    }

    $versionOutput = & $pythonCmd --version 2>&1
    $version = $versionOutput -replace 'Python ', ''
    Print-Info "发现 Python 版本: $version"

    $versionParts = $version.Split('.')
    $major = [int]$versionParts[0]
    $minor = [int]$versionParts[1]

    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
        Print-Error "需要 Python 3.9 或更高版本，当前版本: $version"
        exit 1
    }

    Print-Success "Python 版本检查通过"
    return $pythonCmd
}

# 检查 pip
function Check-Pip {
    param([string]$PythonCmd)

    Print-Step "检查 pip..."

    $pipCmd = $null

    if (Get-Command pip -ErrorAction SilentlyContinue) {
        $pipCmd = "pip"
    } elseif (Get-Command pip3 -ErrorAction SilentlyContinue) {
        $pipCmd = "pip3"
    } else {
        Print-Warning "未找到 pip，正在尝试安装..."
        & $PythonCmd -m ensurepip --default-pip
        $pipCmd = "pip"
    }

    Print-Success "pip 检查通过"
    return $pipCmd
}

# 检查 Git
function Check-Git {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        return $true
    }
    Print-Warning "未找到 git，将跳过从 GitHub 克隆的步骤"
    Print-Info "下载 Git: https://git-scm.com/download/win"
    return $false
}

# 设置仓库
function Setup-Repository {
    Print-Step "设置代码仓库..."

    # 检查当前目录是否已经是 paper_agent
    if ((Test-Path "setup.py") -and (Test-Path "core")) {
        Print-Info "当前目录已包含 paper_agent 代码"
        return "."
    }

    # 检查是否有 git
    if (-not (Check-Git)) {
        Print-Error "当前目录不是 paper_agent，且没有 git 无法克隆仓库"
        Print-Error "请手动下载代码或安装 git"
        exit 1
    }

    $repoDir = "paper_agent"
    $repoUrl = "https://github.com/xuqiaobo001/paper_agent.git"

    if (Test-Path $repoDir) {
        Print-Info "目录 $repoDir 已存在，正在更新..."
        Push-Location $repoDir
        try {
            git pull origin main
        } catch {
            Print-Warning "更新失败，将使用现有代码继续"
        }
        Pop-Location
    } else {
        Print-Info "正在克隆仓库..."
        git clone $repoUrl
        if ($LASTEXITCODE -ne 0) {
            Print-Error "克隆仓库失败"
            exit 1
        }
    }

    Print-Success "代码仓库准备完成"
    return $repoDir
}

# 安装依赖
function Install-Dependencies {
    param([string]$RepoDir, [string]$PipCmd)

    Print-Step "安装依赖包..."

    Push-Location $RepoDir

    try {
        & $PipCmd install -e .
        Print-Success "依赖安装成功"
    } catch {
        try {
            & $PipCmd install -e . --user
            Print-Success "依赖安装成功（用户模式）"
            Print-Warning "可能需要将 Python Scripts 目录添加到 PATH"
        } catch {
            Print-Error "依赖安装失败，请检查错误信息"
            Pop-Location
            exit 1
        }
    }

    Pop-Location
}

# 生成配置文件
function Generate-Config {
    param([string]$RepoDir)

    Print-Step "生成配置文件..."

    Push-Location $RepoDir

    if (Test-Path "config.yaml") {
        Print-Warning "config.yaml 已存在，跳过生成"
        Pop-Location
        return
    }

    try {
        paper-agent init -o config.yaml
        Print-Success "配置文件生成完成"
    } catch {
        Print-Warning "paper-agent 命令未找到，跳过配置文件生成"
        Print-Info "稍后可以手动运行: paper-agent init -o config.yaml"
    }

    Pop-Location
}

# 配置环境变量
function Configure-Environment {
    Print-Step "配置环境变量..."

    Write-Host ""
    Print-Info "请选择您的 LLM 提供商："
    Write-Host "  1) OpenAI"
    Write-Host "  2) DeepSeek"
    Write-Host "  3) Anthropic (Claude)"
    Write-Host "  4) 华为云 ModelArts"
    Write-Host "  5) Ollama (本地)"
    Write-Host "  6) 跳过（稍后手动配置）"

    $choice = Read-Host "请输入选项 [1-6]"

    switch ($choice) {
        "1" {
            $apiKey = Read-Host "请输入 OpenAI API Key"
            [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $apiKey, "User")
            $env:OPENAI_API_KEY = $apiKey
            Print-Success "OpenAI API Key 已设置"
        }
        "2" {
            $apiKey = Read-Host "请输入 DeepSeek API Key"
            [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", $apiKey, "User")
            $env:DEEPSEEK_API_KEY = $apiKey
            Print-Success "DeepSeek API Key 已设置"
        }
        "3" {
            $apiKey = Read-Host "请输入 Anthropic API Key"
            [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", $apiKey, "User")
            $env:ANTHROPIC_API_KEY = $apiKey
            Print-Success "Anthropic API Key 已设置"
        }
        "4" {
            $apiKey = Read-Host "请输入华为云 API Key"
            [Environment]::SetEnvironmentVariable("LLM_API_KEY", $apiKey, "User")
            $env:LLM_API_KEY = $apiKey
            Print-Success "华为云 API Key 已设置"
        }
        "5" {
            Print-Info "请确保 Ollama 已安装并运行"
            Print-Info "下载 Ollama: https://ollama.com/download/windows"
        }
        "6" {
            Print-Info "跳过环境变量配置"
        }
        default {
            Print-Warning "无效选项，跳过环境变量配置"
        }
    }

    Print-Info "环境变量已添加到用户环境变量"
    Print-Warning "可能需要重新打开 PowerShell 窗口使其生效"
}

# 添加 Scripts 到 PATH
function Add-ScriptsToPath {
    $pythonScripts = "$env:APPDATA\Python\Python*\Scripts"
    $scriptsPath = Get-ChildItem $pythonScripts -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName

    if ($scriptsPath) {
        $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if ($currentPath -notlike "*$scriptsPath*") {
            [Environment]::SetEnvironmentVariable("Path", "$currentPath;$scriptsPath", "User")
            $env:Path += ";$scriptsPath"
            Print-Info "已将 Python Scripts 目录添加到 PATH"
        }
    }
}

# 验证安装
function Verify-Installation {
    Print-Step "验证安装..."

    # 刷新环境变量
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

    if (Get-Command paper-agent -ErrorAction SilentlyContinue) {
        Print-Success "paper-agent 命令可用"
        Print-Info "运行 'paper-agent --help' 查看帮助信息"
    } else {
        Print-Warning "paper-agent 命令未找到"
        Print-Info "可能需要重新打开 PowerShell 窗口"
    }

    # 检查 Python 包
    try {
        python -c "import paper_agent" 2>$null
        Print-Success "Python 包导入成功"
    } catch {
        Print-Warning "Python 包导入失败"
    }
}

# 打印后续步骤
function Print-NextSteps {
    Print-Step "安装完成！"
    Write-Host ""
    Print-Info "后续步骤："
    Write-Host "  1. 重新打开 PowerShell 窗口以刷新环境变量"
    Write-Host ""
    Write-Host "  2. 编辑配置文件（如果需要）:"
    Write-Host "     notepad config.yaml"
    Write-Host ""
    Write-Host "  3. 运行测试命令:"
    Write-Host "     paper-agent --help"
    Write-Host ""
    Write-Host "  4. 分析论文:"
    Write-Host "     paper-agent analyze paper.pdf -t single -o output.md"
    Write-Host ""
    Print-Info "详细文档请查看:"
    Write-Host "  - 安装指南: INSTALL.md"
    Write-Host "  - 使用说明: README.md"
    Write-Host ""
    Print-Success "祝使用愉快！"
}

# 主函数
function Main {
    Write-Host "╔═══════════════════════════════════════════════════════════╗"
    Write-Host "║      Paper Reading Agent - Windows 安装脚本              ║"
    Write-Host "╚═══════════════════════════════════════════════════════════╝"
    Write-Host ""

    # 检查管理员权限（可选）
    if (-not (Test-Administrator)) {
        Print-Warning "建议以管理员身份运行此脚本以获得最佳体验"
        $continue = Read-Host "是否继续？[y/N]"
        if ($continue -ne "y" -and $continue -ne "Y") {
            exit 0
        }
    }

    $pythonCmd = Check-Python
    $pipCmd = Check-Pip -PythonCmd $pythonCmd
    $repoDir = Setup-Repository
    Install-Dependencies -RepoDir $repoDir -PipCmd $pipCmd
    Generate-Config -RepoDir $repoDir
    Add-ScriptsToPath

    Write-Host ""
    $configure = Read-Host "是否现在配置 LLM API Key？[y/N]"
    if ($configure -eq "y" -or $configure -eq "Y") {
        Configure-Environment
    } else {
        Print-Info "跳过 API Key 配置，稍后可以手动配置"
    }

    Verify-Installation
    Print-NextSteps

    Write-Host ""
    Read-Host "按 Enter 键退出"
}

# 运行主函数
try {
    Main
} catch {
    Print-Error "安装过程中发生错误: $_"
    Read-Host "按 Enter 键退出"
    exit 1
}
