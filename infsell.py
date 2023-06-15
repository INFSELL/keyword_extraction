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

        num_app = random.randrange(0, CNT_NAVER_APP)
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

    return print('엑셀 변환 완료')

