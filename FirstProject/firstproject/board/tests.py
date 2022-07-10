from django.test import TestCase

# Create your tests here.


# 중앙일보 - 경제 - IT/과학
def crawling_today_ja(request):
    global today, url_list, url_dict, press_name
    url_list = []
    ja_url_list = []
    ja_url_dict = dict()
    press_name = "중앙일보"
    breaker = False
    url = "https://www.joongang.co.kr/money/science/"
    liTags_in_ul = [] 
    # 중앙 - 하루에 1~2페이지. 페이징이 스크롤(더보기) 형식. page1부터.
    for page in range(1, 4):   
        curr_url = "https://www.joongang.co.kr/money/science?page=" + str(page)
        print("----------- 중앙일보 target url: ", curr_url)
        result = requests.get(curr_url, verify=False)
        soup = BeautifulSoup(result.content, "html.parser", from_encoding='utf-8')
        section = soup.find("ul", class_="story_list")
        news_cards = section.find_all("div", class_="card_body")

        for card in news_cards:
            date = card.find("div", class_="meta").find("p", class_="date")
            date = date.get_text()[:10]
            # 날짜 수동 입력해서 테스트 (리스트가 최신순 정렬 안돼있을 때도 있음)
            # c_today = '2022.07.04'
            # if date != c_today:
            if date != today: 
                breaker = True 
                break
            # print(date)
            article = card.find("h2", class_="headline")
            article_title = article.find("a").get_text()
            article_href = article.find("a")["href"]
            # print(article_title, end="")    # 기사 제목
            # print(article_href)     # 기사 링크
            ja_url_dict[article_title] = article_href   # key=제목, value=링크인 dict로 저장
            # ja_url_list.append(article_href)
            # print()

        if breaker == True:
            break
    # url_list = ja_url_list
    url_dict = ja_url_dict
    # print("url list : ", url_list)
    # return wordcloud_url(request, ja_url_list)
    return wordcloud_url(request)



