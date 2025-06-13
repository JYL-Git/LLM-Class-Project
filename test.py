from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_today_naver_news(max_articles=10):
    url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    today = datetime.now().strftime("%Y-%m-%d")
    results = []

    # 상단 10개 + 하단 10개 뉴스 모두 가져오기
    news_items = soup.select("li.newsList.top, li.newsList")
    for item in news_items:
        title_tag = item.select_one("dd.articleSubject > a")
        date_tag = item.select_one("dd.articleSummary > span.wdate")

        if not title_tag or not date_tag:
            continue

        title = title_tag.get("title", "").strip()
        link = title_tag.get("href", "").strip()
        date_text = date_tag.get_text(strip=True)

        # 날짜가 오늘인 경우만 포함
        if not date_text.startswith(today):
            continue

        results.append({
            "title": title,
            "link": link,
            "date": date_text
        })

        if len(results) >= max_articles:
            break

    return results

if __name__ == "__main__":
    news_list = get_today_naver_news()
    if not news_list:
        print("❌ 오늘 뉴스가 없습니다.")
    else:
        print(f"✅ 오늘자 뉴스 {len(news_list)}건:\n")
        for news in news_list:
            print(f"[{news['date']}] {news['title']}")
            print(f"👉 {news['link']}\n")
