import random
import json
import csv
import urllib.request
import openpyxl
from config import *

def remove_brands(keywords, brands):
    res_keywords = []

    for keyword in keywords:
        is_brand = 0

        for brand in brands:
            if brand in keyword:
                is_brand = 1
                break

        if is_brand == 0:
            res_keywords.append(keyword)

    return res_keywords


# 한글자 브랜드 제거
def remove_a_word(brands):
    res_brands = []

    for brand in brands:
        if len(brand) > 1:
            res_brands.append(brand)

    return res_brands


def get_keywords(data):
    res_keywords = []
    res_dict_clicks = {}

    for id_d, d in data.items():

        if "monthly" not in d:
            continue
        cnt_click = d['monthly']['total']


        if cnt_click >= MIN_CLICK and cnt_click <= MAX_CLICK:
            res_keywords.append(d['keyword'])
            res_dict_clicks[d['keyword']] = cnt_click

    return res_keywords, res_dict_clicks


def get_keywords_database(data):
    res_keywords = []

    for id_d, d in data.items():
        res_keywords.append(d['keyword'])

    return res_keywords


def get_auth_api(path):
    f = open(path, 'r')
    lines = f.readlines()
    client_auth = []

    for line in lines:
        client_auth.append(line.strip().split(' '))
    f.close()
    return client_auth


def get_items(url, client_auth):
    # code 429 : 호출 횟수 초과 --> 랜덤으로 app 돌려가면서 추출
    while True:

        num_app = random.randrange(0, len(client_auth))
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_auth[num_app][0])
        request.add_header("X-Naver-Client-Secret", client_auth[num_app][1])
        response = urllib.request.urlopen(request)
        rescode = response.getcode()

        if rescode == 429:
            continue

        elif rescode == 200:
            response_body = response.read().decode('utf-8')
            return json.loads(response_body)['items']

        else:
            print("Error Code:" + rescode)
            break


def convert_dict_to_excel(name, keywords):

    name_file = name + '.xlsx'

    while True:
        try:
            wb = openpyxl.load_workbook(name_file)
            sheet = wb.active
            for keyword in keywords:
                list_values = list(keyword.values())
                sheet.append(list_values)
            wb.save(name_file)
            wb.close()
            break

        except:
            wb = openpyxl.Workbook()
            sheet = wb.active
            list_keys = list(keywords[0].keys())
            sheet.append(list_keys)
            wb.save(name_file)
            wb.close()



def remove_duplicates(titles):
    res = []
    for title in titles:
        if title not in res:
            res.append(title)
    return res


def is_in_database(database, keyword):
    if keyword in database:
        return 1
    else:
        return 0


def recommand_keywords_tags(keyword, database_string,cnt_recommand=5):
    encText = urllib.parse.quote(keyword)
    url_items = "https://openapi.naver.com/v1/search/shop.json?display=80&query=" + encText  # JSON 결과
    path_auth = 'auth_api.txt'
    client_auth = get_auth_api(path_auth)

    titles = []
    items = get_items(url_items, client_auth)

    for item in items:
        title = item['title'].replace('<b>', '').replace('</b>', '')
        titles.append(title)

    titles = remove_duplicates(titles)

    vocab = {}

    for title in titles:
        for word in title.split():
            if word in vocab:
                vocab[word] += 1
            else:
                vocab[word] = 1

    sorted_vocab = sorted(vocab.items(), key=lambda item: item[1], reverse=True)

    recommand_title = keyword + ' '
    recommand_tags = ''
    words = []
    tags = []

    for pair in sorted_vocab:
        # 2개 이상 반복 단어
        if pair[1] > 1:
            word = pair[0]
            # top500 데이터에 존재하는 단어
            if word not in keyword and is_in_database(database_string, word):
                words.append(word)

    # 특수문자 제거, 숫자제거
    punctuation = '~!@#$%^&*()_+{}|:"<>?[]\;'',./123456789020'
    for word in words:
        if word in punctuation:
            words.remove(word)

    recommand_title += ' '.join(s for s in words[:CNT_BASIC_WORDS])

    if len(words[CNT_BASIC_WORDS:]) > cnt_recommand:
        random_words = random.sample(words[CNT_BASIC_WORDS:], cnt_recommand)
    else :
        random_words = words[CNT_BASIC_WORDS:]

    recommand_title += ' ' + ' '.join(s for s in random_words)

    for word in words:
        if word not in recommand_title:
            tags.append(word)

    if len(tags)>10 :
        random_tags = random.sample(tags, 10)
    else :
        random_tags = tags

    recommand_tags += ','.join(s for s in random_tags)

    return recommand_title, recommand_tags, words


