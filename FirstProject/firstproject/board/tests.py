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



# 한 기사 parsing
def makeAll(url):
    start = time.time()
    try:
        driver.get(url)
    except TimeoutException:
        driver.execute_script("window.stop();")
    print('Time consuming:', time.time() - t)

    # from selenium.webdriver.common.by import By
    if 'etnews' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.CLASS_NAME, 'article_txt')
    elif 'mk.co.kr' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.CLASS_NAME, 'art_txt')
    elif 'hankyung' in url : 
        # time.sleep(4)
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.ID, 'articletxt')
    elif 'naver' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.CLASS_NAME, '_article_content')
    elif 'joongang' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.ID, 'article_body')
    elif 'seoul.co.kr' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.ID, 'atic_txt1')
    elif 'khan.co.kr' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.ID, 'articleBody')
    elif 'segye.com' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.ID, 'article_txt')
    elif 'chosun' in url : 
        driver.implicitly_wait(30)
        _cont = driver.find_element(By.CLASS_NAME, 'article-body')
    else :
        _cont = driver.find_element(By.CLASS_NAME, '_article_content')
    end = time.time()
    print(f"{end - start:.5f} sec\t\t" + str(len(_cont.text)) + " 자")
    print(_cont.size)
    print('*****')
    return _cont.text

######### fetch -> df_to_json -> view로 분리
def fetch_cs(request):
    global today, url_dict, press_name, df
    datestr = time.strftime("%Y%m%d")
    cs_url_dict = dict()
    all_keywords = []
    dict_keywords = []
    source_keywords = defaultdict(list)
    press_name = "조선일보"
    breaker = False    
    url = "https://www.chosun.com/economy/tech_it/"
    header = "https://www.chosun.com/economy/"
    # 조선일보 - 테크 - 하루에 최대 3페이지 정도 올라올 것으로 가정하고 범위 설정. (cf. view상 1페이지는 page=0)
    # selenium driver 설정
    # driver.implicitly_wait(20)

    for page in range(1, 4):       # 조선일보 page 1부터 시작 
        curr_url = url + "?page=" + str(page)             
        print("----------- Batch 조선일보 target url: ", curr_url)    
        driver.implicitly_wait(20)
        driver.get(curr_url)
        # time.sleep(2)

        # driver.implicitly_wait(10) 
        wait = WebDriverWait(driver, 30)
        
        # wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'story-card__headline-container')))
        
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'story-card__headline-container')))
        # WebDriverWait(driver, 100).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'story-feed')))
        cards = driver.find_elements(By.CLASS_NAME, 'story-card__headline-container')

        for card in cards:       
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))
            aTag = card.find_element(By.TAG_NAME, 'a')

            article_title = aTag.find_element(By.TAG_NAME, 'span').text
            article_href = aTag.get_attribute('href')
            print(article_title)
            startIndex = article_href.index('/', len(header))

            date = article_href[startIndex+1:startIndex+11]
            article_date = date.replace('/', '.')
            print(article_date)
            # 오늘자 기사 필터링
            if article_date != today:
                breaker = True
                break
            # print(article_date)     # 기사 발행일
            # print(article_title)    # 기사 제목
            # print(article_href)     # 기사 링크
            # 오늘자 기사임을 확인 후 본문까지 가져와서 Data frame으로 저장
            aTag.send_keys(Keys.CONTROL + "\n")
            time.sleep(2)

            driver.switch_to.window(driver.window_handles[-1])  #새로 연 탭으로 이동
            article_content = makeAll(article_href)     
            if article_content == "":
                print(article_title, " 는 유료 기사입니다. ----------- ")

            # print(article_content)  # 기사 본문
            else:
                df = df.append({'press_name':press_name,
                    'article_date':article_date,
                    'article_title':article_title,
                    'article_href':article_href,
                    'article_content':article_content},
                    ignore_index=True)

            # 드라이버 닫고 처음 탭으로 돌아가기
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            # cs_url_dict[article_title] = article_href   # key=제목, value=링크인 dict로 저장
        
        if breaker == True:
            break

    driver.close()
    print("======== df to json ======= \n", df)
    output_path = r"D:\Profiles\20220170\Desktop\뉴스레터\today_news_csv"
    timestr = time.strftime("%Y%m%d")
    df.to_csv(path.join(output_path, press_name + '_' + timestr + '.csv'), header=True, index=True, encoding="utf-8-sig")
    # url_dict = cs_url_dict

    df_to_json(press_name, df)

    return HttpResponse('<h3>CSV & JSON files have been successfully generated.<br>Check your output file directory: ' 
        + output_path
        + '</h3>')



def wordcloud_cs(request):
    global stopwords, url_list, url_dict, press_name
    press_name = "조선일보"
    return wordcloud_view(request, press_name)
