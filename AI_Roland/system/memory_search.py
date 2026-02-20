"""
记忆搜索系统 - 基于语义相似度的智能检索
使用 TF-IDF 和余弦相似度进行语义搜索
v2.0: 集成 jieba 分词，提升中文搜索准确度
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from collections import Counter
import math
import jieba


class MemorySearch:
    """记忆搜索引擎"""

    def __init__(self, workspace_path=None):
        if workspace_path is None:
            current_dir = Path(__file__).parent
            self.workspace = current_dir.parent
        else:
            self.workspace = Path(workspace_path)

        self.memory_lib = self.workspace / "记忆库"
        self.chat_history = self.workspace / "对话历史.md"
        self.diary_dir = self.workspace / "日记"

        # 缓存
        self._documents_cache = None
        self._tfidf_cache = None

    def load_documents(self) -> List[Dict[str, any]]:
        """加载所有文档"""
        if self._documents_cache is not None:
            return self._documents_cache

        documents = []

        # 1. 加载对话历史
        if self.chat_history.exists():
            content = self.chat_history.read_text(encoding='utf-8')
            sessions = re.split(r'---+', content)

            for session in sessions:
                if not session.strip():
                    continue

                # 提取会话信息
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', session)
                user_match = re.search(r'\*\*用户\*\*：(.+)', session)
                task_match = re.search(r'\*\*任务\*\*：(.+)', session)

                if date_match or user_match:
                    documents.append({
                        "type": "conversation",
                        "date": date_match.group(1) if date_match else "",
                        "user": user_match.group(1).strip() if user_match else "",
                        "task": task_match.group(1).strip() if task_match else "",
                        "content": session.strip(),
                        "path": str(self.chat_history)
                    })

        # 2. 加载日记
        if self.diary_dir.exists():
            for diary_file in self.diary_dir.glob("*.md"):
                content = diary_file.read_text(encoding='utf-8')
                documents.append({
                    "type": "diary",
                    "date": diary_file.stem,
                    "content": content,
                    "path": str(diary_file)
                })

        # 3. 加载语义记忆
        semantic_mem_dir = self.memory_lib / "语义记忆"
        if semantic_mem_dir.exists():
            for mem_file in semantic_mem_dir.glob("*.md"):
                content = mem_file.read_text(encoding='utf-8')
                documents.append({
                    "type": "semantic_memory",
                    "name": mem_file.stem,
                    "content": content,
                    "path": str(mem_file)
                })

        self._documents_cache = documents
        return documents

    def tokenize(self, text: str) -> List[str]:
        """使用 jieba 分词（中文和英文）"""
        # 移除特殊字符，保留中英文、数字、空格
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)

        # 使用 jieba 分词
        tokens = jieba.lcut(text)

        # 过滤和清理
        filtered_tokens = []
        for token in tokens:
            token = token.strip()
            # 过滤单字符和空字符串
            if len(token) <= 1:
                continue
            # 过滤纯数字
            if token.isdigit():
                continue
            # 过滤纯标点
            if not any(char.isalnum() or '\u4e00' <= char <= '\u9fff' for char in token):
                continue

            # 英文转小写
            if not any('\u4e00' <= char <= '\u9fff' for char in token):
                token = token.lower()

            filtered_tokens.append(token)

        return filtered_tokens

    def compute_tfidf(self, documents: List[Dict]) -> Dict[str, Dict[str, float]]:
        """计算 TF-IDF"""
        if self._tfidf_cache is not None:
            return self._tfidf_cache

        # 文档频率
        df = Counter()
        # 词频
        tf = {}

        for doc in documents:
            tokens = self.tokenize(doc["content"])
            token_set = set(tokens)

            # 更新文档频率
            for token in token_set:
                df[token] += 1

            # 记录词频
            tf[doc["path"]] = Counter(tokens)

        # 计算 TF-IDF
        num_docs = len(documents)
        tfidf = {}

        for doc in documents:
            path = doc["path"]
            tfidf[path] = {}

            for token, freq in tf[path].items():
                # TF: 词频
                tf_score = freq / len(tf[path])
                # IDF: 逆文档频率
                idf_score = math.log(num_docs / (df[token] + 1))
                # TF-IDF
                tfidf[path][token] = tf_score * idf_score

        self._tfidf_cache = tfidf
        return tfidf

    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """计算余弦相似度"""
        # 获取所有词汇
        all_tokens = set(vec1.keys()) | set(vec2.keys())

        # 计算点积
        dot_product = sum(vec1.get(token, 0) * vec2.get(token, 0) for token in all_tokens)

        # 计算模长
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0

        return dot_product / (norm1 * norm2)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """搜索相关记忆"""
        documents = self.load_documents()
        tfidf = self.compute_tfidf(documents)

        # 处理查询
        query_tokens = self.tokenize(query)
        query_tf = Counter(query_tokens)

        # 构建查询向量
        query_vec = {}
        for token, freq in query_tf.items():
            query_vec[token] = freq / len(query_tokens)

        # 计算相似度
        results = []
        for doc in documents:
            doc_vec = tfidf.get(doc["path"], {})
            similarity = self.cosine_similarity(query_vec, doc_vec)

            if similarity > 0:
                results.append({
                    "document": doc,
                    "similarity": similarity,
                    "snippet": self._extract_snippet(doc["content"], query_tokens)
                })

        # 按相似度排序
        results.sort(key=lambda x: x["similarity"], reverse=True)

        return results[:top_k]

    def _extract_snippet(self, content: str, query_tokens: List[str], max_length: int = 200) -> str:
        """提取包含查询词的片段"""
        # 简单实现：找到第一个匹配的词周围的内容
        for token in query_tokens:
            if token in content:
                idx = content.index(token)
                start = max(0, idx - 50)
                end = min(len(content), idx + max_length)
                snippet = content[start:end]
                return snippet + "..." if len(content) > end else snippet

        # 如果没找到匹配，返回开头
        return content[:max_length] + "..."

    def search_by_type(self, query: str, doc_type: str, top_k: int = 5) -> List[Dict]:
        """按类型搜索"""
        documents = self.load_documents()
        filtered = [d for d in documents if d["type"] == doc_type]

        # 临时替换文档缓存
        original_cache = self._documents_cache
        self._documents_cache = filtered

        try:
            results = self.search(query, top_k)
        finally:
            self._documents_cache = original_cache

        return results

    def get_related_memories(self, current_context: str, top_k: int = 3) -> List[Dict]:
        """根据当前上下文获取相关记忆"""
        return self.search(current_context, top_k)

    def clear_cache(self):
        """清空缓存"""
        self._documents_cache = None
        self._tfidf_cache = None


def main():
    """测试记忆搜索"""
    import sys
    import io

    # 设置标准输出为 UTF-8
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    search = MemorySearch()

    print("=== 记忆搜索系统测试（jieba 分词）===\n")

    print("1. 加载文档:")
    documents = search.load_documents()
    print(f"   共加载 {len(documents)} 个文档")
    print(f"   - 对话: {sum(1 for d in documents if d['type'] == 'conversation')}")
    print(f"   - 日记: {sum(1 for d in documents if d['type'] == 'diary')}")
    print(f"   - 语义记忆: {sum(1 for d in documents if d['type'] == 'semantic_memory')}")

    print("\n2. 测试搜索:")
    query = "任务 管理"
    results = search.search(query, top_k=3)

    print(f"   查询: {query}")
    print(f"   找到 {len(results)} 个相关结果:\n")

    for i, result in enumerate(results, 1):
        doc = result["document"]
        # 移除 emoji 和特殊字符，避免编码错误
        snippet = result['snippet'][:80]
        snippet = ''.join(c if ord(c) < 128 else '?' for c in snippet)

        print(f"   {i}. [{doc['type']}] {doc.get('date', doc.get('name', 'N/A'))}")
        print(f"      相似度: {result['similarity']:.3f}")
        print(f"      片段: {snippet}...")
        print()

    print("3. 测试按类型搜索:")
    results = search.search_by_type(query, "conversation", top_k=2)
    print(f"   对话历史中找到 {len(results)} 个结果")


if __name__ == "__main__":
    main()
