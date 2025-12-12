#!/bin/bash

###############################################################################
# Paper Reading Agent - Linux/macOS 自动安装脚本
#
# 使用方法：
#   chmod +x install.sh
#   ./install.sh
#
# 或直接运行：
#   bash install.sh
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${GREEN}==>${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查 Python 版本
check_python() {
    print_step "检查 Python 环境..."

    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        print_error "未找到 Python，请先安装 Python 3.9 或更高版本"
        exit 1
    fi

    # 获取 Python 版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    print_info "发现 Python 版本: $PYTHON_VERSION"

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
        print_error "需要 Python 3.9 或更高版本，当前版本: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python 版本检查通过"
}

# 检查 pip
check_pip() {
    print_step "检查 pip..."

    if command_exists pip3; then
        PIP_CMD="pip3"
    elif command_exists pip; then
        PIP_CMD="pip"
    else
        print_error "未找到 pip，正在尝试安装..."
        $PYTHON_CMD -m ensurepip --default-pip || {
            print_error "pip 安装失败，请手动安装 pip"
            exit 1
        }
        PIP_CMD="pip3"
    fi

    print_success "pip 检查通过"
}

# 检查 git
check_git() {
    if ! command_exists git; then
        print_warning "未找到 git，将跳过从 GitHub 克隆的步骤"
        return 1
    fi
    return 0
}

# 克隆或更新仓库
setup_repository() {
    print_step "设置代码仓库..."

    # 如果当前目录已经是 paper_agent，不需要克隆
    if [ -f "setup.py" ] && [ -d "core" ]; then
        print_info "当前目录已包含 paper_agent 代码"
        REPO_DIR="."
        return
    fi

    # 检查是否有 git
    if ! check_git; then
        print_error "当前目录不是 paper_agent，且没有 git 无法克隆仓库"
        print_error "请手动下载代码或安装 git"
        exit 1
    fi

    REPO_DIR="paper_agent"
    REPO_URL="https://github.com/xuqiaobo001/paper_agent.git"

    if [ -d "$REPO_DIR" ]; then
        print_info "目录 $REPO_DIR 已存在，正在更新..."
        cd "$REPO_DIR"
        git pull origin main || print_warning "更新失败，将使用现有代码继续"
        cd ..
    else
        print_info "正在克隆仓库..."
        git clone "$REPO_URL" || {
            print_error "克隆仓库失败"
            exit 1
        }
    fi

    print_success "代码仓库准备完成"
}

# 安装依赖
install_dependencies() {
    print_step "安装依赖包..."

    cd "$REPO_DIR"

    # 尝试不同的安装方式
    if $PIP_CMD install -e . 2>/dev/null; then
        print_success "依赖安装成功"
    elif $PIP_CMD install -e . --user 2>/dev/null; then
        print_success "依赖安装成功（用户模式）"
        print_warning "可能需要将 ~/.local/bin 添加到 PATH"
    elif $PIP_CMD install -e . --break-system-packages 2>/dev/null; then
        print_success "依赖安装成功（系统包模式）"
    else
        print_error "依赖安装失败，请检查错误信息"
        exit 1
    fi
}

# 生成配置文件
generate_config() {
    print_step "生成配置文件..."

    if [ -f "config.yaml" ]; then
        print_warning "config.yaml 已存在，跳过生成"
        return
    fi

    if command_exists paper-agent; then
        paper-agent init -o config.yaml
        print_success "配置文件生成完成"
    else
        print_warning "paper-agent 命令未找到，跳过配置文件生成"
        print_info "稍后可以手动运行: paper-agent init -o config.yaml"
    fi
}

# 配置环境变量
configure_env() {
    print_step "配置环境变量..."

    echo ""
    print_info "请选择您的 LLM 提供商："
    echo "  1) OpenAI"
    echo "  2) DeepSeek"
    echo "  3) Anthropic (Claude)"
    echo "  4) 华为云 ModelArts"
    echo "  5) Ollama (本地)"
    echo "  6) 跳过（稍后手动配置）"

    read -p "请输入选项 [1-6]: " choice

    case $choice in
        1)
            read -p "请输入 OpenAI API Key: " api_key
            echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.bashrc
            export OPENAI_API_KEY="$api_key"
            print_success "OpenAI API Key 已设置"
            ;;
        2)
            read -p "请输入 DeepSeek API Key: " api_key
            echo "export DEEPSEEK_API_KEY=\"$api_key\"" >> ~/.bashrc
            export DEEPSEEK_API_KEY="$api_key"
            print_success "DeepSeek API Key 已设置"
            ;;
        3)
            read -p "请输入 Anthropic API Key: " api_key
            echo "export ANTHROPIC_API_KEY=\"$api_key\"" >> ~/.bashrc
            export ANTHROPIC_API_KEY="$api_key"
            print_success "Anthropic API Key 已设置"
            ;;
        4)
            read -p "请输入华为云 API Key: " api_key
            echo "export LLM_API_KEY=\"$api_key\"" >> ~/.bashrc
            export LLM_API_KEY="$api_key"
            print_success "华为云 API Key 已设置"
            ;;
        5)
            print_info "请确保 Ollama 已安装并运行"
            print_info "安装 Ollama: curl -fsSL https://ollama.com/install.sh | sh"
            print_info "启动服务: ollama serve"
            ;;
        6)
            print_info "跳过环境变量配置"
            ;;
        *)
            print_warning "无效选项，跳过环境变量配置"
            ;;
    esac

    # 添加用户 bin 到 PATH（如果需要）
    if [ -d "$HOME/.local/bin" ]; then
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
            print_info "已将 ~/.local/bin 添加到 PATH"
        fi
    fi

    print_info "环境变量已添加到 ~/.bashrc"
    print_warning "请运行 'source ~/.bashrc' 或重新打开终端使其生效"
}

# 验证安装
verify_installation() {
    print_step "验证安装..."

    # 重新加载环境
    export PATH="$HOME/.local/bin:$PATH"

    if command_exists paper-agent; then
        VERSION=$(paper-agent --help | head -1 || echo "未知版本")
        print_success "paper-agent 命令可用"
        print_info "运行 'paper-agent --help' 查看帮助信息"
    else
        print_warning "paper-agent 命令未找到"
        print_info "可能需要重新打开终端或运行 'source ~/.bashrc'"
    fi

    # 检查 Python 包
    if $PYTHON_CMD -c "import paper_agent" 2>/dev/null; then
        print_success "Python 包导入成功"
    else
        print_warning "Python 包导入失败"
    fi
}

# 打印后续步骤
print_next_steps() {
    print_step "安装完成！"
    echo ""
    print_info "后续步骤："
    echo "  1. 重新加载环境变量:"
    echo "     source ~/.bashrc"
    echo ""
    echo "  2. 编辑配置文件（如果需要）:"
    echo "     vim config.yaml"
    echo ""
    echo "  3. 运行测试命令:"
    echo "     paper-agent --help"
    echo ""
    echo "  4. 分析论文:"
    echo "     paper-agent analyze paper.pdf -t single -o output.md"
    echo ""
    print_info "详细文档请查看:"
    echo "  - 安装指南: INSTALL.md"
    echo "  - 使用说明: README.md"
    echo ""
    print_success "祝使用愉快！"
}

# 主函数
main() {
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║     Paper Reading Agent - Linux/macOS 安装脚本           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    check_python
    check_pip
    setup_repository
    install_dependencies
    generate_config

    echo ""
    read -p "是否现在配置 LLM API Key？[y/N]: " configure
    if [[ $configure =~ ^[Yy]$ ]]; then
        configure_env
    else
        print_info "跳过 API Key 配置，稍后可以手动配置"
    fi

    verify_installation
    print_next_steps
}

# 运行主函数
main
