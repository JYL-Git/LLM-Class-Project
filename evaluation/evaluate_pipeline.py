import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from modules.retriever import retrieve_similar_documents
from modules.reranker import rerank_documents
from utils.utils import clean_text, OPENAI_API_KEY
from openai import OpenAI
import json

client = OpenAI(api_key=OPENAI_API_KEY)

MAX_DOC_CHAR_LENGTH = 500
TOP_K = 5

# GPT를 이용해 문서-질문 관련도 평가
def get_relevance_scores(query, docs):
    context = ""
    for i, doc in enumerate(docs):
        body = clean_text(doc["content"])[:MAX_DOC_CHAR_LENGTH]
        context += f"[{i}] Title: {doc['title']}\nContent: {body}\n\n"

    system_prompt = (
        "You are evaluating how relevant each news article is to a user query.\n"
        "Score each article from 1 (not relevant) to 10 (highly relevant).\n"
        "Only return a JSON list like [{\"index\": 0, \"score\": 8}, ...]"
    )

    user_prompt = (
        f"User query: {query}\n\nArticles:\n{context}\n"
        "Respond only with the JSON list."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    try:
        return [item["score"] for item in json.loads(response.choices[0].message.content)]
    except:
        return [5] * len(docs)  # fallback 평균치

# 문서 간 novelty 측정 (1 - 평균 유사도)
def get_novelty_score(docs):
    contents = [clean_text(d["content"])[:MAX_DOC_CHAR_LENGTH] for d in docs]
    vectorizer = TfidfVectorizer().fit_transform(contents)
    sim_matrix = cosine_similarity(vectorizer)
    avg_sim = (np.sum(sim_matrix) - len(docs)) / (len(docs) * (len(docs) - 1))
    return 1 - avg_sim

# redundancy = 평균 유사도
def get_redundancy_score(docs):
    contents = [clean_text(d["content"])[:MAX_DOC_CHAR_LENGTH] for d in docs]
    vectorizer = TfidfVectorizer().fit_transform(contents)
    sim_matrix = cosine_similarity(vectorizer)
    avg_sim = (np.sum(sim_matrix) - len(docs)) / (len(docs) * (len(docs) - 1))
    return avg_sim

# GPT 응답의 informativeness 평가
def get_informativeness_score(query, docs):
    context = "\n---\n".join([
        f"[{i+1}] {doc['title']}\n{clean_text(doc['content'])[:MAX_DOC_CHAR_LENGTH]}"
        for i, doc in enumerate(docs)
    ])

    system_prompt = (
        "You are an expert evaluator. Given the question and supporting news articles, "
        "evaluate how informative a response would likely be, on a scale from 1 (poor) to 10 (excellent)."
    )

    user_prompt = (
        f"Question: {query}\n\nRelevant News Articles:\n{context}\n\n"
        "How informative do you expect the answer will be? Respond only with a number from 1 to 10."
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )
    try:
        return float(response.choices[0].message.content.strip())
    except:
        return 5.0

# 전체 평가
def evaluate(query):
    retrieved = retrieve_similar_documents(query)

    # RAG-only
    rag_docs = retrieved[:TOP_K]
    rag_relevance = get_relevance_scores(query, rag_docs)
    rag_novelty = get_novelty_score(rag_docs)
    rag_redundancy = get_redundancy_score(rag_docs)
    rag_info = get_informativeness_score(query, rag_docs)

    # RAG + rerank
    reranked_docs = rerank_documents(query, retrieved)
    rerank_relevance = get_relevance_scores(query, reranked_docs)
    rerank_novelty = get_novelty_score(reranked_docs)
    rerank_redundancy = get_redundancy_score(reranked_docs)
    rerank_info = get_informativeness_score(query, reranked_docs)

    print("\n📊 Evaluation Result")
    print("--------------------------------------------------------")
    print(f"RAG-only     | Relevance: {np.mean(rag_relevance):.2f} | Novelty: {rag_novelty:.2f} | Redundancy: {rag_redundancy:.2f} | Informativeness: {rag_info:.2f}")
    print(f"RAG+Reranker | Relevance: {np.mean(rerank_relevance):.2f} | Novelty: {rerank_novelty:.2f} | Redundancy: {rerank_redundancy:.2f} | Informativeness: {rerank_info:.2f}")

if __name__ == "__main__":
    query = input("📝 평가할 질문을 입력하세요: ").strip()
    evaluate(query)
