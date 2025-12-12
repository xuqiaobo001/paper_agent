# 安装脚本使用说明

本目录包含 Paper Reading Agent 的自动化安装脚本，支持 Linux、macOS 和 Windows 平台。

## 脚本列表

| 脚本文件 | 平台 | 说明 |
|---------|------|------|
| `install.sh` | Linux / macOS | Bash shell 脚本（推荐） |
| `install.ps1` | Windows | PowerShell 脚本（推荐） |
| `install.bat` | Windows | 批处理脚本（备选） |

---

## Linux / macOS 安装

### 使用方法

```bash
# 1. 下载脚本
wget https://raw.githubusercontent.com/xuqiaobo001/paper_agent/main/install.sh
# 或使用 curl
curl -O https://raw.githubusercontent.com/xuqiaobo001/paper_agent/main/install.sh

# 2. 添加执行权限
chmod +x install.sh

# 3. 运行脚本
./install.sh
```

### 脚本功能

- ✅ 自动检查 Python 3.9+ 版本
- ✅ 自动检查并安装 pip
- ✅ 克隆 GitHub 仓库或使用当前目录代码
- ✅ 自动安装所有依赖包
- ✅ 生成默认配置文件
- ✅ 交互式配置 LLM API Key
- ✅ 自动添加环境变量到 ~/.bashrc
- ✅ 验证安装是否成功

### 支持的 Shell

- Bash（推荐）
- Zsh
- 其他 POSIX 兼容的 shell

---

## Windows 安装

### 方法 1：PowerShell 脚本（推荐）

#### 使用方法

1. **下载脚本**
   - 访问 [GitHub Releases](https://github.com/xuqiaobo001/paper_agent/releases)
   - 或直接下载：https://raw.githubusercontent.com/xuqiaobo001/paper_agent/main/install.ps1

2. **允许脚本执行**（首次运行需要）
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **运行脚本**
   - 右键点击 `install.ps1` → "使用 PowerShell 运行"
   - 或在 PowerShell 中执行：
     ```powershell
     .\install.ps1
     ```

#### 脚本功能

- ✅ 自动检查 Python 3.9+ 版本
- ✅ 自动检查并安装 pip
- ✅ 克隆 GitHub 仓库或使用当前目录代码
- ✅ 自动安装所有依赖包
- ✅ 生成默认配置文件
- ✅ 交互式配置 LLM API Key
- ✅ 自动添加环境变量到系统
- ✅ 自动添加 Python Scripts 到 PATH
- ✅ 验证安装是否成功

---

### 方法 2：批处理脚本（备选）

#### 使用方法

1. **下载脚本**
   - 下载 `install.bat` 文件

2. **运行脚本**
   - 双击 `install.bat`
   - 或在命令提示符中执行：
     ```cmd
     install.bat
     ```

#### 限制

- 功能相对简单，错误处理较少
- 建议优先使用 PowerShell 脚本

---

## 脚本执行流程

所有脚本都遵循以下标准流程：

```
1. 环境检查
   ├── 检查 Python 版本 (>= 3.9)
   ├── 检查 pip
   └── 检查 git (可选)

2. 代码准备
   ├── 检测当前目录
   ├── 克隆 GitHub 仓库
   └── 或使用现有代码

3. 安装依赖
   ├── pip install -e .
   └── 处理安装错误

4. 生成配置
   └── paper-agent init -o config.yaml

5. 环境配置 (可选)
   ├── 选择 LLM 提供商
   ├── 输入 API Key
   └── 设置环境变量

6. 验证安装
   ├── 检查 paper-agent 命令
   └── 测试 Python 包导入

7. 完成
   └── 显示后续步骤
```

---

## 常见问题

### Q1: 脚本执行权限不足

**Linux/macOS**:
```bash
chmod +x install.sh
```

**Windows PowerShell**:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Q2: Git 未安装怎么办？

脚本会检测 git 是否可用：

- **如果当前目录已是 `paper_agent`**：直接安装，不需要 git
- **如果需要克隆仓库**：脚本会提示安装 git

**手动下载代码**：
```bash
# 下载 ZIP 并解压
wget https://github.com/xuqiaobo001/paper_agent/archive/refs/heads/main.zip
unzip main.zip
cd paper_agent-main
# 然后运行安装脚本
```

---

### Q3: Python 版本不符合要求

需要 **Python 3.9 或更高版本**。

**安装最新 Python**：
- Linux: `sudo apt install python3.9` 或 `sudo yum install python39`
- macOS: `brew install python@3.9`
- Windows: https://www.python.org/downloads/

---

### Q4: pip install 失败

脚本会尝试多种安装方式：

1. 标准安装: `pip install -e .`
2. 用户模式: `pip install -e . --user`
3. 系统包模式 (Linux): `pip install -e . --break-system-packages`

如果都失败：
```bash
# 手动安装依赖
pip install -r requirements.txt
```

---

### Q5: paper-agent 命令未找到

**原因**：环境变量未生效

**Linux/macOS**:
```bash
source ~/.bashrc
# 或
source ~/.zshrc
```

**Windows**:
- 重新打开命令提示符或 PowerShell 窗口

---

### Q6: 环境变量配置失败

**手动设置环境变量**：

**Linux/macOS**:
```bash
export OPENAI_API_KEY="sk-xxxxxxxx"
echo 'export OPENAI_API_KEY="sk-xxxxxxxx"' >> ~/.bashrc
```

**Windows PowerShell**:
```powershell
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-xxxxxxxx", "User")
```

**Windows 命令提示符**:
```cmd
setx OPENAI_API_KEY "sk-xxxxxxxx"
```

---

## 脚本安全性

### 审查代码

在运行任何脚本前，建议先查看代码内容：

```bash
# Linux/macOS
cat install.sh

# Windows PowerShell
Get-Content install.ps1
```

### 脚本来源

- **官方仓库**: https://github.com/xuqiaobo001/paper_agent
- **仅从可信来源下载脚本**

---

## 手动安装

如果不想使用自动化脚本，可以手动安装：

```bash
# 1. 克隆仓库
git clone https://github.com/xuqiaobo001/paper_agent.git
cd paper_agent

# 2. 安装依赖
pip install -e .

# 3. 生成配置
paper-agent init -o config.yaml

# 4. 编辑配置文件
vim config.yaml

# 5. 设置环境变量
export OPENAI_API_KEY="your-api-key"
```

---

## 卸载

如果需要卸载工具：

```bash
# 卸载 Python 包
pip uninstall paper-agent

# 删除代码目录
rm -rf paper_agent

# 删除环境变量 (Linux/macOS)
# 编辑 ~/.bashrc 删除相关的 export 行

# 删除环境变量 (Windows)
# 在系统设置 → 环境变量中手动删除
```

---

## 获取帮助

如果遇到问题：

1. **查看详细文档**: [INSTALL.md](INSTALL.md)
2. **提交 Issue**: [GitHub Issues](https://github.com/xuqiaobo001/paper_agent/issues)
3. **查看常见问题**: 上方 FAQ 部分

---

## 贡献

欢迎改进安装脚本！如果您发现 bug 或有改进建议，请：

1. Fork 仓库
2. 创建分支
3. 提交 Pull Request

---

**祝安装顺利！**
