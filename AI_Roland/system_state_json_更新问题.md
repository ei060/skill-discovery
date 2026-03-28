# system_state.json 更新问题记录

## 问题描述

守护进程每秒更新 `system_state.json`（心跳计数），导致手动修改的内容被覆盖。

## 具体表现

1. 编辑 `system_state.json`
2. 守护进程在下一秒更新心跳计数
3. 整个文件被旧内容覆盖

## 受影响的功能

- `skill_discovery_pending` 更新
- `skill_discovery_integrated` 添加
- 其他需要持久化的状态更新

## 解决方案选项

### 选项 1: 停止守护进程，修改文件，重启
```bash
# 找到守护进程 PID
ps aux | grep python

# 停止守护进程
kill <PID>

# 修改文件
# 编辑 system_state.json

# 重启守护进程
python system/daemon.py &
```

### 选项 2: 使用脚本原子性更新
```python
import json
from pathlib import Path

def update_system_state(updates):
    """原子性更新 system_state.json"""
    file_path = Path('system_state.json')
    
    # 读取当前状态
    with open(file_path, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    # 应用更新
    state.update(updates)
    
    # 原子性写入
    temp_file = file_path.with_suffix('.json.tmp')
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    # 原子性重命名
    temp_file.replace(file_path)
```

### 选项 3: 修改守护进程，使用信号处理
守护进程监听 SIGUSR1 信号，收到信号时重新加载配置。

### 选项 4: 分离心跳文件和状态文件
- `heartbeat.json`: 只包含心跳计数
- `system_state.json`: 其他系统状态

## 推荐方案

**选项 4** - 分离文件：
1. 守护进程只更新 `heartbeat.json`
2. `system_state.json` 仅在手动修改时更新
3. 避免冲突

## 当前状态

- ✅ 技能集成报告已创建
- ✅ skills_registry.json 已包含所有技能
- ⚠️ system_state.json 更新被守护进程覆盖

## 下一步

实施选项 4，分离心跳文件和状态文件。

---
创建时间: 2026-03-28
优先级: 中
