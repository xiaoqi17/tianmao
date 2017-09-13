# -*- coding: utf-8 -*-
import re
from multiprocessing import Pool
from urllib import urlencode

import pymongo
import requests
import json
import time
from config import *
import sys
from requests import ConnectionError

reload(sys)
sys.setdefaultencoding('utf-8')

client = pymongo.MongoClient( 'localhost', connect=False)
db = client['tianmao']

headers = {
        'User - Agent': 'Mozilla / 5.0(iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit / 601.1.46(KHTML, like Gecko) Version / 9.0 Mobile / 13 B143 Safari / 601.1',
    }

def Keywords():
    for keyword in keywords:
        yield keyword

def MONGO_TABLES(keyword):
    if keyword == '笔记本电脑':
        MONGO_TABLE = '笔记本电脑'
        return MONGO_TABLE
    if keyword == '台式电脑':
        MONGO_TABLE = '台式电脑'
        return MONGO_TABLE
    if keyword == '鼠标':
        MONGO_TABLE = '鼠标'
        return MONGO_TABLE
    if keyword == '键盘':
        MONGO_TABLE = '键盘'
        return MONGO_TABLE
    if keyword == '硬盘':
        MONGO_TABLE = '硬盘'
        return MONGO_TABLE
    if keyword == '显卡':
        MONGO_TABLE = '显卡'
        return MONGO_TABLE
    if keyword == '内存条':
        MONGO_TABLE = '内存条'
        return MONGO_TABLE

def index_html(keyword,page):
    try:
        data = {
            'keyword': keyword,
            'page': page,
        }
        params = urlencode(data)  ##利用urllib中的urlencode来构建data
        url = 'https://jingxuan.tmall.com/jxm/tmall/search/v1?' + params
        print url
        response = requests.get(url, headers)
        time.sleep(3)
        response.encoding = response.apparent_encoding  # 默认编码改为UTF-8
        if response.status_code == 200:  # 检测返回码是否200
            text = response.text
            text = re.sub(r'<span class=H>','',text)
            text = re.sub(r'</span>','',text)
            return text
        return None

    except ConnectionError:
        pass

def page_index(MONGO_TABLE,text):
    try:
        datas = json.loads(text)
        items = datas['result']['items']
        for item in items:
            data = {
                '产品名':item['title'].strip('<span class=H>.*?</span>'),
                '产地':item['provcity'],
                '店铺':item['nick'],
                '价格':item['discountPrice'],
                '成交':item['uvsum'],
                '店铺链接':item['clickUrl']
            }
            print data
            db[MONGO_TABLE].insert_one(data)
        return None
    except:
        pass



def main(page):
   for keyword in Keywords():
       MONGO_TABLE = MONGO_TABLES(keyword)
       text = index_html(keyword, page)
       page_index(MONGO_TABLE, text)
if __name__ == '__main__':
    pool_num = 4
    pool = Pool(pool_num)
    group = ([page for page in range(1, 101)])
    pool.map(main, group)
    pool.close()
    pool.join()