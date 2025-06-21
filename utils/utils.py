# utils/utils.py
from dotenv import load_dotenv
load_dotenv()

import os
import logging
import re
import tiktoken

# ✅ 환경변수에서 API Key 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ 공통 텍스트 전처리 함수
def clean_text(text):
    return re.sub(r"<.*?>", "", text).replace("\n", " ").replace("\r", " ").strip()

# ✅ 토큰 수 계산 함수
def count_tokens(text, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))