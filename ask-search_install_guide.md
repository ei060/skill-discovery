# ask-search 安装指南 (Windows)

**状态**: ⚠️ Docker 不可用，需要手动安装

---

## 方案 A: Docker 安装 (推荐)

### 1. 安装 Docker Desktop for Windows

下载: https://www.docker.com/products/docker-desktop/

安装后运行:
```bash
cd D:\ClaudeWork\.claude\skills\ask-search\searxng
docker-compose up -d
```

### 2. 验证 SearxNG

访问: http://localhost:8080

### 3. 安装 ask-search 命令

```bash
cd D:\ClaudeWork\.claude\skills\ask-search
install.bat
```

---

## 方案 B: 使用公共 SearxNG 实例

如果 Docker 不可用，可以使用公共 SearxNG 实例：

| 实例 | URL |
|------|-----|
| Searx.me | https://searx.me |
| Searx.work | https://searx.work |
| Fireball | https://fireball.org |

### 配置 ask-search 使用公共实例

设置环境变量:
```bash
set SEARXNG_URL=https://searx.me
```

或直接测试:
```bash
python D:\ClaudeWork\.claude\skills\ask-search\scripts\core.py "test query"
```

---

## 方案 C: 本地 Python 运行 (临时测试)

当前可以直接测试核心功能:

```bash
cd D:\ClaudeWork\.claude\skills\ask-search

# 直接使用 Python 调用
python -c "import sys; sys.path.insert(0, 'scripts'); from core import search; print(search('Claude AI', 3))"
```

---

## 文件位置

| 文件 | 路径 |
|------|------|
| 仓库 | `D:\ClaudeWork\.claude\skills\ask-search` |
| 核心脚本 | `scripts/core.py` |
| 安装脚本 | `install.bat` |
| 配置 | `searxng/.env` |
| Docker Compose | `searxng/docker-compose.yml` |

---

## 下一步

1. **安装 Docker Desktop** (推荐)
2. 运行 `install.bat`
3. 测试: `ask-search "test query"`

---

**当前状态**:
- ✅ 仓库已克隆
- ✅ 依赖已检查 (Python 3.14.2, curl 8.17)
- ✅ 配置文件已创建
- ⚠️ 等待 Docker 启动 SearxNG
