# Paper Reading Agent - 安装指南

本文档提供 Paper Reading Agent 工具的详细安装和配置说明。

## 目录

- [系统要求](#系统要求)
- [安装步骤](#安装步骤)
- [配置说明](#配置说明)
- [验证安装](#验证安装)
- [常见问题](#常见问题)

---

## 系统要求

### 操作系统
- Linux (推荐)
- macOS
- Windows (需要 WSL 或 Git Bash)

### Python 环境
- **Python 3.9 或更高版本**
- pip (Python 包管理器)

### 硬件要求
- **内存**: 建议 4GB 以上
- **磁盘空间**: 至少 500MB 可用空间
- **网络**: 需要访问 LLM API（OpenAI、DeepSeek、Anthropic 等）

---

## 安装步骤

### 方法一：从 GitHub 安装（推荐）

#### 1. 克隆仓库

```bash
# 使用 HTTPS
git clone https://github.com/xuqiaobo001/paper_agent.git

# 或使用 SSH
git clone git@github.com:xuqiaobo001/paper_agent.git

# 进入项目目录
cd paper_agent
```

#### 2. 安装依赖

```bash
# 使用 pip 安装（开发模式）
pip install -e .

# 或直接安装依赖
pip install -r requirements.txt
```

**注意**：如果遇到权限问题，可以添加 `--user` 参数：

```bash
pip install -e . --user
```

或在某些 Linux 发行版上：

```bash
pip install -e . --break-system-packages
```

#### 3. 验证安装

```bash
# 检查命令行工具是否可用
paper-agent --help
```

如果看到帮助信息，说明安装成功！

---

### 方法二：直接下载源码

#### 1. 下载项目

访问 [GitHub Releases](https://github.com/xuqiaobo001/paper_agent/releases) 下载最新版本的源码压缩包。

或使用 `wget`/`curl` 下载：

```bash
# 下载并解压
wget https://github.com/xuqiaobo001/paper_agent/archive/refs/heads/main.zip
unzip main.zip
cd paper_agent-main
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
pip install -e .
```

---

## 配置说明

### 1. 生成配置文件

```bash
# 生成默认配置文件
paper-agent init -o config.yaml
```

这将在当前目录创建 `config.yaml` 配置文件。

### 2. 配置 LLM API

编辑 `config.yaml`，设置您的 LLM 提供商和 API 密钥。

#### 选项 A：OpenAI

```yaml
llm:
  provider: "openai"
  model: "gpt-4o"
  api_key: "${OPENAI_API_KEY}"  # 使用环境变量（推荐）
  # 或直接填写
  # api_key: "sk-xxxxxxxxxxxxx"
```

**设置环境变量**（推荐）：

```bash
# Linux/macOS
export OPENAI_API_KEY="sk-xxxxxxxxxxxxx"

# 永久保存（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export OPENAI_API_KEY="sk-xxxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

#### 选项 B：DeepSeek

```yaml
llm:
  provider: "deepseek"
  model: "deepseek-chat"
  api_key: "${DEEPSEEK_API_KEY}"
```

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
```

#### 选项 C：Anthropic (Claude)

```yaml
llm:
  provider: "anthropic"
  model: "claude-sonnet-4-20250514"
  api_key: "${ANTHROPIC_API_KEY}"
```

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

#### 选项 D：华为云 ModelArts MAAS

```yaml
llm:
  provider: "openai"  # 使用 OpenAI 兼容接口
  model: "DeepSeek-V3"  # 或其他可用模型
  api_key: "${LLM_API_KEY}"
  api_base: "https://api.modelarts-maas.com/v1"
```

```bash
export LLM_API_KEY="your-huawei-api-key"
```

#### 选项 E：Ollama（本地部署，免费）

```yaml
llm:
  provider: "ollama"
  model: "llama3.1"  # 或 qwen2.5, deepseek-r1 等
  api_base: "http://localhost:11434/v1"
  # Ollama 不需要 API key
```

**安装 Ollama**：

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama3.1

# 启动服务
ollama serve
```

### 3. 配置其他选项

#### PDF 解析器配置

```yaml
pdf_parser:
  engine: "pymupdf"           # 推荐，或使用 "pdfplumber"
  extract_images: true        # 是否提取图片
  extract_tables: true        # 是否提取表格
  max_pages: 0                # 0 表示不限制页数
```

#### 并行处理配置

```yaml
parallel:
  enabled: true               # 启用并行处理
  max_workers: 4              # 最大并行工作线程数
```

#### 报告生成配置

```yaml
report_generator:
  output_format: "markdown"   # markdown, json, html
  language: "english"         # english 或 chinese
  summary_level: "detailed"   # brief, detailed, comprehensive
```

---

## 验证安装

### 1. 检查命令行工具

```bash
paper-agent --help
```

应该看到类似以下输出：

```
Usage: paper-agent [OPTIONS] COMMAND [ARGS]...

Commands:
  analyze  Analyze papers and generate reports
  init     Initialize configuration file
```

### 2. 测试基本功能

#### 生成配置文件测试

```bash
paper-agent init -o test_config.yaml
ls test_config.yaml  # 检查文件是否生成
```

#### 分析单篇论文测试

```bash
# 准备一个 PDF 文件
paper-agent analyze sample.pdf -t single -o test_output.md
```

如果成功生成 `test_output.md`，说明工具运行正常！

### 3. 检查依赖包

```bash
# 检查关键依赖
python -c "import fitz; print('PyMuPDF:', fitz.__version__)"
python -c "import pdfplumber; print('pdfplumber installed')"
python -c "import yaml; print('PyYAML installed')"
python -c "import openai; print('openai installed')"
```

---

## 常见问题

### Q1: `ModuleNotFoundError: No module named 'paper_agent'`

**原因**: 包未正确安装

**解决方案**:

```bash
cd paper_agent
pip install -e .
```

如果仍然失败，尝试：

```bash
pip install -e . --break-system-packages  # Linux 系统包管理冲突
pip install -e . --user                   # 安装到用户目录
```

---

### Q2: `paper-agent: command not found`

**原因**: 命令未添加到 PATH

**解决方案**:

1. 检查安装位置：

```bash
pip show paper-agent | grep Location
```

2. 添加到 PATH（临时）：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

3. 永久添加（添加到 ~/.bashrc）：

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### Q3: API 认证失败 (401/403 错误)

**原因**: API 密钥配置错误或无效

**解决方案**:

1. 检查环境变量是否设置：

```bash
echo $OPENAI_API_KEY
# 或
echo $DEEPSEEK_API_KEY
```

2. 验证 API 密钥有效性（以 OpenAI 为例）：

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

3. 检查配置文件中的 API 密钥是否正确：

```bash
grep "api_key" config.yaml
```

---

### Q4: `max_tokens` 参数错误

**错误信息**: `max_tokens parameter is invalid (655536 > 32768)`

**解决方案**:

编辑 `config.yaml`，修改 `max_tokens` 值：

```yaml
llm:
  max_tokens: 32768  # 或更小的值，如 4096
```

---

### Q5: PDF 解析失败或乱码

**原因**: PDF 是扫描版或加密文档

**解决方案**:

1. 检查 PDF 是否可提取文本：

```bash
python -c "import fitz; doc=fitz.open('paper.pdf'); print(doc[0].get_text()[:200])"
```

2. 如果是扫描版 PDF，需要 OCR 工具（工具当前不支持）

3. 尝试更换 PDF 解析引擎：

```yaml
pdf_parser:
  engine: "pdfplumber"  # 从 pymupdf 换成 pdfplumber
```

---

### Q6: 表格提取不完整

**现象**: 报告中表格只有标题，没有内容

**解决方案**:

1. 检查图片提取是否启用：

```yaml
pdf_parser:
  extract_images: true   # 确保为 true
  extract_tables: true
```

2. 工具会自动截图复杂表格，确保有写入权限

---

### Q7: 内存不足错误

**错误信息**: `MemoryError` 或系统卡死

**解决方案**:

1. 减少并行工作线程：

```yaml
parallel:
  enabled: true
  max_workers: 2  # 从 4 降到 2
```

2. 限制 PDF 页数：

```yaml
pdf_parser:
  max_pages: 50  # 只处理前 50 页
```

3. 关闭并行处理：

```yaml
parallel:
  enabled: false
```

---

### Q8: 网络连接超时

**错误信息**: `Timeout` 或 `Connection Error`

**解决方案**:

1. 增加超时时间：

```yaml
llm:
  timeout: 300  # 从 120 秒增加到 300 秒
```

2. 检查网络连接：

```bash
# 测试 API 连通性
curl -I https://api.openai.com
```

3. 配置代理（如需要）：

```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
```

---

### Q9: 不同模型被混淆（如 QwenVL 和 Qwen LLM）

**现象**: 多模态模型和 LLM 被归为一类

**解决方案**:

这个问题已在最新版本修复。请更新到最新版本：

```bash
cd paper_agent
git pull origin main
pip install -e . --upgrade
```

现在工具会正确识别模型类型（LLM、Multimodal、Vision 等）并在报告中明确显示。

---

## 获取帮助

如果遇到其他问题：

1. **查看详细文档**: [README.md](README.md)
2. **提交 Issue**: [GitHub Issues](https://github.com/xuqiaobo001/paper_agent/issues)
3. **查看示例**: `example/` 目录中有示例输出

---

## 卸载

如果需要卸载工具：

```bash
# 卸载 paper_agent
pip uninstall paper-agent

# 删除配置文件（可选）
rm -f config.yaml

# 删除源码目录（可选）
cd ..
rm -rf paper_agent
```

---

## 更新

保持工具更新以获得最新功能和 bug 修复：

```bash
cd paper_agent
git pull origin main
pip install -e . --upgrade
```

---

## 下一步

安装完成后，请参考：

- [README.md](README.md) - 功能介绍和使用示例
- [example/](example/) - 查看示例输出
- 运行 `paper-agent analyze --help` 查看命令参数

祝使用愉快！
