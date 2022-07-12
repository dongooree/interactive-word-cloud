import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sys

datetype_today = datetime.today()
today = datetype_today.strftime('%Y.%m.%d')
print("----------- today: ", today)    
url_list = []

def get_href(soup):
    global today
    # soup에 저장되어 있는 각 기사에 접근할 수 있는 href들을 담은 리스트를 반환

    # dl = soup.find("dl", class_="article_list")

    # for dt in dl.find_all("dt", class_="tit"):
    #     print(dt.find("a").attrs)
    for news in soup.find("div", class_="list_area").find_all("dl"):
        date = news.find("dd", class_="desc").find("span", class_="date")
        date = date.get_text()[:10]

        if date != today:
            return 0
        dt = news.find("dt", class_="tit")
        url = dt.find("a")["href"]
        title = dt.get_text()
        # print(title)
        # print(url)

        url_list.append(url)

        # print(date)
        # print()

    return

def main():
    global se_url_list, today, url_list, url_dict, press_name
    url_list = []
    se_url_dict = dict()
    press_name = "서울신문"
    breaker = False
    url = "https://www.seoul.co.kr/news/newsList.php?section=it&date=" + today
    liTags_in_ul = [] 
    # 서울신문-경제-IT,인터넷 - 하루에 3개 정도 업로드되고 있음. 페이징은 (더보기) 스크롤 형식
    # for page in range(1, 5):    
    href_header = "https://www.seoul.co.kr"
    curr_url = "https://www.seoul.co.kr/news/newsList.php?section=it&date=" + today
    print("----------- 서울신문 target url: ", curr_url)
    result = requests.get(curr_url, verify=False)
    soup = BeautifulSoup(result.content.decode('utf-8', 'replace'), "html.parser")
    liTags = soup.find_all("li", class_="S20_List_article")

    for li in liTags:
        # 한경은 url에 date쿼리 있으므로 날짜검사 생략
        article = li.find("div", class_="tit")
        article_href = href_header + article.find("a")["href"]
        article_title = article.find("a").get_text()
        print(article_href)     # 기사 링크
        print(article_title)    # 기사 제목
        print()
        se_url_dict[article_title] = article_href   # key=제목, value=링크 형식의 dict로 저장
        # print()

    print(se_url_dict)
    url_dict = se_url_dict
    # return wordcloud_url(request, hk_url_list)
    return

if __name__ == "__main__":
    main()