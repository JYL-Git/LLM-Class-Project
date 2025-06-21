from pipelines.rerank_rag_pipeline import generate_investment_recommendation
from email_sender import send_email
from datetime import datetime

def build_email_body(query: str, answer: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    body = f"""📅 LLM 투자 리포트 - {today}

📝 질문:
{query}

📈 LLM 추천:
{answer}
"""
    return body

if __name__ == "__main__":
    # 보낼 질문
    query = "최근 뉴스 기반으로 투자 유망한 주식은?"

    try:
        answer = generate_investment_recommendation(query)
        email_body = build_email_body(query, answer)
        send_email(
            subject=f"📈 LLM 자동 리포트 ({datetime.now().strftime('%Y-%m-%d')})",
            body=email_body,
            to_email="jaeyonglee110@gmail.com"
        )
        print("✅ 이메일 전송 완료")
    except Exception as e:
        print(f"❌ 이메일 전송 실패: {e}")
