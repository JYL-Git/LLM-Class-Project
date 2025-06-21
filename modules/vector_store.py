import faiss
import numpy as np
import pickle

from config import EMBEDDING_STORE_PATH, TOP_K_RETRIEVE

class VectorStore:
    def __init__(self):
        self.index = None
        self.documents = []  # 각 문서의 메타 정보 포함

    def build_index(self, embedded_data):
        vectors = [item["embedding"] for item in embedded_data]
        self.documents = embedded_data
        dim = len(vectors[0])
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(vectors).astype("float32"))

    def save(self, path=EMBEDDING_STORE_PATH):
        with open(path, "wb") as f:
            pickle.dump({"index": self.index, "documents": self.documents}, f)

    def load(self, path=EMBEDDING_STORE_PATH):
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.index = data["index"]
            self.documents = data["documents"]

    def search(self, query_vector, top_k=TOP_K_RETRIEVE):
        D, I = self.index.search(np.array([query_vector]).astype("float32"), top_k)
        results = [self.documents[i] for i in I[0]]
        return results

# 예시 실행 코드 (임베딩 데이터 로드 및 저장)
if __name__ == "__main__":
    with open(EMBEDDING_STORE_PATH, 'rb') as f:
        embedded_data = pickle.load(f)

    store = VectorStore()
    store.build_index(embedded_data)
    store.save()
    print(f"✅ FAISS 인덱스 저장 완료: {EMBEDDING_STORE_PATH}")
