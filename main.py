from scraping.news_scraper import get_news_by_date
from rerank_rag_pipeline import reranked_rag

if __name__ == "__main__":
    news_list = get_news_by_date("20250610")
    question = "지금 투자할 만한 주식은?"
    result = reranked_rag(news_list, question)
    print(result)
