"""RAG 性能测试脚本"""
import time
import tempfile
import os
from pathlib import Path


def test_document_processor():
    """测试文档处理"""
    print("\n[TEST 1] Document Processor")

    from app.rag.document_processor import DocumentProcessor

    # 创建测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("这是第一段测试内容。\n\n")
        f.write("这是第二段测试内容，包含一些技术术语：Python、FastAPI、ChromaDB。\n\n")
        f.write("这是第三段内容，用于测试分块效果。\n\n")
        f.write("第四段：RAG (Retrieval-Augmented Generation) 是一种结合检索和生成的技术。\n\n")
        f.write("第五段：向量数据库用于存储嵌入向量，支持高效的相似度搜索。")
        temp_path = f.name

    try:
        chunks = DocumentProcessor.process(temp_path, "txt")
        print(f"   [OK] Document parsed, {len(chunks)} chunks")
        print(f"   Content length: {len(chunks[0].content) if chunks else 0} chars")
    finally:
        os.unlink(temp_path)


def test_text_chunker():
    """测试文本分块"""
    print("\n[TEST 2] Text Chunker")

    from app.rag.chunker import TextChunker
    from app.config import settings

    chunker = TextChunker()

    text = """
    第一段内容。这是一个很长的段落，包含了很多信息。我们需要测试分块功能是否正常工作。
    第二段内容。这里有一些技术术语：机器学习、深度学习、神经网络、Transformer、BERT。
    第三段内容。向量数据库是 RAG 系统的重要组成部分，常见的选择包括 ChromaDB、Qdrant、Weaviate。
    第四段内容。企业内部知识库需要支持多种文档格式，包括 PDF、Word、Excel、Markdown 等。
    第五段内容。RAG 系统的性能优化包括：批量 embedding、查询缓存、异步处理、向量化索引优化。
    """

    chunks = chunker.chunk_text(text, document_id=1)

    print(f"   [OK] Chunking complete, {len(chunks)} chunks")
    print(f"   Chunk size: {settings.CHUNK_SIZE}, Overlap: {settings.CHUNK_OVERLAP}")
    for i, chunk in enumerate(chunks[:3]):
        print(f"   Chunk {i+1}: {len(chunk.text)} chars")


def test_embedding_service():
    """测试 Embedding 服务"""
    print("\n[TEST 3] Embedding Service")

    from app.rag.embedding import EmbeddingService, MockEmbeddingService

    # 测试 Mock 服务（不需要 Ollama）
    mock = MockEmbeddingService()

    texts = ["测试文本1", "测试文本2", "测试文本3"]
    start = time.time()
    embeddings = mock.embed_texts(texts)
    elapsed = time.time() - start

    print(f"   [OK] Mock Embedding complete")
    print(f"   Text count: {len(texts)}")
    print(f"   Vector dimension: {mock.get_embedding_dimension()}")
    print(f"   Time: {elapsed:.3f}s")

    # 测试真实服务（需要 Ollama）
    print("\n   Trying to connect to Ollama...")
    try:
        real = EmbeddingService()
        if real.is_available():
            start = time.time()
            emb = real.embed_text("测试")
            elapsed = time.time() - start
            print(f"   [OK] Real Embedding available, dimension: {len(emb)}, time: {elapsed:.3f}s")
        else:
            print("   [SKIP] Ollama not running, skip real test")
    except Exception as e:
        print(f"   [SKIP] Ollama connection failed: {e}")


def test_vector_store():
    """测试向量存储"""
    print("\n[TEST 4] Vector Store (ChromaDB)")

    from app.rag.vector_store import VectorStore
    from app.rag.chunker import Chunk
    from app.rag.embedding import MockEmbeddingService, EmbeddingService

    # 使用固定目录避免并发问题
    test_dir = "./data/test_chroma"
    os.makedirs(test_dir, exist_ok=True)

    # 临时修改配置
    from app import config
    original = config.settings.CHROMA_PERSIST_DIR
    config.settings.CHROMA_PERSIST_DIR = test_dir

    try:
        store = VectorStore(collection_name=f"test_rag_{int(time.time())}")

        # 添加测试数据
        chunks = [
            Chunk(text="这是关于 Python 编程的内容", chunk_index=0, document_id=1, start_char=0, end_char=30),
            Chunk(text="这是关于 FastAPI Web 框架的内容", chunk_index=1, document_id=1, start_char=30, end_char=60),
            Chunk(text="这是关于 ChromaDB 向量数据库的内容", chunk_index=2, document_id=2, start_char=0, end_char=35),
        ]

        # 使用真实 Embedding 服务的维度
        real_embedding = EmbeddingService()
        dim = real_embedding.get_embedding_dimension()
        mock = MockEmbeddingService(dimension=dim)

        embeddings = mock.embed_texts([c.text for c in chunks])

        start = time.time()
        store.add_chunks(chunks, embeddings)
        elapsed = time.time() - start

        print(f"   [OK] Added {len(chunks)} chunks, time: {elapsed:.3f}s")
        print(f"   Total vectors: {store.count()}")

        # 测试搜索
        query_emb = mock.embed_text("Python 编程")
        start = time.time()
        results = store.search(query_emb, document_ids=[1], top_k=2)
        elapsed = time.time() - start

        print(f"   [OK] Search complete, time: {elapsed:.3f}s")
        print(f"   Results: {len(results)} items")
        for r in results:
            print(f"      - {r.text[:30]}... (score: {r.score:.2f})")

        # 测试单文档查询（兼容旧接口）
        results2 = store.search(query_emb, document_ids=[1], top_k=2)
        print(f"   [OK] Single-doc search: {len(results2)} items")

    finally:
        config.settings.CHROMA_PERSIST_DIR = original


def test_rag_service():
    """测试 RAG 完整流程"""
    print("\n[TEST 5] RAG Service")

    from app.rag.rag_service import RAGService

    rag = RAGService()

    print(f"   Embedding service: {type(rag.embedding_service).__name__}")
    print(f"   LLM service: {type(rag.llm_service).__name__ if rag.llm_service else 'None'}")
    print(f"   Vector store: {type(rag.vector_store).__name__}")

    stats = rag.get_index_stats()
    print(f"   Stats: {stats}")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("RAG System Function Test")
    print("=" * 50)

    try:
        test_document_processor()
        test_text_chunker()
        test_embedding_service()
        test_vector_store()
        test_rag_service()

        print("\n" + "=" * 50)
        print("All tests passed!")
        print("=" * 50)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()