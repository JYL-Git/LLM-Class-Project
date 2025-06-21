from openai import OpenAI
from config import TOP_K_RERANK
from utils.utils import OPENAI_API_KEY, clean_text, count_tokens, logger
import json

client = OpenAI(api_key=OPENAI_API_KEY)

def rerank_documents(query, documents):
    system_prompt = (
        "You are a professional financial analyst assistant. Given a user query and multiple news articles,\n"
        "score each article on a scale from 1 to 10 for relevance to the query.\n"
        "Only return a JSON list like [{\"index\": 0, \"score\": 9}, ...]. No explanations."
    )

    context = ""
    for i, doc in enumerate(documents):
        body = clean_text(doc["content"])[:300]
        context += f"[{i}]\nTitle: {doc['title']}\nContent: {body}\n\n"

    user_prompt = (
        f"Query: {query}\n\nNews Articles:\n{context}\n"
        "Now score each article based on relevance to the query. Respond only with JSON."
    )

    full_prompt = system_prompt + user_prompt
    logger.info(f"🧮 reranker prompt token count: {count_tokens(full_prompt)}")

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0
    )

    result_text = response.choices[0].message.content
    logger.debug("📤 GPT 응답 원문:\n" + repr(result_text))

    if not result_text or not result_text.strip().startswith("["):
        logger.warning("📭 GPT 응답이 비었거나 JSON 형식이 아닙니다.")
        logger.warning("🔁 응답 내용:\n" + repr(result_text))
        return documents[:TOP_K_RERANK]

    try:
        scored = json.loads(result_text)
    except Exception as e:
        logger.warning(f"❌ LLM 응답 파싱 실패: {e}")
        logger.warning("🔁 원본 응답: " + repr(result_text))
        return documents[:TOP_K_RERANK]

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)
    reranked_docs = [documents[item["index"]] for item in scored[:TOP_K_RERANK]]

    return reranked_docs

# 테스트 실행 예시 (직접 실행할 경우)
if __name__ == "__main__":
    sample_docs = [
        {"title": "삼성전자, AI 반도체 시장 확대", "content": "삼성전자가 새로운 AI 반도체를 출시하면서 관련 산업에 큰 기대가 모이고 있다."},
        {"title": "현대차, 전기차 수출 증가", "content": "현대차는 전기차 수출이 급증하며 매출이 증가하고 있다."},
        {"title": "SK하이닉스, HBM 공급 확대", "content": "SK하이닉스는 HBM 공급 확대를 통해 AI 시장 수요에 대응하고 있다."}
    ]
    query = "AI 반도체 관련 투자 종목 추천"
    result = rerank_documents(query, sample_docs)
    for i, doc in enumerate(result):
        print(f"{i+1}. {doc['title']}")
