# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-30 14:21:52
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2024-12-30 16:49:23
FilePath: /script/StockeRewards/util/config.py
Description: 
'''
XAI_API_KEY = None

prompt = {
    'pdf_prompt': """通过以下内容,识别当前股票持股是否能获取礼品(礼品可以是虚伪票或者实体物品),内容如下:\n%s""",
    'award_bool_prompt': "是否有奖励",
    'award_get_tutorial': "文档中的礼品领取教程"
}