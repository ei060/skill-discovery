# 记忆搜索系统 v3.0 迁移指南

## 快速开始

### 1. 验证安装

```bash
cd AI_Roland
python system/test_v3_logic.py
```

预期输出：所有测试通过 ✓

### 2. 运行完整测试

```bash
python system/memory_search_v3.py
```

预期输出：
- 模型自动下载（首次，~420MB）
- 47 个文档编码
- 4 个测试查询正常

### 3. 使用新系统

```python
# 导入新版本
from system.memory_search_v3 import MemorySearchV3

# 初始化
search = MemorySearchV3()

# 搜索（API 完全兼容 v2.1）
results = search.search("任务管理", top_k=5)
```

---

## API 对比

### 搜索（完全兼容）

```python
# v2.1
from system.memory_search import MemorySearch
search = MemorySearch()
results = search.search("任务管理", top_k=5, use_time_weight=True)

# v3.0（API 完全相同）
from system.memory_search_v3 import MemorySearchV3
search = MemorySearchV3()
results = search.search("任务管理", top_k=5, use_time_weight=True)
```

### 按类型搜索（完全兼容）

```python
# 两个版本 API 相同
results = search.search_by_type("任务管理", "semantic_memory", top_k=3)
```

---

## 主要区别

### 1. 搜索质量提升

**示例**: 搜索"记忆系统"

| 版本 | 最佳结果 | 相似度 | 说明 |
|------|----------|--------|------|
| v2.1 | 关键词匹配 | 0.3-0.5 | 依赖关键词重叠 |
| v3.0 | 语义理解 | 0.7-0.9 | 理解查询意图 |

### 2. 首次启动时间

| 版本 | 首次启动 | 后续启动 |
|------|----------|----------|
| v2.1 | ~0.5秒 | ~0.5秒 |
| v3.0 | ~3-5秒 | ~0.5秒（使用缓存） |

**说明**:
- v3.0 首次需要加载模型（~420MB，仅一次）
- 向量自动缓存到 `system/cache/embeddings_cache.pkl`
- 后续启动速度与 v2.1 相同

### 3. 新增功能

```python
# 查看系统统计
stats = search.get_stats()
# {'version': '3.0', 'model': '...', 'total_documents': 47, ...}

# 清空缓存
search.clear_cache()
# 删除所有缓存文件，强制重新生成
```

---

## 常见问题

### Q1: 首次运行很慢？

**原因**: 下载模型 + 编码文档

**解决**:
- 耐心等待 3-5 分钟（仅首次）
- 后续启动速度恢复正常（~0.5秒）

### Q2: 搜索结果不如 v2.1？

**原因**: 语义理解和关键词匹配逻辑不同

**解决**:
- 调整查询词，使用更自然的表达
- 例如："如何管理任务" vs "任务管理"

### Q3: 想回退到 v2.1？

**方法**:
```python
# 直接导入旧版本
from system.memory_search import MemorySearch
search = MemorySearch()
```

**说明**: v2.1 完全保留，可以随时切换

### Q4: 如何更新缓存？

**场景**: 添加新文档后

**方法 1**: 自动检测
```python
# v3.0 自动检测文档变化，自动重新编码
search = MemorySearchV3()  # 自动更新
```

**方法 2**: 手动清空
```python
search.clear_cache()  # 强制重新生成
```

---

## 性能优化建议

### 1. 预加载模型

```python
# 启动时预加载，避免首次搜索等待
search = MemorySearchV3()
_ = search.model  # 强制加载模型
```

### 2. 批量搜索

```python
# 批量搜索，复用编码结果
queries = ["任务管理", "记忆系统", "技能集成"]
for query in queries:
    results = search.search(query)  # 使用缓存，速度快
```

### 3. 定期清理缓存

```bash
# 手动清理缓存文件
rm AI_Roland/system/cache/*.pkl
rm AI_Roland/system/cache/*.json
```

---

## 下一步

- [x] Phase 3: Sentence Transformers 集成（已完成）
- [ ] Phase 4: ChromaDB 集成（下月）
- [ ] Phase 5: 自动提炼机制（下月）

---

**文档版本**: 1.0
**更新日期**: 2026-03-29
