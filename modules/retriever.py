from openai import OpenAI
from modules.embedder import get_embedding
from modules.vector_store import VectorStore

from config import EMBEDDING_STORE_PATH, TOP_K_RETRIEVE
from utils.utils import OPENAI_API_KEY, logger

client = OpenAI(api_key=OPENAI_API_KEY)

def retrieve_similar_documents(query: str, top_k=TOP_K_RETRIEVE):
    # 1. Query를 임베딩
    query_vec = get_embedding(query)

    # 2. 벡터 스토어 로드 후 검색
    store = VectorStore()
    store.load(EMBEDDING_STORE_PATH)

    results = store.search(query_vec, top_k=top_k)
    logger.info(f"🔍 Retrieved {len(results)} documents for query: '{query}'")
    return results

# 예시 실행
if __name__ == "__main__":
    query = "요즘 투자 유망한 반도체 주식은?"
    results = retrieve_similar_documents(query)

    for i, doc in enumerate(results):
        print(f"[{i+1}] {doc['title']}")
        print(f"👉 {doc['link']}")
        print(f"📰 {doc['content'][:100]}...\n")
