import os
from selenium import webdriver
# from webdriver_manager.chrome import ChromDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sys

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

datetype_today = datetime.today()
today = datetype_today.strftime('%Y.%m.%d')
print("----------- today: ", today)    
url_list = []
driver = webdriver.Chrome(r'D:\Profiles\20220170\django\interactive-word-cloud\FirstProject\firstproject\chromedriver.exe', options=options) 

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
    case = 4
    global today, url_list, url_dict, press_name, driver
    if case == 0:
        url_list = []
        press_name = ""
        curr_url = "https://sway.office.com/NnBPrJ8MQfFdSxHQ"
        print("----------- Sway target url: ", curr_url)
        driver.get(curr_url)
        driver.implicitly_wait(4)
        pause = driver.find_element(By.CLASS_NAME, 'autoplayControlButton.ButtonVE')
        pause.click()
        container = driver.find_element(By.XPATH, '/html/body/div/div[3]/div[3]/div/div[2]/div/div[1]/div/div/div[3]/div[2]/div/div/div')
        aTags = container.find_elements(By.TAG_NAME, 'a')
        print("a 태그 개수: ", len(aTags))
        for a in aTags:
            url_list.append(a.get_attribute('href'))
        print()

    elif case == 1:
        # 기사 html parsing : _cont = driver.find_element(By.ID, 'articletxt')
        kh_url_dict = dict()
        press_name = "경향신문"
        breaker = False
        url = "https://www.khan.co.kr/economy/it-electronic/articles?"
        url_len = len(url)
        # 경향신문 - 경제 - IT/가전 - 하루에 1~2페이지. page1부터.
        for page in range(1, 4):   
            curr_url = "https://www.khan.co.kr/economy/it-electronic/articles" + "?page=" + str(page)
            print("----------- 경향신문 target url: ", curr_url)
            driver.get(curr_url)
            driver.implicitly_wait(2)
            # cards = driver.find_elements(By.CLASS_NAME, 'story-card-container')
            ul = driver.find_element(By.ID, 'recentList')
            liTags_in_ul = ul.find_elements(By.TAG_NAME, 'li')
            for li in liTags_in_ul:
                # print(li.text)
                tit = li.find_element(By.CLASS_NAME, 'tit')
                aTag = tit.find_element(By.TAG_NAME, 'a')

                article_title = aTag.text
                article_href = aTag.get_attribute('href')
                lastSlash = article_href.rindex("/")
                date = article_href[lastSlash+1:lastSlash+9]
                article_date = date[:4] + "." + date[4:6] + "." + date[6:]
                # 오늘자 기사 필터링
                if article_date != today:
                    breaker = True
                    break
                print(article_date)     # 기사 발행일
                print(article_title)    # 기사 제목
                print(article_href)     # 기사 링크
                print()
                kh_url_dict[article_title] = article_href   # key=제목, value=링크인 dict로 저장
            
            if breaker == True:
                break
        print(kh_url_dict)
        url_dict = kh_url_dict
    elif case == 2:
        article_url_paid = "https://www.hankyung.com/it/article/202207011221i"
        article_url_free = "https://www.hankyung.com/it/article/202207134861g"
        driver.implicitly_wait(2)
        driver.get(article_url_paid)
        article_cont = driver.find_element(By.ID, 'articletxt')
        print("--- text: ", article_cont.text)
        print("--- text length: ", len(article_cont.text))
    elif case == 3:
        eco = "https://www.chosun.com/economy/economy_general/2022/07/26/ZJEMD7CO3JFD3MF6SJ2EUTSIPE/"
        it = "https://www.chosun.com/economy/tech_it/2022/07/26/IPV4QDI2TVE4BLZNJ6FKPQYZMI/"
        header = "https://www.chosun.com/economy/"

        start = it.index('/', len(header))
        print(start)
        print(it[start + 1:])
    else:   
        driver.implicitly_wait(20)
        print('------------기사 제목, 발행 신문사------------')

        url = 'https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105'
        driver.get(url)
    return

if __name__ == "__main__":
    main()