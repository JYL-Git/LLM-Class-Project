from modules.retriever import retrieve_similar_documents
from openai import OpenAI
from config import TOP_K_RERANK
from utils.utils import OPENAI_API_KEY, clean_text, count_tokens, logger

client = OpenAI(api_key=OPENAI_API_KEY)

MAX_DOC_CHAR_LENGTH = 300
MAX_DOC_COUNT = 3

def generate_investment_recommendation(query: str):
    retrieved_docs = retrieve_similar_documents(query)
    top_docs = retrieved_docs[:TOP_K_RERANK]  # rerank 없이 단순 상위 K개 사용

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

    total_text = system_prompt + "\n" + user_prompt
    logger.info(f"🧮 rag_pipeline prompt token count: {count_tokens(total_text)}")

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
    print("💬 사용자 질문을 입력하세요 (예: 요즘 반도체 관련 투자 종목은?)")
    query = input("📝 질문: ").strip()

    if not query:
        print("❗ 질문이 비어 있습니다.")
    else:
        print("\n🔍 RAG 파이프라인 실행 중...\n")
        result = generate_investment_recommendation(query)
        print("\n📈 GPT 추천 결과:")
        print(result)
