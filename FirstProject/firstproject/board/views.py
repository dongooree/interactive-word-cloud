import itertools
from django.shortcuts import render
from django.http import HttpResponse
from .models import Curriculum
import os
from os import path
import string
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter, OrderedDict, defaultdict
from wordcloud import WordCloud,STOPWORDS
from tika import tika, parser
tika.TikaJarPath = r'D:\Profiles\20220170\AppData\Local\Temp'
# import PyPDF2
# import textract
from konlpy.tag import Okt
from PIL import Image
import numpy as np
import json
from itertools import islice
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import pickle
import re
from ckonlpy.tag import Twitter
from datetime import datetime

from soynlp.utils import DoublespaceLineCorpus
from soynlp.noun import LRNounExtractor_v2
from soynlp.word import WordExtractor
# nltk.download('gutenberg')
# nltk.download('maxent_treebank_pos_tagger')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')
import pandas as pd
import math

# df = pd.read_csv('./static/text/stopwords_KO2.csv', encoding="UTF-8") # encoding='cp949'
# df = pd.read_csv('./static/text/stopwords_KO2.csv', encoding='ISO-8859-1')
# # df.loc[-1] = '가'
# df.index = df.index + 1
# df = df.sort_index()
# df = df.rename(columns={'가': 'words'})

# 추가하고 싶은 Stopwords 입력 - 워드 클라우드에 반영
NewStopwords = ''
NewStopwords = set(NewStopwords.split(' '))
# idx = len(df.index)
# for word in NewStopwords :
#     if not (df['words']==word).any() : 
#         df.loc[idx] = word
#         idx += 1

# Create your views here.

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome('D:/Profiles/20220170/django/chromedriver.exe', options=options) 
driver = webdriver.Chrome('chromedriver.exe', options=options) 

t = time.time()
driver.set_page_load_timeout(10)

url_list = []

datetype_today = datetime.today()
today = datetype_today.strftime('%Y.%m.%d')

mk_url_list = []
hk_url_list = []
url_dict = dict()
ja_url_dict = dict()

press_name = ""

## 사용자 사전에 명사 등록
twitter = Twitter()
twitter.add_dictionary(['메타버스', 'DBMS'], 'Noun')

# 불용어 사전 - 파일 읽어서 등록
global stopwords
stopwords = set(STOPWORDS)
st_file_path = './static/text/stopwords_KO.txt'

with open(st_file_path, "r", encoding="UTF-8") as f:
    lines = f.read().splitlines()

for stw in lines:
    stopwords.add(stw)


def home(request):
    return render(
        request, 'board/home.html'
    )

def word_score(score):
    return ((score.cohesion_forward * 10) * (math.exp(score.right_branching_entropy + 0.5)))

### 매일경제 IT/과학 -> IT/인터넷 오늘자 기사 크롤링
datetype_today = datetime.today()
today = datetype_today.strftime('%Y.%m.%d')
print("-------------------------------------- today: ", today)    

def get_mk_href(soup):
    global datetype_today, today, url_list, mk_url_list
    # soup에 저장되어 있는 각 기사에 접근할 수 있는 href들을 담은 리스트를 반환

    # dl = soup.find("dl", class_="article_list")

    # for dt in dl.find_all("dt", class_="tit"):
    #     print(dt.find("a").attrs)
    for news in soup.find("div", class_="list_area").find_all("dl"):
        date = news.find("dd", class_="desc").find("span", class_="date")
        date = date.get_text()[:10]
        
        # 날짜 수동 입력해서 테스트 (리스트가 최신순 정렬 안돼있을 때도 있음)
        # c_today = '2022.07.04'
        # if date != c_today:
        if date != today:  
            break
        dt = news.find("dt", class_="tit")
        url = dt.find("a")["href"]
        title = dt.get_text()
        # print(title)
        # print(url)

        mk_url_list.append(url)
        # print(mk_url_list)
        # print(date)
        # print()

    return mk_url_list

# 매일경제
def crawling_today_mk(request):
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
            # today = '2022.07.10'
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
                # print(article_title)
                # print(article_href)
                # print()
                mk_url_dict[article_title] = article_href   # key=제목, value=링크 형식의 dict로 저장
                # mk_url_list.append(url)
                # print()
            
        if breaker == True:
            break
    
    # print(mk_url_list)
    # url_list = mk_url_list
    url_dict = mk_url_dict
    return wordcloud_url(request)

# 한국경제
def crawling_today_hk(request):
    global hk_url_list, today, url_dict, press_name
    hk_url_dict = dict()
    press_name = "한국경제"
    breaker = False
    url = "https://www.hankyung.com/it?date=" + today
    # 한경 - 하루에 4페이지 정도 올라올 것으로 가정하고 범위 설정. (cf. view상 1페이지는 page=0)
    for page in range(1, 5):    # 한경 IT섹션은 page 1부터 시작
        curr_url = url + "&page=" + str(page)
        # print("----------- 한국경제 target url: ", curr_url)
        result = requests.get(curr_url, verify=False)
        soup = BeautifulSoup(result.content, "html.parser", from_encoding='utf-8')
        section = soup.find("ul", class_="news-list")
        # liTags_in_ul = section.find_all("li")

        conts = section.find_all("div", class_="txt-cont")
        for cont in conts:
            date = cont.find("span", class_="txt-date")
            date = date.get_text()[:10]
            # 날짜 수동 입력해서 테스트
            # c_today = '2022.07.04'
            # if date != c_today:
            if date != today: 
                breaker = True 
                break
            article = cont.find("h3", class_="news-tit")
            article_title = article.find("a").get_text()
            article_href = article.find("a")["href"]
            # print(article_title)    # 기사 제목
            # print(article_href)     # 기사 링크
            # print(date)             # 기사 날짜
            # print()
            hk_url_dict[article_title] = article_href   # key=제목, value=링크인 dict로 저장

        if breaker == True:
            break

    print(hk_url_dict)
    url_dict = hk_url_dict
    return wordcloud_url(request)

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

# 서울신문 - 경제 - IT/인터넷
def crawling_today_se(request):
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
    # print(liTags)
    for li in liTags:
        # 서울신문은 url에 date쿼리 있으므로 날짜검사 생략
        article = li.find("div", class_="tit")
        if article == None:
            break
        article_href = href_header + article.find("a")["href"]
        article_title = article.find("a").get_text()
        # print(article_href)     # 기사 링크
        # print(article_title)    # 기사 제목
        # print()
        se_url_dict[article_title] = article_href   # key=제목, value=링크 형식의 dict로 저장
        # print()

    print(se_url_dict)
    url_dict = se_url_dict
    return wordcloud_url(request)

def crawling_today_sg(request):
    global today, url_dict, press_name
    sg_url_dict = dict()
    press_name = "세계일보"
    breaker = False
    url = "https://www.segye.com/newsList/0101030900000"
    # href_header = "https://www.segye.com"
    # selenium driver 설정
    driver.implicitly_wait(2)
        
    # 세계일보 Biz - IT과학 - 하루에 최대 3페이지 정도 올라올 것으로 가정하고 범위 설정. (cf. view상 1페이지는 page=0)
    for page in range(3):             
        # driver.implicitly_wait(2)
        curr_url = url + "?page=" + str(page)
        print("----------- 세계일보 target url: ", curr_url)
        driver.get(curr_url)
        
        ul = driver.find_element(By.CLASS_NAME, 'listBox')
        liTags_in_ul = ul.find_elements(By.TAG_NAME, 'li')
        for li in liTags_in_ul:
            date = li.find_element(By.CLASS_NAME, 'date')
            date = date.text[:10].replace('-', '.')
            # print(date)
            # 날짜 수동 입력해서 테스트
            # c_today = '2022.07.04'
            # if date != c_today:
            if date != today: 
                breaker = True 
                break
            aTag = li.find_element(By.TAG_NAME, 'a')
            article_title = aTag.find_element(By.CLASS_NAME, 'tit').text
            article_href = aTag.get_attribute('href')
            # print(article_title)    # 기사 제목
            # print(article_href)     # 기사 링크
            # print()
            sg_url_dict[article_title] = article_href   # key=제목, value=링크인 dict로 저장

        if breaker == True:
            break

    # print(sg_url_dict)
    url_dict = sg_url_dict
    return wordcloud_url(request)


def crawling_today_cs(request):
    global today, url_dict, press_name
    cs_url_dict = dict()
    press_name = "조선일보"
    breaker = False    
    url = "https://www.chosun.com/economy/tech_it/"
    # result = requests.get(curr_url, verify=False)
    # soup = BeautifulSoup(result.content.decode('utf-8', 'replace'), "html.parser")
    # cards = soup.find("div", id="main")
    # print(cards)

    # 조선일보 - 테크 - 하루에 최대 3페이지 정도 올라올 것으로 가정하고 범위 설정. (cf. view상 1페이지는 page=0)
    # selenium driver 설정
    driver.implicitly_wait(2)

    for page in range(1, 4):       # 조선일보 page 1부터 시작 
        curr_url = url + "?page=" + str(page)             
        print("----------- 조선일보 target url: ", curr_url)    
        driver.implicitly_wait(2)
        driver.get(curr_url)

        # cards = driver.find_elements(By.CLASS_NAME, 'story-card-container')
        cards = driver.find_elements(By.CLASS_NAME, 'story-card__headline-container')
        for card in cards:
            aTag = card.find_element(By.TAG_NAME, 'a')

            article_title = aTag.find_element(By.TAG_NAME, 'span').text
            article_href = aTag.get_attribute('href')
            date = article_href[(len(url)):(len(url))+10]
            article_date = date.replace('/', '.')
            # 오늘자 기사 필터링
            if article_date != today:
                breaker = True
                break
            # print(article_date)     # 기사 발행일
            # print(article_title)    # 기사 제목
            # print(article_href)     # 기사 링크
            # print()
            cs_url_dict[article_title] = article_href   # key=제목, value=링크인 dict로 저장
        
        if breaker == True:
            break

    # print(cs_url_dict)
    url_dict = cs_url_dict
    return wordcloud_url(request)

def crawling_today_kh(request):
    global today, url_dict, press_name
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

        ul = driver.find_element(By.ID, 'recentList')
        liTags_in_ul = ul.find_elements(By.TAG_NAME, 'li')

        for li in liTags_in_ul:
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
            # print(article_date)     # 기사 발행일
            # print(article_title)    # 기사 제목
            # print(article_href)     # 기사 링크
            # print()
            kh_url_dict[article_title] = article_href   # key=제목, value=링크인 dict로 저장
        
        if breaker == True:
            break

    print(kh_url_dict)
    url_dict = kh_url_dict
    return wordcloud_url(request)


def read_file_textract(filepath):
    text = textract.process(filepath)
    return text.decode("utf-8") 

# Method 2. PyPDF
def read_file_pypdf(filepath):
    pdfFileObj = open(filepath,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    num_pages = pdfReader.numPages
    text = ""
    # Read all the pages
    for pg in range(num_pages):
        page = pdfReader.getPage(pg)
        text += page.extractText()
    return text

# Read file using any of the pdf readers
def read_file(filepath, use_method = 'textract'):
    
    text = ""
    if not os.path.isfile(filepath):
        print(f'Invalid file:{filepath}')
    else:
        if use_method == 'textract':
            return read_file_textract(filepath)
        elif use_method == 'pypdf':
            return read_file_pypdf(filepath)
        else:
            print('Invalid method to read file. Supported formats: "textract" or "pypdf".')
    
    return text

def extract_keywords(text, ignore_words = [],
                     min_word_length = 0,
                     ignore_numbers = True,
                     ignore_case = True):
    # Remove words with special characters
    filtered_text = ''.join(filter(lambda x:x in string.printable, text))
    
    # Create word tokens from the text string
    tokens = word_tokenize(filtered_text)
    
    # List of punctuations to be ignored 
    punctuations = ['(',')',';',':','[',']',',','.','--','-','#','!','*','"','%']
    
    # Get the stopwords list to be ignored
    stop_words = stopwords.words('english')

    # Convert ignore words from user to lower case
    ignore_words_lower = [x.lower() for x in ignore_words]
    
    # Combine all the words to be ignored
    all_ignored_words = punctuations + stop_words + ignore_words_lower
    
    # Get the keywords list
    keywords = [word for word in tokens \
                    if  word.lower() not in all_ignored_words
                    and len(word) >= min_word_length]    

    # Remove keywords with only digits
    if ignore_numbers:
        keywords = [keyword for keyword in keywords if not keyword.isdigit()]

    # Return all keywords in lower case if case is not of significance
    if ignore_case:
        keywords = [keyword.lower() for keyword in keywords]
    
    return keywords

# Create Word cloud
def create_word_cloud(keywords, maximum_words = 100, bg = 'white', cmap='Dark2',
                     maximum_font_size = 256, width = 3000, height = 2000,
                     random_state = 42, fig_w = 15, fig_h = 10, output_filepath = None):
    
    # Convert keywords to dictionary with values and its occurences
    word_could_dict=Counter(keywords)

    wordcloud = WordCloud(background_color=bg, max_words=maximum_words, colormap=cmap, 
                          stopwords=STOPWORDS, max_font_size=maximum_font_size,
                          random_state=random_state, 
                          width=width, height=height).generate_from_frequencies(word_could_dict)
    
    plt.figure(figsize=(fig_w,fig_h))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    if output_filepath:
        plt.savefig(output_filepath, bbox_inches='tight')
    plt.show()
    plt.close()
  
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
        _cont = driver.find_element(By.CLASS_NAME, 'article_txt')
    elif 'mk.co.kr' in url : 
        _cont = driver.find_element(By.CLASS_NAME, 'art_txt')
    elif 'hankyung' in url : 
        time.sleep(2)
        _cont = driver.find_element(By.ID, 'articletxt')
    elif 'naver' in url : 
        _cont = driver.find_element(By.CLASS_NAME, '_article_content')
    elif 'joongang' in url : 
        _cont = driver.find_element(By.ID, 'article_body')
    elif 'seoul.co.kr' in url : 
        _cont = driver.find_element(By.ID, 'atic_txt1')
    elif 'khan.co.kr' in url : 
        _cont = driver.find_element(By.ID, 'articleBody')
    elif 'segye.com' in url : 
        _cont = driver.find_element(By.ID, 'article_txt')
    elif 'chosun' in url : 
        _cont = driver.find_element(By.CLASS_NAME, 'article-body')
    else :
        _cont = driver.find_element(By.CLASS_NAME, '_article_content')
    end = time.time()
    print(f"{end - start:.5f} sec\t\t" + str(len(_cont.text)) + " 자")
    print(_cont.size)
    print('*****')
    time.sleep(2)
    return _cont.text

# Views
def main(request):
    # 한글 출력 위한 폰트 설치
    # sys_font = fm.findSystemFonts()
    # [f for f in sys_font if 'Nanum' in f]
    global url_list
    global twitter
    global stopwords
    font_path = r'D:\\Profiles\\20220170\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumGothic.ttf'
    font_name = fm.FontProperties(fname=font_path, size=10).get_name()
    # print(font_name)
    plt.rc('font', family=font_name)
    plt.rcParams["font.family"] = font_name
    # fm._rebuild()

    # print('------------발행내용------------')

    wordTxt = ''

    for url in url_list:
        wordTxt += makeAll(url)

    # 한달치 기사로 text 만들기
    # wordTxt = open('./static/text/article.txt', "r", encoding="UTF-8").read()

    # print(wordTxt)

    # 심볼 제거
    wordTxt = re.compile(r'[^\w\s]').sub(' ',wordTxt)
    # 한글만 추출
    korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
    parseText= re.sub(korean, '', wordTxt)

    # nltk 함수로 영어 분리
    en_word = nltk.word_tokenize(parseText)
    tokens_pos = nltk.pos_tag(en_word)
    # print(tokens_pos)
    en_Nwords = []
    for word, pos in tokens_pos :
        if 'NN' in pos or 'JJ' in pos:
            en_Nwords.append(word)
    # print(en_Nwords)

    # Okt 함수를 이용해 형태소 분석
    # okt = Okt()

    naword =[]
    _naword =[]
    # _naword = okt.pos(wordTxt)

    _naword = twitter.pos(wordTxt)
        
    for word, tag in _naword:
        if tag in ['Noun','Adjective']:
            naword.append(word)
    # print(naword)

    for word in en_Nwords:
        naword.append(word)
    # print(naword)

    # 한국어 + 영어 명사 추출 후 불용어 제거
    # custom stopwords
    stw_list = []
    if len(stw_list) > 0:
        for c_stw in stw_list:
            stopwords.add(c_stw)

    naword = [word for word in naword if (not word in stopwords) and len(word) > 1]

    # Counter로 빈도 집계
    counts = Counter(naword)
    dict_keywords = counts.most_common(100)
    
    mask = np.array(Image.open('./static/image/Circle.JPG'))

    wc = WordCloud(stopwords=stopwords,
                # font_path=font_name, 
                font_path=r"D:\Profiles\20220170\Downloads\nanum-all\나눔 글꼴\나눔고딕\NanumFontSetup_TTF_GOTHIC\NanumGothic.ttf", 
                mask = mask, background_color='white', colormap = 'Set1',
                max_words=100, max_font_size=125, random_state=87, 
                width=400, height=400)# mask.shape[0]

    # wc.generate_from_frequencies(dict_keywords)    
    wc.generate_from_frequencies(dict(dict_keywords))
    
    # wc.generate(wordTxt)
    fig = plt.figure(figsize = (10,10))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis('off')
    # plt.show()
    
    output_path = r"D:\Profiles\20220170\Desktop\뉴스레터\wc images"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    wc.to_file(path.join(output_path, 'wc_' + timestr + '.png'))
    # plt.close()

    return HttpResponse('<h3>Word Cloud has been successfully generated. <br> Check your output file directory: ' 
        + output_path
        + '</h3>')
    
# 기사 wc
def wordcloud_url(request):
    global stopwords, url_list, url_dict, press_name
    urls = url_list
    
    wFileName = r'D:\\Profiles\\20220170\\Desktop\\뉴스레터\\DXletter_contents\\' + today + '.txt'
    if os.path.isfile(wFileName):    
        os.remove(wFileName)
    all_keywords = []
    dict_keywords = []
    # 
    # --- list 버전
    # print("기사 리스트: ", urls)
    # print("기사 개수: ", len(urls))
    source_keywords = defaultdict(list)
    # test_urls = ['https://www.hankyung.com/it/article/202207069766Y', 'https://www.hankyung.com/it/article/202207069745i']
    # for url in test_urls:
    # for url in urls:

    # --- dict 버전 (제목:링크)
    newsCount = len(url_dict.items())
    print("기사 리스트: ", url_dict.values())
    print("기사 개수: ", newsCount)
    
    # source_keywords = defaultdict(dict)
    for title, url in url_dict.items():
    # for url in urls:
        # url에서 텍스트를 추출
        print(f'Parsing url: {url}')
        wordTxt = makeAll(url)     # 가공 전 기사 text를 return
        if wordTxt == "":
            print(url, " 는 유료 기사입니다. ----------- ")
            continue
        # driver.close()
        # 심볼 제거
        wordTxt = re.compile(r'[^\w\s]').sub(' ', wordTxt)
        # 한글만 추출
        korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
        parseText= re.sub(korean, '', wordTxt)

        # nltk 함수로 영어 분리
        en_word = nltk.word_tokenize(parseText)
        tokens_pos = nltk.pos_tag(en_word)
        # print(tokens_pos)
        en_Nwords = []
        for word, pos in tokens_pos :
            if 'NN' in pos or 'JJ' in pos:
                en_Nwords.append(word)
        if 'CD' in pos : 
            tmpPattern = re.compile("[0-9][A-Z]")
            if tmpPattern.match(word) : 
                en_Nwords.append(word)
        print(en_Nwords)
        # print(en_Nwords)

        # Okt 함수를 이용해 형태소 분석
        okt = Okt()
        # nouns = okt.nouns(contents) # 명사만 추출
        # words = [n for n in nouns if len(n) > 1] # 단어의 길이가 1개인 것은 제외

        naword =[]
        _naword =[]
        _naword = okt.pos(wordTxt)
        # _naword = twitter.pos(wordTxt)
        for word, tag in _naword:
            if tag in ['Noun','Adjective']:
                naword.append(word)

        for word in en_Nwords:
            naword.append(word)

        # Stopwords Customizing
        target_stop = ['https', 'all', 'article', 'Copyright', 'print', 'etnews', 'mnews', 'news', 'Segye', 'segye', 'hankyung', 'joongang']
        for t in target_stop:
            stopwords.add(t)

        ####### 신조어/복합어 따로 지정해서 관련 단어 추가 및 제거하기
        #### 복합어 추가 시작
        # contents.txt 파일 생성 wordTxt
        # with open(wFileName, 'a+', encoding='utf-8') as saveTxt:
        with open(wFileName, 'w+', encoding='utf-8') as saveTxt:
            saveTxt.write(wordTxt)
        
        # corpus_path = './static/text/contents.txt'
        # sents = DoublespaceLineCorpus(corpus_path, iter_sent=True)
        sents = DoublespaceLineCorpus(wFileName, iter_sent=True)
        
        noun_extractor = LRNounExtractor_v2(verbose=True)
        nouns = noun_extractor.train_extract(sents)
        # print(nouns)

        list(noun_extractor._compounds_components.items())[:100]
        # naword = [word for word in naword if (not word in stopwords) and len(word) > 1]

        #### START 신조어 추가
        wordTxtList = [ sentence for sentence in wordTxt.split('\n') if sentence ]

        # 5번 이상 언급된 단어들 중 일부 추출
        word_extractor = WordExtractor(min_frequency=5,
                                    min_cohesion_forward = 0.05,
                                    min_right_branching_entropy = 0.0)

        word_extractor.train(wordTxtList) # list of str or like
        words =word_extractor.extract()

        for word in words : 
            if len(word) < 2:
                continue
            subword = word[:-1]
            if not subword in words:
                continue
            if(words[word].leftside_frequency == words[subword].leftside_frequency) : 
                tmp = words[subword].cohesion_forward + words[word].cohesion_forward
                if word in stopwords : # 스탑워드에 있는 단어는 낮은 점수 부여
                    # print(word)
                    tmp *= -10
                words[word] = words[word]._replace(cohesion_forward = 10 + tmp)
                words[subword] = words[word]._replace(cohesion_forward = 0)

        # 내림차순 점수와 단어 출력
        print('기사: ', title)
        print('단어   (빈도수, cohesion, branching entropy)\n')
        for word, score in sorted(words.items(), key=lambda x:word_score(x[1]), reverse=True)[:100]:
            print('%s     (%d, %.3f, %.3f)' % (
                word,
                score.leftside_frequency,
                score.cohesion_forward,
                score.right_branching_entropy
                )
            )

        # naword에 단어 추가
        for word in list(noun_extractor._compounds_components) : # 복합어
            if word in naword : break
            naword.append(word)
            # print('+' + word)

        # print('********')

        #
        for word in sorted(words.items(), key=lambda x:word_score(x[1]), reverse=True)[:30]: # 신조어 추정 단어 개수 지정
          # if word[0] in naword : break
            if len(word[0]) > 1 and ( word[0][-2:] == '에서' or word[0][-2:] == '이다' or word[0][-2:] == '으로' ) : 
                naword.append(word[0][:-2])
                print('++' + str(word[0][:-2]))
                continue
            if ((word[0][-1:]) == '은') or ((word[0][-1:]) == '는') or ((word[0][-1:]) == '을') or ((word[0][-1:]) == '를') or ((word[0][-1:]) == '하') or ((word[0][-1:]) == '의') :
                # if word[0][-1:] in naword : break
                naword.append(word[0][:-1])
                print('++' + str(word[0][:-1]))
            else : 
                naword.append(word[0])
                print('+' + str(word[0]))

        # 사용자 단어 추가
        # addWords = "메타버스 블록체인 노코드 스마트팩토리 얼굴인식 음성인식 LG유플러스 디지털트윈 디지털전환 디지털트랜스포메이션"
        # addWords += " LGCNS LG화학 LG에너지솔루션 LG이노텍 카카오엔터프라이즈 SK텔레콤 비즈니스 삼성SDS"
        # addWords = set(addWords.split(' '))
        # for word in addWords:
        #     # if word in naword : break
        #     naword.append(word)
        #     print('+' + str(word))

        # 파일로 저장 후 다운로드하여 이름 변경하고 사용하기.
        # 2번 실행 시 중복으로 입력되니 삭제 후 1회만 실행 필요.
        # df.to_csv("./static/text/stopwords_KO2.csv", index=False, encoding="utf-8-sig")

        naword = [word for word in naword if (not word in stopwords) and len(word) > 1]

        # 중복제거된 단어들 - 원본 filename을 저장
        distinct_words = set(naword)
        for word in distinct_words:
            # --- list 버전
            # source_keywords[word].append(url)
            # --- dict 버전
            source_keywords[word].append({title:url})
            
        # 한 기사 다 읽은 뒤 all keywords에 추가
        all_keywords.extend(naword)
               
    # driver.quit()
    # print(source_keywords)
    dict_keywords = Counter(all_keywords) # 위에서 얻은 words를 처리하여 단어별 빈도수 형태의 딕셔너리 데이터를 구함

    # 복합어에 점수 더하기
    for word in dict_keywords.keys():
        for e in range(1, len(word)) : 
            subword = word[:e]
            if subword in dict_keywords.keys() :
                dict_keywords[word] = (dict_keywords[word] + dict_keywords[subword]*0.7)
                dict_keywords[subword] *= 0.3
            subword = word[-e:]
            if subword in dict_keywords.keys() :
                dict_keywords[word] = (dict_keywords[word] + dict_keywords[subword]*0.7)
                dict_keywords[subword] *= 0.3

    # count 임의 조정
    # dict_keywords['개인정보보호'] /= 10
    # dict_keywords['스마트공장지원'] /= 4
    # dict_keywords['공장운영'] /= 4

    #### END 복합어, 신조어 추가

    ### dict_keywords
    # 빈도로 내림차순 정렬
    dict_keywords = OrderedDict(sorted(dict_keywords.items(), key = lambda item: item[1], reverse = True))
    # dict_keywords = dict(islice(dict_keywords.items(), 200))
    dict_keywords = dict(islice(dict_keywords.items(), 100))
    
    # dict_keywords = dict_keywords.most_common(100)
    
    dict_keywords = json.dumps(dict_keywords, indent=4, ensure_ascii=False)
    source_keywords = json.dumps(source_keywords, indent=4, ensure_ascii=False)
    # print("원래 dict_keywords: ", dict_keywords)
    # print("------------------------------------")
    # print("path붙인 source_keywords: ", source_keywords)
    # print("----- 자른 후: ", len(dict_keywords))

    return render(
        request, 'board/wordcloud_url.html',
        { 'dict': dict_keywords,
         'source_dict' : source_keywords,
         'news_count' : newsCount,
         'press_name' : press_name
        }
    )

def wordcloud_pdf(request):
    # Multiple pdfs in a directory
    docs_path = './static/pdf'
    all_keywords = []
    source_keywords = defaultdict(list)
    
    for filename in os.listdir(docs_path):
        filepath = os.path.join(docs_path, filename)
        
        # PDF 파일에서 텍스트를 추출
        print(f'Parsing file: {filename}')
    
        raw_pdf = parser.from_file(filepath) 
        contents = raw_pdf['content']       # PDF DRM 걸려있으면 못 읽음
        contents = contents.strip()

        # 심볼 제거
        wordTxt = re.compile(r'[^\w\s]').sub(' ', contents)
        # 한글만 추출
        korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
        parseText= re.sub(korean, '', wordTxt)

        # nltk 함수로 영어 분리
        en_word = nltk.word_tokenize(parseText)
        tokens_pos = nltk.pos_tag(en_word)
        # print(tokens_pos)
        en_Nwords = []
        for word, pos in tokens_pos :
            if 'NN' in pos or 'JJ' in pos:
                en_Nwords.append(word)
        # print(en_Nwords)

        # Okt 함수를 이용해 형태소 분석
        okt = Okt()
        # nouns = okt.nouns(contents) # 명사만 추출
        # words = [n for n in nouns if len(n) > 1] # 단어의 길이가 1개인 것은 제외

        naword =[]
        _naword =[]
        # _naword = okt.pos(wordTxt)
        _naword = twitter.pos(wordTxt)
        for word, tag in _naword:
            if tag in ['Noun','Adjective']:
                naword.append(word)
        # print(naword)

        for word in en_Nwords:
            naword.append(word)

        # Stopwords Customizing https
        target_stop = ['인쇄', '뉴스', 'https', 'all', 'article',
            'copyright', 'COPYRIGHT', 'print', 'etnews', 'mnews', 'news', '오전', '금지', 'rights', 'RIGHTS']
        for t in target_stop:
            stopwords.add(t)
        
        naword = [word for word in naword if (not word in stopwords) and len(word) > 1]

        # 중복제거된 단어들 - 원본 filename을 저장
        distinct_words = set(naword)
        for word in distinct_words:
            source_keywords[word].append(filename)
            # source_keywords[word].append(filepath)

        # 한 pdf 다 읽은 뒤 all keywords에 추가
        all_keywords.extend(naword)
               
    dict_keywords = Counter(all_keywords) # 위에서 얻은 words를 처리하여 단어별 빈도수 형태의 딕셔너리 데이터를 구함

    ### dict_keywords
    # 빈도로 내림차순 정렬
    dict_keywords = OrderedDict(sorted(dict_keywords.items(), key = lambda item: item[1], reverse = True))
    dict_keywords = dict(islice(dict_keywords.items(), 100))
    # print("********** all keywords **************")
    # print(dict_keywords)

    dict_keywords = json.dumps(dict_keywords, indent=4, ensure_ascii=False)
    source_keywords = json.dumps(source_keywords, indent=4, ensure_ascii=False)
    # print("원래 dict_keywords: ", dict_keywords)
    # print("------------------------------------")
    # print("path붙인 source_keywords: ", source_keywords)
    # print("----- 자른 후: ", len(dict_keywords))
    
    # dict_source_list
    return render(
        request, 'board/wordcloud_pdf.html',
        { 'dict': dict_keywords,
         'source_dict' : source_keywords
        }
    )

def insert(request):
    Curriculum(name='class1').save()
    Curriculum(name='class2').save()
    return HttpResponse('데이터 입력 완료')

def test(request):
    # return HttpResponse('접속이 잘 되네용')
    test = "메롱"
    return render(
        request, 'board/test.html',
        { 'str': test
        }
    )


# 뉴스레터 wc 이미지
def main_new(request):
    # 한글 출력 위한 폰트 설치
    # sys_font = fm.findSystemFonts()
    # [f for f in sys_font if 'Nanum' in f]
    global url_list, today
    global twitter
    global stopwords, df, NewStopwords, t, driver, options
    font_path = r'D:\\Profiles\\20220170\\AppData\\Local\\Microsoft\\Windows\\Fonts\\NanumGothic.ttf'
    font_name = fm.FontProperties(fname=font_path, size=10).get_name()
    # print(font_name)
    plt.rc('font', family=font_name)
    plt.rcParams["font.family"] = font_name
    # fm._rebuild()

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

    wFileName = r'D:\\Profiles\\20220170\\Desktop\\뉴스레터\\DXletter_contents\\' + today + '_main_new.txt'
    if os.path.isfile(wFileName):    
        os.remove(wFileName)

    # print('------------발행내용------------')

    wordTxt = ''

    for url in url_list:
        wordTxt += makeAll(url)

    # driver.quit()
    # 한달치 기사로 text 만들기
    # wordTxt = open('./static/text/article.txt', "r", encoding="UTF-8").read()

    # print(wordTxt)

    # 심볼 제거
    wordTxt = re.compile(r'[^\w\s]').sub(' ',wordTxt)
    # 한글만 추출
    korean = re.compile('[\u3131-\u3163\uac00-\ud7a3]+')
    parseText= re.sub(korean, '', wordTxt)

    # nltk 함수로 영어 분리
    en_word = nltk.word_tokenize(parseText)
    tokens_pos = nltk.pos_tag(en_word)
    # print(tokens_pos)
    en_Nwords = []
    for word, pos in tokens_pos :
        if 'NN' in pos or 'JJ' in pos:
            en_Nwords.append(word)
        if 'CD' in pos : 
            tmpPattern = re.compile("[0-9][A-Z]")
            if tmpPattern.match(word) : 
                en_Nwords.append(word)
    # print(en_Nwords)

    # Okt 함수를 이용해 형태소 분석
    okt = Okt()

    naword =[]
    _naword =[]
    _naword = okt.pos(wordTxt)

    # _naword = twitter.pos(wordTxt)
        
    for word, tag in _naword:
        if tag in ['Noun','Adjective']:
            naword.append(word)
    # print(naword)

    for word in en_Nwords:
        naword.append(word)
    # print(naword)

    #### 복합어 추가
    # contents.txt 파일 생성 wordTxt
    with open(wFileName, 'w', encoding='utf-8') as saveTxt:
        saveTxt.write(wordTxt)
     
    corpus_path = './static/text/contents.txt'
    sents = DoublespaceLineCorpus(corpus_path, iter_sent=True)
    
    noun_extractor = LRNounExtractor_v2(verbose=True)
    nouns = noun_extractor.train_extract(sents)
    # print(nouns)

    list(noun_extractor._compounds_components.items())[:100]
    # naword = [word for word in naword if (not word in stopwords) and len(word) > 1]

    #### START 신조어 추가
    wordTxtList = [ sentence for sentence in wordTxt.split('\n') if sentence ]

    # 5번 이상 언급된 단어들 중 일부 추출
    word_extractor = WordExtractor(min_frequency=5,
                                min_cohesion_forward = 0.05,
                                min_right_branching_entropy = 0.0)

    word_extractor.train(wordTxtList) # list of str or like
    words =word_extractor.extract()

    for word in words : 
        if len(word) < 2:
            continue
        subword = word[:-1]
        if not subword in words:
            continue
        if(words[word].leftside_frequency == words[subword].leftside_frequency) : 
            tmp = words[subword].cohesion_forward + words[word].cohesion_forward
            if word in stopwords : # 스탑워드에 있는 단어는 낮은 점수 부여
                # print(word)
                tmp *= -10
            words[word] = words[word]._replace(cohesion_forward = 10 + tmp)
            words[subword] = words[word]._replace(cohesion_forward = 0)

    # 내림차순 점수와 단어 출력
    print('단어   (빈도수, cohesion, branching entropy)\n')
    for word, score in sorted(words.items(), key=lambda x:word_score(x[1]), reverse=True)[:100]:
        print('%s     (%d, %.3f, %.3f)' % (
            word,
            score.leftside_frequency,
            score.cohesion_forward,
            score.right_branching_entropy
            )
        )

    # naword에 단어 추가
    for word in list(noun_extractor._compounds_components) : # 복합어
        # if word in naword : break
        naword.append(word)
        print('+' + word)

    print('********')

    for word in sorted(words.items(), key=lambda x:word_score(x[1]), reverse=True)[:30]: # 신조어 추정 단어 개수 지정
        # if word[0] in naword : break
        if len(word[0]) > 1 and ( word[0][-2:] == '에서' or word[0][-2:] == '이다' ) : 
            naword.append(word[0][:-2])
            print('++' + str(word[0][:-2]))
            continue
        if ((word[0][-1:]) == '은') or ((word[0][-1:]) == '는') or ((word[0][-1:]) == '을') or ((word[0][-1:]) == '를') or ((word[0][-1:]) == '하') or ((word[0][-1:]) == '의'):
            # if word[0][-1:] in naword : break
            naword.append(word[0][:-1])
            print('++' + str(word[0][:-1]))
        else : 
            naword.append(word[0])
            print('+' + str(word[0]))

    # 사용자 단어 추가
    addWords = ""
    # addWords = " 드론배송 탄소배출 배터리소재 전지소재 2차전지 탄소중립 자율비행 언어분석 로봇주행"
    addWords = set(addWords.split(' '))
    for word in addWords:
        # if word in naword : break
        naword.append(word)
        print('+' + str(word))    

    # 파일로 저장 후 다운로드하여 이름 변경하고 사용하기.
    # 2번 실행 시 중복으로 입력되니 삭제 후 1회만 실행 필요.
    # df.to_csv("./static/text/stopwords_KO2.csv", index=False, encoding="utf-8-sig")

    naword = [word for word in naword if (not word in stopwords) and len(word) > 1]

    # print(naword)

    # Counter로 빈도 집계
    counts = Counter(naword)

    # 복합어에 점수 더하기
    for word in counts.keys():
        for e in range(1, len(word)) : 
            subword = word[:e]
            if subword in counts.keys() :
                counts[word] = (counts[word] + counts[subword] * 0.8)
                counts[subword] *= 0.2
            subword = word[-e:]
            if subword in counts.keys() :
                counts[word] = (counts[word] + counts[subword] * 0.8)
                counts[subword] *= 0.2

    # count 임의 조정
    counts['클라우드'] /= 10
    # counts['금호석유화학'] /= 2

    #### END 복합어, 신조어 추가

    dict_keywords = counts.most_common(100)
    
    mask = np.array(Image.open('./static/image/Circle.JPG'))

    wc = WordCloud(stopwords=stopwords,
                # font_path=font_name, 
                font_path=r"D:\Profiles\20220170\Downloads\nanum-all\나눔 글꼴\나눔고딕\NanumFontSetup_TTF_GOTHIC\NanumGothic.ttf", 
                mask = mask, background_color='white', colormap = 'Set1',
                max_words=100, max_font_size=125, random_state=87, 
                width=400, height=400)# mask.shape[0]

    # wc.generate_from_frequencies(dict_keywords)    
    wc.generate_from_frequencies(dict(dict_keywords))
    
    # wc.generate(wordTxt)
    fig = plt.figure(figsize = (10,10))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis('off')
    # plt.show()
    
    output_path = r"D:\Profiles\20220170\Desktop\뉴스레터\wc images"
    timestr = time.strftime("%Y%m%d-%H%M%S")
    wc.to_file(path.join(output_path, 'wc_' + timestr + '.png'))
    # plt.close()

    # dict_source_list
    # return render(
    #     request, 'main.html',
    #     { 'dict': dict_keywords,
    #      'source_dict' : source_keywords
    #     }
    # )

    return HttpResponse('<h3>Word Cloud v.2 has been successfully generated. <br> Check your output file directory: ' 
        + output_path
        + '</h3>')
