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
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import pickle
import re
from ckonlpy.tag import Twitter
# nltk.download('gutenberg')
# nltk.download('maxent_treebank_pos_tagger')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('stopwords')
# Create your views here.
# Read PDF files
# Method 1. textract

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# driver = webdriver.Chrome('D:/Profiles/20220170/django/chromedriver.exe', options=options) 
driver = webdriver.Chrome('chromedriver.exe', options=options) 

t = time.time()
driver.set_page_load_timeout(10)

url_list = [
    'https://n.news.naver.com/mnews/article/092/0002260916?sid=105',
    'https://n.news.naver.com/mnews/article/366/0000823875?sid=105',
    'https://n.news.naver.com/mnews/article/003/0011273577?sid=105',
    'https://n.news.naver.com/mnews/article/031/0000681807?sid=105',
    'https://www.hankyung.com/it/article/202206281272Y',
    # 'https://www.etnews.com/20220628000152',
    'https://n.news.naver.com/mnews/article/030/0003026448?sid=101',
    # 'https://www.etnews.com/20220628000166'
    'https://n.news.naver.com/mnews/article/030/0003026460?sid=105'
]

## 사용자 사전에 명사 등록
twitter = Twitter()
twitter.add_dictionary(
    ['메타버스', 'DBMS', '애널리틱스', '로보틱스', 'LG유플러스', 'LGCNS', 'LG화학', '삼성전자', '디지털트랜스포메이션', 'SKT', 'SK쉴더스',
    '세일즈포스','하이퍼포스', '랜섬웨어', '액화수소', '폴더블', '스마트폰', '라이다'],
    'Noun')

# 불용어 사전 - 파일 읽어서 등록
global stopwords
stopwords = set(STOPWORDS)
st_file_path = './static/text/stopwords_KO.txt'
with open(st_file_path, "r", encoding="UTF-8") as f:
    lines = f.read().splitlines()

for stw in lines:
    stopwords.add(stw)

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
  
def makeAll(url):
    start = time.time()
    try:
        driver.get(url)
    except TimeoutException:
        driver.execute_script("window.stop();")
    print('Time consuming:', time.time() - t)

    from selenium.webdriver.common.by import By
    if 'etnews' in url : 
        _cont = driver.find_element(By.CLASS_NAME, 'article_txt')
    elif 'mk.co.kr' in url : 
        _cont = driver.find_element(By.CLASS_NAME, 'art_txt')
    elif 'hankyung' in url : 
        _cont = driver.find_element(By.ID, 'articletxt')
    elif 'naver' in url : 
        _cont = driver.find_element(By.CLASS_NAME, '_article_content')
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

    # dict_source_list
    # return render(
    #     request, 'main.html',
    #     { 'dict': dict_keywords,
    #      'source_dict' : source_keywords
    #     }
    # )

    return HttpResponse('<h3>Word Cloud has been successfully generated. <br> Check your output file directory: ' 
        + output_path
        + '</h3>')
    
def wordcloud_url(request):
    all_keywords = []
    dict_keywords = []
    source_keywords = defaultdict(list)
    
    global url_list

    for url in url_list:
        # url에서 텍스트를 추출
        print(f'Parsing url: {url}')
        wordTxt = makeAll(url)     # 가공 전 기사 text를 return
    
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
        # print(naword)

        # 한국어 + 영어 명사 추출 후 불용어 제거
        # 한글 stopwords txt 읽어서 추가
        stopwords = set(STOPWORDS)
        st_file_path = './static/text/stopwords_KO.txt'
        with open(st_file_path, "r", encoding="UTF-8") as f:
            lines = f.read().splitlines()

        for stw in lines:
            stopwords.add(stw)

        # Stopwords Customizing
        # target_stop = ['https', 'all', 'article', 'copyright', 'print', 'etnews', 'mnews', 'news']
        # for t in target_stop:
        #     stopwords.add(t)
        
        naword = [word for word in naword if (not word in stopwords) and len(word) > 1]
        # naword = [i.upper() for i in naword]

        # 중복제거된 단어들 - 원본 filename을 저장
        distinct_words = set(naword)
        for word in distinct_words:
            source_keywords[word].append(url)
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

    return render(
        request, 'board/wordcloud_url.html',
        { 'dict': dict_keywords,
         'source_dict' : source_keywords
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
    return HttpResponse('접속이 잘 되네용')