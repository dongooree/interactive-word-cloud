import requests
from bs4 import BeautifulSoup
from datetime import datetime

today = datetime.today().strftime('%Y.%m.%d')
print("----------- today: ", today)    
hk_url_list = []

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
    global hk_url_list, today
    list_href = []
    breaker = False
    url = "https://www.hankyung.com/it?date=" + today
    liTags_in_ul = [] 
    # 한경 - 하루에 4페이지 정도 올라올 것으로 가정하고 범위 설정. (cf. view상 1페이지는 page=0)
    for page in range(1, 5):    # 한경 IT섹션은 page 1부터 시작
        curr_url = url + "&page=" + str(page)
        raw = requests.get(curr_url, verify=False)

        print("----------- 한국경제 target url: ", curr_url)

        result = requests.get(curr_url, verify=False)
        soup = BeautifulSoup(result.content, "html.parser", from_encoding='utf-8')

        news_uls = soup.find_all("ul", class_="list_basic")
        # print(news_uls)
        
        for ul in news_uls:
            lis_in_ul = ul.find_all("li")
            liTags_in_ul.append(lis_in_ul)

    for liTags in liTags_in_ul:
        for li in liTags:
            # 한경은 url에 date쿼리 있으므로 날짜검사 생략
            article = li.find("div", class_="article").find("h3", class_="tit")
            article_href = article.find("a")["href"]
            article_title = article.find("a").get_text()
            # .find("h3", class_="tit").find("a")["href"]
            # article = article.find("h3", class_="tit")
            # article = article.find("span", class_="time").get_text()
            print(article_href)     # 기사 링크
            print(article_title)    # 기사 제목
            print()
    return

if __name__ == "__main__":
    main()