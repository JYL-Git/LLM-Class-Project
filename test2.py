from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re


def get_today_naver_news(max_articles=100):
    base_url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&page={}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    # 1️⃣ 첫 페이지 로딩
    driver.get(base_url.format(1))
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # 2️⃣ 오늘 날짜 형식 가져오기 ("06월09일")
    today_kor = datetime.now().strftime("%m월%d일")

    day_text = soup.select_one("div.pagenavi_day > span.viewday")
    if not day_text or today_kor not in day_text.text:
        print("❌ 오늘 날짜가 아닙니다.")
        driver.quit()
        return []

    # 3️⃣ 전체 페이지 수 구하기
    last_page = 1
    pages = soup.select("table.Nnavi td > a")
    for p in pages:
        try:
            num = int(p.text)
            last_page = max(last_page, num)
        except ValueError:
            continue

    print(f"🔎 총 페이지 수: {last_page}")
    today_str = datetime.now().strftime("%Y-%m-%d")
    results = []

    # 4️⃣ 각 페이지 탐색
    for page_num in range(1, last_page + 1):
        driver.get(base_url.format(page_num))
        time.sleep(1.5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        news_items = soup.select("li.newsList.top, li.newsList")
        for item in news_items:
            title_tag = item.select_one("dd.articleSubject > a")
            date_tag = item.select_one("dd.articleSummary > span.wdate")
            if not title_tag or not date_tag:
                continue

            title = title_tag.get("title", "").strip()
            link = title_tag.get("href", "").strip()
            date_text = date_tag.get_text(strip=True)

            # 5️⃣ 날짜 필터링
            if not date_text.startswith(today_str):
                continue

            results.append({
                "title": title,
                "link": link,
                "date": date_text
            })

            if len(results) >= max_articles:
                driver.quit()
                return results

    driver.quit()
    return results


if __name__ == "__main__":
    news_list = get_today_naver_news(max_articles=100)
    if not news_list:
        print("❌ 오늘 뉴스가 없습니다.")
    else:
        print(f"✅ 오늘자 뉴스 {len(news_list)}건 수집 완료:\n")
        for news in news_list:
            print(f"[{news['date']}] {news['title']}")
            print(f"👉 {news['link']}\n")
