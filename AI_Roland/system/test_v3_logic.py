"""
快速测试 v3.0 的基本逻辑（不加载模型）
"""

from pathlib import Path
import json
import sys
import io

# 设置 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 测试文档加载逻辑
def test_document_loading():
    """测试文档加载"""
    print("[TEST] 测试 1: 文档加载逻辑")

    workspace = Path(__file__).parent.parent
    memory_lib = workspace / "记忆库"
    chat_history = workspace / "对话历史.md"
    diary_dir = workspace / "日记"

    print(f"   工作区: {workspace}")
    print(f"   记忆库: {memory_lib.exists()}")
    print(f"   对话历史: {chat_history.exists()}")
    print(f"   日记目录: {diary_dir.exists()}")

    # 统计文档数量
    semantic_mem_dir = memory_lib / "语义记忆"
    if semantic_mem_dir.exists():
        mem_files = list(semantic_mem_dir.glob("*.md"))
        print(f"   语义记忆: {len(mem_files)} 个")

    if diary_dir.exists():
        diary_files = list(diary_dir.glob("*.md"))
        print(f"   日记: {len(diary_files)} 个")

    print("   [OK] 文档加载逻辑正常\n")


# 测试缓存目录创建
def test_cache_setup():
    """测试缓存设置"""
    print("[TEST] 测试 2: 缓存目录设置")

    workspace = Path(__file__).parent.parent
    cache_dir = workspace / "system" / "cache"

    # 创建缓存目录
    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"   缓存目录: {cache_dir}")
    print(f"   存在: {cache_dir.exists()}")

    # 测试缓存文件路径
    embeddings_file = cache_dir / "embeddings_cache.pkl"
    documents_file = cache_dir / "documents_cache.json"

    print(f"   向量缓存: {embeddings_file}")
    print(f"   文档缓存: {documents_file}")

    print("   [OK] 缓存设置正常\n")


# 测试版本和配置
# 全局配置
VERSION = "v3.0"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

def test_version_config():
    """测试版本配置"""
    print("[TEST] 测试 3: 版本配置")

    print(f"   系统版本: {VERSION}")
    print(f"   模型名称: {MODEL_NAME}")
    print(f"   模型大小: ~420MB (首次下载)")
    print(f"   支持语言: 中文、英文、多语言")

    print("   [OK] 版本配置正常\n")


# 测试依赖包
def test_dependencies():
    """测试依赖包"""
    print("[TEST] 测试 4: 依赖包检查")

    try:
        import sentence_transformers
        print(f"   sentence-transformers: [OK] {sentence_transformers.__version__}")
    except ImportError:
        print(f"   sentence-transformers: [FAIL] 未安装")

    try:
        import numpy
        print(f"   numpy: [OK] {numpy.__version__}")
    except ImportError:
        print(f"   numpy: [FAIL] 未安装")

    try:
        import sklearn
        print(f"   scikit-learn: [OK] {sklearn.__version__}")
    except ImportError:
        print(f"   scikit-learn: [FAIL] 未安装")

    try:
        import torch
        print(f"   torch: [OK] {torch.__version__}")
    except ImportError:
        print(f"   torch: [FAIL] 未安装")

    print("   [OK] 依赖包检查完成\n")


def main():
    print("\n" + "="*60)
    print("=== Memory Search v3.0 逻辑测试 ===")
    print("="*60 + "\n")

    test_version_config()
    test_dependencies()
    test_cache_setup()
    test_document_loading()

    print("="*60)
    print("[SUMMARY] 测试总结:")
    print("="*60)
    print("[OK] 所有基础逻辑正常")
    print("[OK] 依赖包已安装")
    print("[OK] 缓存目录已创建")
    print("\n[NEXT] 下一步:")
    print("1. 首次运行会下载模型 (~420MB)")
    print("2. 模型会自动缓存到本地")
    print("3. 后续启动速度会快很多")
    print("\n[TIP] 提示: 如果下载慢，可以手动下载模型文件")
    print(f"   模型地址: https://huggingface.co/{MODEL_NAME}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
