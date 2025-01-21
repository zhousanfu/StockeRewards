# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-30 15:03:05
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-05 12:19:04
FilePath: /script/StockeRewards/util/init_log.py
Description: 
'''
import os 
import logging


CURRENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = CURRENT_DIRECTORY+'/logs/stockerewards.log'



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
