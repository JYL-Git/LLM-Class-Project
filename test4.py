from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

def get_news_from_page(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(3)  # 충분히 기다리기

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    news_results = []

    # 상단 뉴스 10개 (li.newsList.top 내 a 태그 10개)
    top_section = soup.select("li.newsList.top")
    if top_section:
        top_links = top_section[0].select("a[title]")
        for a in top_links[:10]:  # 최대 10개
            title = a["title"]
            link = a["href"]
            news_results.append({"title": title, "link": link, "section": "top"})

    # 하단 뉴스 10개 (li.newsList 내 a 태그 10개)
    bottom_section = soup.select("li.newsList")
    if bottom_section:
        # li.newsList가 여러 개일 수 있으니 모두 돌려보기
        bottom_links = []
        for li in bottom_section:
            bottom_links.extend(li.select("a[title]"))
        # 중복 제거(같은 a가 여러 개일 수 있음)
        seen = set()
        unique_bottom_links = []
        for a in bottom_links:
            if a["href"] not in seen:
                seen.add(a["href"])
                unique_bottom_links.append(a)
        for a in unique_bottom_links[:10]:  # 최대 10개
            title = a["title"]
            link = a["href"]
            news_results.append({"title": title, "link": link, "section": "bottom"})

    return news_results


if __name__ == "__main__":
    # 예: 1페이지 URL (날짜별로 페이지 번호 바꿔가면서 반복 크롤링 가능)
    url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&page=1"
    news = get_news_from_page(url)

    print(f"총 {len(news)}개 뉴스 수집됨")
    for n in news:
        print(f"[{n['section']}] {n['title']}")
        print(f"👉 {n['link']}")
