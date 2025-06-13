from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import datetime

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def get_total_pages(soup):
    # 페이지 네비게이션에서 마지막 페이지 숫자 구하기
    try:
        navi = soup.select_one('table.Nnavi')
        pages = navi.select('a')
        page_numbers = [int(p.text) for p in pages if p.text.isdigit()]
        return max(page_numbers) if page_numbers else 1
    except:
        return 1

def get_news_list(soup):
    news_items = []
    bottom_section = soup.select("li.newsList:not(.top)")
    seen = set()

    for li in bottom_section:
        for a in li.select("a[title]"):
            href = a["href"]
            if href not in seen:
                seen.add(href)
                news_items.append({
                    "title": a["title"],
                    "link": "https://finance.naver.com" + href
                })
    return news_items

def get_article_content(driver, url):
    driver.get(url)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.select_one("#news_read")  # 본문 내용 ID
    return content.text.strip() if content else ""

def crawl_news_by_date(date_str):
    all_news = []
    base_url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date={date}&page={page}"
    driver = init_driver()

    # 첫 페이지로 soup 파싱
    driver.get(base_url.format(date=date_str, page=1))
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    total_pages = get_total_pages(soup)

    for page in range(1, total_pages + 1):
        print(f"🔄 {date_str} - Page {page}/{total_pages}")
        driver.get(base_url.format(date=date_str, page=page))
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        news_list = get_news_list(soup)

        for news in news_list:
            content = get_article_content(driver, news["link"])
            all_news.append({
                "date": date_str,
                "title": news["title"],
                "link": news["link"],
                "content": content
            })

    driver.quit()
    return all_news

# 예: 2025년 6월 11일
if __name__ == "__main__":
    news_data = crawl_news_by_date("20250611")
    print(f"\n총 {len(news_data)}개 뉴스 수집됨\n")
    for n in news_data:
        print(f"[{n['date']}] {n['title']}")
        print(f"👉 {n['link']}")
        print(f"{n['content'][:100]}...")  # 본문 일부 출력
