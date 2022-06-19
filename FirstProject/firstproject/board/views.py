import itertools
from django.shortcuts import render
from django.http import HttpResponse
from .models import Curriculum

import os
import string
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter, OrderedDict, defaultdict
from wordcloud import WordCloud,STOPWORDS
from tika import parser
# import PyPDF2
# import textract
# import nltk
from konlpy.tag import Okt
from PIL import Image
import numpy as np
import json
from itertools import islice


# nltk.download('punkt')
# nltk.download('stopwords')
# Create your views here.
# Read PDF files
# Method 1. textract
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
  
# Views
def main(request):
    return HttpResponse('<u>Hello</u>')

def insert(request):
    Curriculum(name='class1').save()
    Curriculum(name='class2').save()
    return HttpResponse('데이터 입력 완료')
    
def show(request):
    # Multiple pdfs in a directory
    docs_path = './static/pdf'
    all_keywords = []
    source_keywords = defaultdict(list)
    
    for filename in os.listdir(docs_path):
        filepath = os.path.join(docs_path, filename)
        
        # PDF 파일에서 텍스트를 추출
        print(f'Parsing file: {filename}')
    
        raw_pdf = parser.from_file(filepath) 
        contents = raw_pdf['content'] 
        contents = contents.strip()

        okt = Okt()
        nouns = okt.nouns(contents) # 명사만 추출

        words = [n for n in nouns if len(n) > 1] # 단어의 길이가 1개인 것은 제외
        distinct_words = set(words)
        for word in distinct_words:
            source_keywords[word].append(filename)
            # source_keywords[word].append(filepath)
            
        all_keywords.extend(words)
               
    dict_keywords = Counter(all_keywords) # 위에서 얻은 words를 처리하여 단어별 빈도수 형태의 딕셔너리 데이터를 구함

    ###
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
        request, 'board/show.html',
        { 'dict': dict_keywords,
         'source_dict' : source_keywords
        }
    )


# def show(request):
#     # curriculum = Curriculum.objects.all()
#     # result = ''
#     # for c in curriculum:
#     #     result += c.name + '<br>'
#     # return HttpResponse(result)
#     curriculum = Curriculum.objects.all()
    
#     # single pdf    
#     filepath = './static/pdf/4초시대.pdf'

#     # multiple pdfs in a dir
#     docs_path = './static/pdf'
#     all_keywords = []
    
#     # PDF 파일에서 텍스트를 추출
#     raw_pdf = parser.from_file(filepath) 
#     contents = raw_pdf['content'] 
#     contents = contents.strip()

#     # print(contents)
#     # print("**** type: ", type(contents))
    
#     okt = Okt()
#     nouns = okt.nouns(contents) # 명사만 추출

#     words = [n for n in nouns if len(n) > 1] # 단어의 길이가 1개인 것은 제외

#     dict_keywords = Counter(words) # 위에서 얻은 words를 처리하여 단어별 빈도수 형태의 딕셔너리 데이터를 구함
    
#     wc = WordCloud(
#             font_path='/Library/Fonts/NotoSansCJKkr-Regular.otf',
#             width=400, height=400, scale=2.0,
#             max_font_size=250
#         )
    
#     gen = wc.generate_from_frequencies(dict_keywords)
#     # print(dict_keywords)
#     # plt.figure()
#     # plt.imshow(gen)
#     # wc.to_file('outputImage.png')
    
#     ###
#     # 빈도로 내림차순 정렬
#     dict_keywords = OrderedDict(sorted(dict_keywords.items(), key = lambda item: item[1], reverse = True))
#     # print("----- 자르기 전: ", len(dict_keywords))
#     dict_keywords = dict(islice(dict_keywords.items(), 100))
#     for key in dict_keywords.keys():
#         source_keywords[key].append(filepath)
    
#     # dict_keywords_list = list(dict_keywords)
#     dict_keywords = json.dumps(dict_keywords, indent=4, ensure_ascii=False)
#     source_keywords = json.dumps(source_keywords, indent=4, ensure_ascii=False)
#     print("원래 dict_keywords: ", dict_keywords)
#     print("------------------------------------")
#     print("path붙인 source_keywords: ", source_keywords)
#     # print("----- 자른 후: ", len(dict_keywords))
    
#     # dict_source_list
#     return render(
#         request, 'board/show.html',
#         { 'dict': dict_keywords,
#          'source_dict' : source_keywords}
#     )
