import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

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
    global today, url_list, url_dict, press_name
    url_list = []
    mk_url_list = []
    mk_url_dict = dict()
    press_name = "매일경제"
    breaker = False
    url = "https://www.mk.co.kr/news/it/internet/"
    # url = "https://www.mk.co.kr/news/it/?page=1"

    datetype_today = datetime.strptime(today, "%Y.%m.%d")
    # 매경 - 하루에 4페이지 정도 올라올 것으로 가정하고 범위 설정. (cf. view상 1페이지는 page=0)
    for page in range(4):
        curr_url = "https://www.mk.co.kr/news/it/internet/?page=" + str(page)
        print("----------- 매일경제 target url: ", curr_url)
        result = requests.get(curr_url, verify=False)
        soup = BeautifulSoup(result.content, "html.parser", from_encoding='utf-8')
        # list_href = get_mk_href(soup)

        # soup에 저장되어 있는 각 기사에 접근할 수 있는 href들을 담은 리스트를 반환

        for news in soup.find("div", class_="list_area").find_all("dl"):
            date = news.find("dd", class_="desc").find("span", class_="date")
            date = date.get_text()[:10]
            # 날짜 수동 입력해서 테스트 (리스트가 최신순 정렬 안돼있을 때도 있음)
            # c_today = '2022.07.04'
            # if date != c_today:
            article_date = datetime.strptime(date, "%Y.%m.%d")
            if datetype_today.day - article_date.day > 1:
            # if date != today: 
                breaker = True 
                break
            elif date == today:
                dt = news.find("dt", class_="tit")
                article_href = dt.find("a")["href"]
                article_title = dt.get_text()
                print(article_title)
                print(article_href)
                print()
                mk_url_dict[article_title] = article_href   # key=제목, value=링크 형식의 dict로 저장
                # mk_url_list.append(url)
                # print()
            
        if breaker == True:
            break
    
    print(mk_url_dict)
    # url_list = mk_url_list
    url_dict = mk_url_dict
    # return wordcloud_url(request, mk_url_list)
    return

if __name__ == "__main__":
    main()