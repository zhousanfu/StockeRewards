# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-27 23:46:02
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2024-12-30 16:27:45
FilePath: /script/StockeRewards/util/qa.py
Description: 
'''
import os
import sys
import json
import asyncio
import requests
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from util.xai import chat
from util.db import DB
from util.config import prompt



CURRENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AwardResponse(BaseModel):
    has_reward: bool = Field(description=prompt['award_bool_prompt'])
    get_tutorial: str = Field(description=prompt['award_get_tutorial'])

async def load_pdf(pdf_url):
    reward = []
    pdf_path = CURRENT_DIRECTORY+'/data/tmp.pdf'
    
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(pdf_path, 'wb') as file:
            file.write(response.content)
        file.close()

    loader = PyPDFLoader(
        file_path=pdf_path,
        extract_images = True,
    )
    
    for d in await loader.aload():
        reward.append(d.page_content.replace('\n', ' ').replace('\t', ' ').replace('\r', ' '))
    
    return reward


async def award_qa(db, pdf_url):
    docs = await load_pdf(pdf_url=pdf_url)
    reward = await chat(
        prompt=prompt['pdf_prompt']%(" ".join(docs)),
        Response=AwardResponse
    )

    reward = json.loads(reward)
    db.update_data(
        table_name="stocke_rewards",
        data={'has_reward': reward['has_reward'], 'ai_detection': reward['get_tutorial']},
        condition={'pdf_url': pdf_url}
        )


async def award_all(db):
    data = db.query_data(table_name="stocke_rewards", condition={'has_reward': None})
    for i in data:
        await award_qa(db, pdf_url=i['pdf_url'])
    # tasks = [award_qa(db, pdf_url=i['pdf_url']) for i in data]
    # await asyncio.gather(*tasks)



if __name__ == "__main__":
    db = DB()
    asyncio.run(award_all(db=db))
    db.close()