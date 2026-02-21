# Claude 工作区配置

## 自动启动

每次打开 Claude 时，会自动执行 `startup.py`，启动 AI Roland 系统。

## 功能

- ✅ 自动检查并启动守护进程
- ✅ 显示最近对话历史
- ✅ 显示当前待办任务
- ✅ 自动记录新会话

## 文件说明

- `startup.py` - 自动启动脚本
- `settings.json` - 配置文件
- `README.md` - 本说明文件

## 手动控制

如需手动重启系统：

```bash
python AI_Roland/system/session_start.py
```

查看守护进程状态：

```bash
python AI_Roland/system/monitor.py
```

停止守护进程：

```bash
# Windows
taskkill /F /PID <PID>

# 或等待系统自动停止（会话结束时）
```
