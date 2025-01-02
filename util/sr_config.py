# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-30 14:21:52
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-02 14:41:06
FilePath: /script/StockeRewards/util/sr_config.py
Description: 
'''
XAI_API_KEY = None

prompt = {
    'pdf_prompt': """通过以下内容,判断持股当前是否能获取礼品(礼品可以是虚伪票务或者实体物品, 现金分红和股权等不算),如果有礼品还要结出领取教程,公告内容如下:\n%s""",
    'award_bool_prompt': "是否有礼品",
    'award_get_tutorial': "礼品领取教程"
}