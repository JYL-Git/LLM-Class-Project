from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import time
import requests
import json

def get_last_page_number(soup):
    # 마지막 페이지 번호 찾기
    navi = soup.select("table.Nnavi td a")
    page_numbers = []
    for a in navi:
        if 'page=' in a['href']:
            page = int(a['href'].split('page=')[-1])
            page_numbers.append(page)
    return max(page_numbers) if page_numbers else 1
    # return 1


def get_news_content(url):
    # 본문 내용 가져오기
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code != 200:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")

        # 새 구조에 맞는 셀렉터 사용
        content_area = soup.select_one("div#newsct_article article#dic_area")
        if not content_area:
            return ""
        return content_area.get_text(strip=True, separator="\n")
    except Exception as e:
        print(f"[Error] {url} - {e}")
        return ""

def get_news_from_page(soup):
    news_results = []
    bottom_section = soup.select("li.newsList")

    seen = set()
    for li in bottom_section:
        for a in li.select("a[title]"):
            href = a.get("href")
            if href and href not in seen:
                seen.add(href)
                # 절대 URL이면 그대로 사용, 상대 URL이면 finance.naver.com을 기준으로 변환
                if href.startswith("http"):
                    full_url = href
                else:
                    full_url = urljoin("https://finance.naver.com", href)
                content = get_news_content(full_url)
                news_results.append({
                    "title": a["title"],
                    "link": full_url,
                    "section": "bottom",
                    "content": content  # 본문 추가

                })
    return news_results


def get_news_by_date(date_str):
    base_url = f"https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258&date={date_str}&page="

    # 셀레니움 드라이버 설정
    options = Options()
    options.add_argument("--headless")
    service = Service("/usr/local/bin/chromedriver")  # 사용자 환경에 맞게 경로 조정
    driver = webdriver.Chrome(service=service, options=options)

    # 1페이지 먼저 열어서 전체 페이지 수 확인
    driver.get(base_url + "1")
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    last_page = get_last_page_number(soup)
    print(f"{date_str} - 총 {last_page} 페이지 있음")

    all_news = []

    for page in range(1, last_page + 1):
        driver.get(base_url + str(page))
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        page_news = get_news_from_page(soup)
        all_news.extend(page_news)
        print(f"{page}페이지: {len(page_news)}개 수집됨")

    driver.quit()
    return all_news

if __name__ == "__main__":
    news_list = get_news_by_date("20250610")
    print(f"\n총 {len(news_list)}개 뉴스 수집 완료")
    for news in news_list[:3]:  # 미리보기
        print(f"- {news['title']}\n  👉 {news['link']}\n  📰 {news['content'][:100]}...\n")

    # ✅ JSON 파일로 저장
    with open("../data/raw_news.json", "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    print("📝 뉴스 데이터를 data/raw_news.json 파일로 저장 완료")