import openai
import json
from tqdm import tqdm
from modules.vector_store import VectorStore
# from embedder import get_embedding
import pickle

from config import EMBED_MODEL, NEWS_JSON_PATH, EMBEDDING_STORE_PATH
from utils.utils import OPENAI_API_KEY, logger

openai.api_key = OPENAI_API_KEY

def load_news(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_embedding(text, model=EMBED_MODEL):
    response = openai.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def embed_news_articles(news_list):
    embedded_data = []
    for item in tqdm(news_list, desc="Embedding news articles"):
        try:
            content = item.get("content")
            if not content:
                continue
            embedding = get_embedding(content)
            embedded_data.append({
                "title": item["title"],
                "link": item["link"],
                "content": content,
                "embedding": embedding
            })
        except Exception as e:
            logger.warning(f"[Error] Skipping article: {e}")
    return embedded_data

def save_embeddings(data, path):
    store = VectorStore()
    store.build_index(data)
    store.save(path)

def main():
    news_list = load_news(NEWS_JSON_PATH)
    embedded = embed_news_articles(news_list)
    save_embeddings(embedded, EMBEDDING_STORE_PATH)
    logger.info(f"✅ Saved {len(embedded)} embeddings to {EMBEDDING_STORE_PATH}")

if __name__ == "__main__":
    main()
