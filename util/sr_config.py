# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-30 14:21:52
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-05 14:48:30
FilePath: /script/StockeRewards/util/sr_config.py
Description: 
'''
import re
prompt = {
    'system_prompt': """你是一个研究股东分红的的帮助手,认真阅读公司的公告,判断公告中是否有福利活动(实物礼品、电影票、景点门票等类似的礼品, 现金分红和股权等不算),如果有福利活动就提取公告的中的领取说明,最终输出JSON数据:{"礼品":"", "活动开始时间":"", "活动结束时间":"", "领取要求":"", "领取说明":""},其中"礼品"的值只能是布尔类型True或False,不可以为空""",
    'user_prompt': "公告内容如下:{}",
}