from modules.retriever import retrieve_similar_documents
from modules.reranker import rerank_documents
from openai import OpenAI
from config import TOP_K_RERANK
from utils.utils import OPENAI_API_KEY, clean_text, count_tokens, logger

client = OpenAI(api_key=OPENAI_API_KEY)

MAX_DOC_CHAR_LENGTH = 600
MAX_DOC_COUNT = 5

def generate_investment_recommendation(query: str):
    retrieved_docs = retrieve_similar_documents(query)
    top_docs = rerank_documents(query, retrieved_docs)

    logger.info("📚 선택된 문서 목록:")
    for i, doc in enumerate(top_docs):
        logger.info(f"[{i+1}] {doc['title']}")

    context = "\n---\n".join([
        f"[{i+1}] {doc['title']}\n{clean_text(doc['content'])[:MAX_DOC_CHAR_LENGTH]}"
        for i, doc in enumerate(top_docs[:MAX_DOC_COUNT])
    ])

    system_prompt = (
        "You are a professional financial advisor AI. Based on the news articles provided, "
        "recommend 1~3 promising stock sectors or companies in Korea. Explain your reasoning."
    )

    user_prompt = (
        f"User question: {query}\n\nRelevant News Articles:\n{context}\n\n"
        "Please answer in concise Korean with bullet points."
    )

    full_prompt = system_prompt + "\n" + user_prompt
    logger.info(f"🧮 전체 메시지 예상 토큰 수: {count_tokens(full_prompt)}")

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        top_p=1.0
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    print("💬 사용자 질문을 입력하세요 (예: 최근 뉴스 기반으로 투자 유망한 주식은?)")
    query = input("📝 질문: ").strip()

    if not query:
        print("❗ 질문이 비어 있습니다. 프로그램을 종료합니다.")
    else:
        print("\n🔍 질문 기반 추천을 시작합니다...\n")
        try:
            recommendation = generate_investment_recommendation(query)
            print("\n📈 투자 추천 결과:")
            print(recommendation)
        except Exception as e:
            logger.error(f"❌ 오류 발생: {e}")
