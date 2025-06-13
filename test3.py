from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time

def get_today_news_by_url_loop(max_page=50):
    base_url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&page={}"
    today_str = datetime.now().strftime("%Y-%m-%d")
    results = []

    # headless selenium 설정
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    for page in range(1, max_page + 1):
        url = base_url.format(page)
        driver.get(url)
        time.sleep(1.5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        news_items = soup.select("li.newsList.top, li.newsList")

        page_has_today_news = False

        for item in news_items:
            title_tag = item.select_one("dd.articleSubject > a")
            date_tag = item.select_one("dd.articleSummary > span.wdate")
            if not title_tag or not date_tag:
                continue

            date_text = date_tag.get_text(strip=True)
            if not date_text.startswith(today_str):
                continue

            page_has_today_news = True
            title = title_tag.get("title", "").strip()
            link = title_tag.get("href", "").strip()

            results.append({
                "title": title,
                "link": "https://finance.naver.com" + link,
                "date": date_text
            })

        # 오늘 뉴스가 없는 페이지를 만나면 종료
        if not page_has_today_news:
            break

    driver.quit()
    return results

if __name__ == "__main__":
    news = get_today_news_by_url_loop()
    if news:
        print(f"\n✅ 오늘 뉴스 {len(news)}건 수집 완료\n")
        for n in news:
            print(f"[{n['date']}] {n['title']}")
            print(f"👉 {n['link']}\n")
    else:
        print("❌ 오늘 뉴스가 없습니다.")
