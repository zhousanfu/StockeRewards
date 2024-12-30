# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-27 08:51:10
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2024-12-30 17:03:26
FilePath: /script/StockeRewards/main.py
Description: 
'''
import asyncio
from util.db import DB
from util.bulletin import get_list, init_all_data
from util.qa import award_all



if __name__ == '__main__':
    # init_all_data()

    get_list()
    db = DB()
    asyncio.run(award_all(db=db))
    rewards = db.query_data(condition={'has_reward', 1})
    for i in rewards:
        print(i)
    db.close()