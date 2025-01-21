# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-27 08:51:10
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-21 18:46:16
FilePath: /script/StockeRewards/main.py
Description: 
'''
import re
import json
from load_pdf import load_pdf
from llm import create_chatbot
from util.bulletin import get_list
from util.db import DB
from util.init_log import logger
from util.sr_config import prompt




def re_response(text):
    json_content = ""
    pattern = r'\{(.*?)\}'
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        json_content = matches[0]
        json_content.replace('\n', '')
    return '{'+json_content+'}'


def award_qa(db, chatbot, pdf_url):
    texts = load_pdf(pdf_url=pdf_url)
    prompt['user_prompt'] = prompt['user_prompt'].format(texts)

    try:
        has_reward = False
        
        response = chatbot.chat(prompt=prompt)
        response = re_response(response)
        response_json = json.loads(response)
        if '礼品' in response_json.keys():
            if response_json['礼品'] == 'True' or response_json['礼品'] == True:
                has_reward = True
        print(response_json, type(response_json), has_reward)
    except Exception as e:
        logger.error(f"award_qa: {str(e)} pdf: {pdf_url}")
    
    try:
        db.update_data(
            table_name="stocke_rewards",
            data={
                'has_reward': has_reward,
                'ai_detection': response,
                },
            condition={'pdf_url': pdf_url}
            )
    except Exception as e:
        logger.error(f"award_qa db.update_data: {str(e)} pdf: {pdf_url}")


def award_qa_all():
    db = DB()
    model_name = "mlx-community/deepseek-r1-distill-qwen-1.5b"
    chatbot = create_chatbot(model_name)

    # get_list()
    data = db.query_data(table_name="stocke_rewards", condition={'has_reward': None})
    for i in data:
        award_qa(db, chatbot=chatbot, pdf_url=i['pdf_url'])

    db.close()


def test_award_qa():
    db = DB()
    chatbot = create_chatbot(model_name="mlx-community/Qwen2.5-3B-Instruct-4bit")
    award_qa(db, chatbot, pdf_url='https://disc.static.szse.cn/download/disc/disk03/finalpage/2024-12-10/9996c33d-43de-486e-b1ef-6ec28e1c24e6.PDF')
    db.close()



if __name__ == '__main__':
    award_qa_all()
    # test_award_qa()
