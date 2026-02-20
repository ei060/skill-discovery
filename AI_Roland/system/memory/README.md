# 记忆搜索系统

基于语义相似度的智能记忆检索。

## 功能

- 🔍 **语义搜索**：不仅匹配关键词，还理解语义
- 📊 **多维度检索**：支持对话历史、日记、语义记忆
- 🎯 **智能排序**：按相似度排序，返回最相关的结果
- ⚡ **缓存优化**：首次加载后缓存，后续查询快速

## 使用方法

### Python API

```python
from system.memory_search import MemorySearch

# 初始化
search = MemorySearch()

# 搜索相关记忆
results = search.search("任务管理", top_k=5)

for result in results:
    doc = result["document"]
    print(f"类型: {doc['type']}")
    print(f"相似度: {result['similarity']}")
    print(f"内容: {result['snippet']}")

# 按类型搜索
results = search.search_by_type("项目管理", "conversation")

# 根据当前上下文获取相关记忆
context = "正在开发新功能"
related = search.get_related_memories(context)
```

## 搜索算法

使用 **TF-IDF + 余弦相似度**：

1. **分词**：支持中文和英文
2. **TF-IDF**：计算词频-逆文档频率
3. **余弦相似度**：计算查询和文档的相似度
4. **排序**：按相似度降序返回

## 支持的文档类型

| 类型 | 路径 | 说明 |
|------|------|------|
| 对话历史 | 对话历史.md | 所有会话记录 |
| 日记 | 日记/*.md | 每日记录 |
| 语义记忆 | 记忆库/语义记忆/*.md | 提炼的知识 |

## 性能优化

- ✅ 文档缓存：避免重复加载
- ✅ TF-IDF 缓存：避免重复计算
- ⚡ 增量更新：只处理新增文档

## 升级到向量数据库

当前使用 TF-IDF，可以升级到：

1. **Sentence Transformers**：使用预训练模型
2. **ChromaDB**：本地向量数据库
3. **FAISS**：Facebook 的相似度搜索库

### 示例升级代码

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 编码文档
embeddings = model.encode([doc["content"] for doc in documents])

# 编码查询
query_embedding = model.encode(query)

# 计算相似度
from sklearn.metrics.pairwise import cosine_similarity
similarities = cosine_similarity([query_embedding], embeddings)[0]
```

## 测试

```bash
cd AI_Roland/system
python memory_search.py
```

## 未来改进

- [ ] 添加时间权重（最近的记忆更相关）
- [ ] 支持模糊搜索
- [ ] 添加同义词扩展
- [ ] 集成到对话流程中自动推荐
