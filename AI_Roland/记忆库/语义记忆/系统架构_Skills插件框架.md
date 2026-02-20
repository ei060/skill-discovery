# Skills 插件框架

## 概念

Skills 是可插拔的功能模块，通过标准化的接口扩展系统能力。

## 核心架构

```
技能定义 → 技能管理器 → 动态加载 → 执行技能
```

## 技能结构

```
skills/
├── commit/
│   ├── skill.yaml      # 技能元数据
│   └── prompt.md       # 技能提示词
├── briefing/
│   ├── skill.yaml
│   └── prompt.md
└── test_skill/
    ├── skill.yaml
    └── prompt.md
```

## 技能元数据格式

```yaml
name: commit
version: 1.0.0
author: AI Roland
description: 智能代码提交助手
enabled: true
category: development

settings:
  require_confirmation: true
  timeout: 30

triggers:
  - /commit
  - "git commit"
```

## 核心功能

### 1. 技能发现
- 扫描 skills/ 目录
- 加载所有 skill.yaml
- 验证配置完整性

### 2. 技能加载
- 按需加载技能
- 缓存技能配置
- 支持热重载

### 3. 技能执行
- 解析技能参数
- 构建执行上下文
- 调用技能处理器
- 返回执行结果

### 4. 技能管理
- 列出所有技能
- 启用/禁用技能
- 查看技能详情

## 技能类型

### 1. 交互式技能
需要用户确认的技能
- 示例：commit、review

### 2. 自动技能
无需确认直接执行
- 示例：briefing、format

### 3. 查询式技能
返回信息不修改数据
- 示例：status、search

## 实现要点

### 统一接口
```python
class Skill:
    def execute(self, context: dict) -> dict:
        """执行技能"""
        pass

    def validate(self, params: dict) -> bool:
        """验证参数"""
        pass
```

### 错误处理
- 参数验证失败
- 执行超时
- 依赖缺失
- 权限不足

### 日志记录
- 技能调用记录
- 执行时间统计
- 错误堆栈追踪

## 实践案例

### commit 技能
- 分析 git 状态
- 生成提交信息
- 创建提交
- 推送到远程

### briefing 技能
- 读取任务清单
- 生成晨间简报
- 显示优先级分组
- 提供快速入口

## 优势

✅ **模块化**：每个技能独立开发和维护
✅ **可复用**：技能可在不同场景复用
✅ **可扩展**：新增技能无需修改框架
✅ **可测试**：每个技能可独立测试

## 相关文件

- `system/skills_manager.py` - Skills 管理器
- `system/skills/` - 技能目录
- `system/skills/README.md` - 技能开发指南

## 扩展方向

- [ ] 技能依赖管理
- [ ] 技能版本控制
- [ ] 技能市场（在线仓库）
- [ ] 技能性能监控
- [ ] 技能热更新

## 开发新技能

1. 创建技能目录：`system/skills/your_skill/`
2. 编写 skill.yaml 配置
3. 编写 prompt.md 提示词
4. 实现技能处理器（可选）
5. 测试技能功能
6. 启用技能
