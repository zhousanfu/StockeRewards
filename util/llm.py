# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-28 09:38:55
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-02 16:18:13
FilePath: /script/StockeRewards/util/llm.py
Description: 
'''
import os
import json
import cohere
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
try:
    from .sr_config import prompt
except ImportError:
    from sr_config import prompt
load_dotenv()




XAI_API_KEY = os.getenv("XAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")


client_cohere = cohere.ClientV2(COHERE_API_KEY)
client_xai = OpenAI(api_key=XAI_API_KEY, base_url="https://api.x.ai/v1")


class AwardResponse(BaseModel):
    has_reward: bool = Field(description=prompt['award_bool_prompt'])
    get_tutorial: str = Field(description=prompt['award_get_tutorial'])
    start_time: str = Field(description="开始时间")
    end_time: str = Field(description="结束时间")


def chat_cohere(prompt, model_name="command-r-plus", Response=None):
    response = client_cohere.chat(
        model=model_name, 
        messages=[
            {"role": "user", "content": prompt}
            ],
        response_format={
            "type": "json_object",
            "schema": {
                "type": "object",
                "properties": {
                    "has_reward": {"type": "string"},
                    "get_tutorial": {"type": "string"},
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                },
                "required": ["has_reward", "get_tutorial", "start_time", "end_time"],
            },
        },
    )

    return response.message.content[0].text

def chat_xai(prompt, model_name="grok-2-latest", structur:bool = True, Response=None):
    results = None

    if structur:
        completion = client_xai.beta.chat.completions.parse(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format=Response,
        )
        results = completion.choices[0].message.content
    else:
        stream = client_xai.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in stream:
            if chunk:
                res = chunk.choices[0].delta.content
                if res:
                    results += res

    return results



if __name__=="__main__":
    r = chat_xai(prompt="你是谁", structur=False)
    r = chat_cohere("你是谁")
    print(r)