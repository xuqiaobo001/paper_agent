@echo off
REM ###############################################################################
REM Paper Reading Agent - Windows 批处理安装脚本
REM
REM 使用方法：双击运行或在命令提示符中执行
REM
REM 注意：推荐使用 PowerShell 脚本 (install.ps1) 以获得更好的体验
REM ###############################################################################

setlocal enabledelayedexpansion

echo ╔═══════════════════════════════════════════════════════════╗
echo ║      Paper Reading Agent - Windows 批处理安装脚本         ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM 检查 Python
echo [INFO] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.9 或更高版本
    echo [INFO] 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] 发现 Python 版本: %PYTHON_VERSION%

REM 检查 pip
echo.
echo [INFO] 检查 pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 未找到 pip，正在尝试安装...
    python -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        echo [ERROR] pip 安装失败
        pause
        exit /b 1
    )
)
echo [SUCCESS] pip 检查通过

REM 检查 Git
echo.
echo [INFO] 检查 Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] 未找到 git
    echo [INFO] 如果当前目录不是 paper_agent，请先安装 git 或手动下载代码
    echo [INFO] 下载 Git: https://git-scm.com/download/win
    set HAS_GIT=0
) else (
    set HAS_GIT=1
    echo [SUCCESS] Git 检查通过
)

REM 检查或克隆仓库
echo.
echo [INFO] 设置代码仓库...
if exist "setup.py" (
    if exist "core" (
        echo [INFO] 当前目录已包含 paper_agent 代码
        set REPO_DIR=.
        goto install_deps
    )
)

if %HAS_GIT%==0 (
    echo [ERROR] 当前目录不是 paper_agent，且没有 git 无法克隆仓库
    echo [ERROR] 请手动下载代码或安装 git
    pause
    exit /b 1
)

set REPO_DIR=paper_agent
if exist "%REPO_DIR%" (
    echo [INFO] 目录 %REPO_DIR% 已存在，正在更新...
    cd %REPO_DIR%
    git pull origin main
    cd ..
) else (
    echo [INFO] 正在克隆仓库...
    git clone https://github.com/xuqiaobo001/paper_agent.git
    if %errorlevel% neq 0 (
        echo [ERROR] 克隆仓库失败
        pause
        exit /b 1
    )
)
echo [SUCCESS] 代码仓库准备完成

:install_deps
REM 安装依赖
echo.
echo [INFO] 安装依赖包...
cd %REPO_DIR%
pip install -e .
if %errorlevel% neq 0 (
    echo [WARNING] 标准安装失败，尝试用户模式...
    pip install -e . --user
    if %errorlevel% neq 0 (
        echo [ERROR] 依赖安装失败
        cd ..
        pause
        exit /b 1
    )
    echo [SUCCESS] 依赖安装成功（用户模式）
    echo [WARNING] 可能需要将 Python Scripts 目录添加到 PATH
) else (
    echo [SUCCESS] 依赖安装成功
)

REM 生成配置文件
echo.
echo [INFO] 生成配置文件...
if exist "config.yaml" (
    echo [WARNING] config.yaml 已存在，跳过生成
) else (
    paper-agent init -o config.yaml 2>nul
    if %errorlevel% neq 0 (
        echo [WARNING] paper-agent 命令未找到，跳过配置文件生成
        echo [INFO] 稍后可以手动运行: paper-agent init -o config.yaml
    ) else (
        echo [SUCCESS] 配置文件生成完成
    )
)

REM 配置环境变量
echo.
set /p CONFIGURE_ENV="是否现在配置 LLM API Key？[y/N]: "
if /i "%CONFIGURE_ENV%"=="y" (
    echo.
    echo 请选择您的 LLM 提供商：
    echo   1^) OpenAI
    echo   2^) DeepSeek
    echo   3^) Anthropic ^(Claude^)
    echo   4^) 华为云 ModelArts
    echo   5^) Ollama ^(本地^)
    echo   6^) 跳过
    echo.
    set /p PROVIDER_CHOICE="请输入选项 [1-6]: "

    if "!PROVIDER_CHOICE!"=="1" (
        set /p API_KEY="请输入 OpenAI API Key: "
        setx OPENAI_API_KEY "!API_KEY!" >nul
        echo [SUCCESS] OpenAI API Key 已设置
    ) else if "!PROVIDER_CHOICE!"=="2" (
        set /p API_KEY="请输入 DeepSeek API Key: "
        setx DEEPSEEK_API_KEY "!API_KEY!" >nul
        echo [SUCCESS] DeepSeek API Key 已设置
    ) else if "!PROVIDER_CHOICE!"=="3" (
        set /p API_KEY="请输入 Anthropic API Key: "
        setx ANTHROPIC_API_KEY "!API_KEY!" >nul
        echo [SUCCESS] Anthropic API Key 已设置
    ) else if "!PROVIDER_CHOICE!"=="4" (
        set /p API_KEY="请输入华为云 API Key: "
        setx LLM_API_KEY "!API_KEY!" >nul
        echo [SUCCESS] 华为云 API Key 已设置
    ) else if "!PROVIDER_CHOICE!"=="5" (
        echo [INFO] 请确保 Ollama 已安装并运行
        echo [INFO] 下载 Ollama: https://ollama.com/download/windows
    ) else (
        echo [INFO] 跳过环境变量配置
    )

    echo [INFO] 环境变量已添加到系统环境变量
    echo [WARNING] 需要重新打开命令提示符窗口使其生效
) else (
    echo [INFO] 跳过 API Key 配置，稍后可以手动配置
)

REM 验证安装
echo.
echo [INFO] 验证安装...
paper-agent --help >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] paper-agent 命令未找到
    echo [INFO] 可能需要重新打开命令提示符窗口
) else (
    echo [SUCCESS] paper-agent 命令可用
    echo [INFO] 运行 'paper-agent --help' 查看帮助信息
)

REM 打印后续步骤
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                     安装完成！                            ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo [INFO] 后续步骤：
echo   1. 重新打开命令提示符窗口以刷新环境变量
echo.
echo   2. 编辑配置文件（如果需要）:
echo      notepad config.yaml
echo.
echo   3. 运行测试命令:
echo      paper-agent --help
echo.
echo   4. 分析论文:
echo      paper-agent analyze paper.pdf -t single -o output.md
echo.
echo [INFO] 详细文档请查看:
echo   - 安装指南: INSTALL.md
echo   - 使用说明: README.md
echo.
echo [SUCCESS] 祝使用愉快！
echo.

cd ..
pause
