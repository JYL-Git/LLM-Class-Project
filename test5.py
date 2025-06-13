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
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # original # 상단 뉴스 (li.newsList.top 여러 개)
        # original top_items = soup.select("li.newsList.top")
        # original # 하단 뉴스 (li.newsList 여러 개, 단 상단과 겹칠 수 있으므로 .top 없는 것만)
        # original bottom_items = [li for li in soup.select("li.newsList") if 'top' not in li.get('class', [])]
        # original
        # original combined_items = top_items + bottom_items

        news_results = []

        # 전체 뉴스 (li.newsList 내 a 태그)
        news_section = soup.select("li.newsList")
        if news_section:
            # li.newsList가 여러 개일 수 있으니 모두 돌려보기
            bottom_links = []
            for li in news_section:
                bottom_links.extend(li.select("a[title]"))
            # 중복 제거(같은 a가 여러 개일 수 있음)
            seen = set()
            unique_bottom_links = []
            for a in bottom_links:
                if a["href"] not in seen:
                    seen.add(a["href"])
                    unique_bottom_links.append(a)
            for a in unique_bottom_links[:20]:  # 최대 10개
                title = a["title"]
                link = a["href"]
                news_results.append({"title": title, "link": link, "section": "bottom"})

        page_has_today_news = False

        for item in combined_items:
            date_tag = item.select_one("dd.articleSummary > span.wdate")
            if not title_tag or not date_tag:
                continue

            date_text = date_tag.get_text(strip=True)
            if not date_text.startswith(today_str):
                continue

            page_has_today_news = True

            results.append({
                "title": title,
                "link": "https://finance.naver.com" + link,
                "date": date_text
            })

        print(f"📄 Page {page}: {len(combined_items)}개 중 오늘 뉴스 {len([r for r in results if r['date'].startswith(today_str)])}개 수집됨")

        # 오늘 뉴스가 하나도 없는 페이지면 종료
        if not page_has_today_news:
            break

    driver.quit()
    return results


# def get_news_from_page(url):
#
#     driver.get(url)
#     time.sleep(3)  # 충분히 기다리기
#
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     driver.quit()
#
#     news_results = []
#
#     # 전체 뉴스 (li.newsList 내 a 태그)
#     bottom_section = soup.select("li.newsList")
#     if bottom_section:
#         # li.newsList가 여러 개일 수 있으니 모두 돌려보기
#         bottom_links = []
#         for li in bottom_section:
#             bottom_links.extend(li.select("a[title]"))
#         # 중복 제거(같은 a가 여러 개일 수 있음)
#         seen = set()
#         unique_bottom_links = []
#         for a in bottom_links:
#             if a["href"] not in seen:
#                 seen.add(a["href"])
#                 unique_bottom_links.append(a)
#         for a in unique_bottom_links[:20]:  # 최대 10개
#             title = a["title"]
#             link = a["href"]
#             news_results.append({"title": title, "link": link, "section": "bottom"})
#
#     return news_results

if __name__ == "__main__":
    news = get_today_news_by_url_loop(max_page=49)
    if news:
        print(f"\n✅ 오늘 뉴스 {len(news)}건 수집 완료\n")
        for n in news:
            print(f"[{n['date']}] {n['title']}")
            print(f"👉 {n['link']}\n")
    else:
        print("❌ 오늘 뉴스가 없습니다.")
