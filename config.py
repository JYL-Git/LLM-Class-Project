# config.py
import os

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4-turbo"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NEWS_JSON_PATH = os.path.join(BASE_DIR, "data/raw_news.json")
EMBEDDING_STORE_PATH = os.path.join(BASE_DIR, "data/news_embeddings.pkl")

TOP_K_RETRIEVE = 20  # FAISS 유사 뉴스 추출
TOP_K_RERANK = 5     # LLM rerank 후 실제 사용 문서 수
MAX_CONTEXT_DOCS = 5  # LLM에 넘기는 뉴스 수 제한
