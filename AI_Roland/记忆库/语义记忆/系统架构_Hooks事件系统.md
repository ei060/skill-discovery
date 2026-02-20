# Hooks 事件系统

## 概念

Hooks 是一种事件驱动的扩展机制，允许在系统的特定生命周期点触发自定义动作。

## 核心架构

```
事件触发 → Hooks管理器 → 匹配的事件处理器 → 执行动作
```

## 支持的事件类型

### 1. 会话事件
- `session_start` - 会话开始时
- `session_end` - 会话结束时

### 2. 任务事件
- `task_created` - 任务创建时
- `task_completed` - 任务完成时
- `task_failed` - 任务失败时

### 3. 系统事件
- `system_startup` - 系统启动时
- `system_shutdown` - 系统关闭时

### 4. 数据事件
- `data_changed` - 数据变化时
- `file_created` - 文件创建时
- `file_deleted` - 文件删除时

## 配置格式

```yaml
hooks:
  session_start:
    - name: 晨间简报
      enabled: true
      actions:
        - type: display_briefing
      priority: 10

  task_completed:
    - name: 任务归档
      enabled: true
      actions:
        - type: archive_task
      priority: 5
```

## 实现要点

### 管理器职责
1. 加载配置文件
2. 注册事件处理器
3. 触发时匹配并执行
4. 处理执行结果

### 处理器接口
```python
def handle(event_name: str, context: dict) -> dict:
    """
    event_name: 事件名称
    context: 事件上下文数据
    return: 执行结果
    """
```

### 优先级
- 数值越大，优先级越高
- 同优先级按注册顺序执行
- 可用于控制执行顺序

## 实践应用

### 晨间简报（session_start）
- 检查今日任务
- 显示未完成事项
- 提供快速开始入口

### 任务归档（task_completed）
- 将已完成任务移至归档
- 更新统计数字
- 保留完整元数据

### 数据维护（周期性）
- 周日提醒数据录入
- 月度日记合并
- 存储复盘报告

## 优势

✅ **解耦**：业务逻辑与扩展功能分离
✅ **可扩展**：新增功能无需修改核心代码
✅ **可配置**：通过 YAML 文件灵活配置
✅ **可测试**：每个 Hook 可独立测试

## 相关文件

- `system/hooks_manager.py` - Hooks 管理器
- `config/hooks.yaml` - Hooks 配置
- `system/hooks/` - Hook 处理器目录

## 扩展方向

- [ ] 支持异步 Hook 执行
- [ ] 添加 Hook 依赖关系
- [ ] Hook 执行结果聚合
- [ ] Hook 性能监控
