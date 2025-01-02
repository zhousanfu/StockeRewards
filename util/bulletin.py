# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-27 08:51:10
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-02 14:34:52
FilePath: /script/StockeRewards/util/bulletin.py
Description: 
'''
import time
import json
import requests
from datetime import datetime, timedelta
try:
    from .init_log import init_log
    from .db import DB
except ImportError:
    from init_log import init_log
    from db import DB



URL = "http://www.szse.cn"
DOWNLOAD_URL = "https://disc.static.szse.cn/download"
logger = init_log()

def save_data(data: json):
    db = DB()
    for i in data:
        i['attachPath'] = DOWNLOAD_URL+i['attachPath']
        d = {
            'stock_name': i['secName'][0],
            'announcement_title': i['title'],
            'pdf_url': DOWNLOAD_URL+i['attachPath'],
            'publish_date': i['publishTime']
        }
        try:
            db.insert_data(table_name="stocke_rewards", data=d)
        except Exception as e:
            logger.error(f"插入数据时出错: {e}")
    db.close()

def get_list(date: str=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")):
    """获取昨天的公告"""
    announceCount = 0
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "www.szse.cn",
        "Origin": "http://www.szse.cn",
        "Referer": "http://www.szse.cn/disclosure/listed/notice/index.html",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15",
        "X-Request-Type": "ajax",
        "X-Requested-With": "XMLHttpRequest"
    }
    data = {
        "seDate": [date, date],
        "channelCode": ["listedNotice_disc"],
        "pageSize": 50,
        "pageNum": 1
    }
    response = requests.post(URL+'/api/disc/announcement/annList', headers=headers, json=data)
    if response.status_code == 200:
        announceCount = response.json()['announceCount']
        save_data(data=response.json()['data'])
    else:
        logger.error(f"Requests Error: {response.status_code}")

    for i in range(5, int(announceCount/50)+5):
        time.sleep(5)
        data['pageNum'] = i
        response = requests.post(URL+'/api/disc/announcement/annList', headers=headers, json=data)
        if response.status_code == 200:
            save_data(data=response.json()['data'])
        else:
            logger.error(f"Requests Error: {response.status_code}")

def init_all_data(day: int=30):
    """获取历史公告数据 默认:过去30天"""
    today = datetime.now()
    for i in range(day):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        get_list(date)

if __name__=="__main__":
    get_list()