# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-27 23:46:02
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-02 16:20:39
FilePath: /script/StockeRewards/util/qa.py
Description: 
'''
import os
import json
import requests
from langchain_community.document_loaders import PyPDFLoader
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from .llm import chat_cohere as chat
    from .llm import AwardResponse
    from .db import DB
    from .sr_config import prompt
except ImportError:
    from llm import chat_cohere as chat
    from llm import AwardResponse
    from db import DB
    from sr_config import prompt




CURRENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_pdf(pdf_url):
    reward = []
    pdf_path = CURRENT_DIRECTORY+f'/data/{pdf_url.split('/')[-1]}.pdf'
    
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(pdf_path, 'wb') as file:
            file.write(response.content)
        file.close()

    loader = PyPDFLoader(
        file_path=pdf_path,
        extract_images=True,
    )
    
    for d in loader.lazy_load():
        reward.append(d.page_content.replace('\n', ' ').replace('\t', ' ').replace('\r', ' '))
    
    return reward


def award_qa(db, pdf_url):
    docs = load_pdf(pdf_url=pdf_url)
    reward = chat(
        prompt=prompt['pdf_prompt']%(" ".join(docs)),
        Response=AwardResponse
    )
    reward_json = json.loads(reward)
    db.update_data(
        table_name="stocke_rewards",
        data={
            'has_reward': reward_json['has_reward'],
            'ai_detection': reward,
            },
        condition={'pdf_url': pdf_url}
        )


def award_all(db):
    data = db.query_data(table_name="stocke_rewards", condition={'has_reward': None})
    for i in data:
        award_qa(db, pdf_url=i['pdf_url'])


if __name__ == "__main__":
    db = DB()
    award_qa(db=db, pdf_url='https://disc.static.szse.cn/download/disc/disk03/finalpage/2024-12-10/9996c33d-43de-486e-b1ef-6ec28e1c24e6.PDF')
    db.close()