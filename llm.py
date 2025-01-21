# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2025-01-05 10:57:22
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-21 18:36:41
FilePath: /script/StockeRewards/llm.py
Description: Qwen DOC https://qwen.readthedocs.io/zh-cn/latest/quantization/gptq.html
'''
import sys
from mlx_lm import load, generate
from typing import Dict, Optional
from dataclasses import dataclass
from util.init_log import logger
from modelscope import AutoModelForCausalLM, AutoTokenizer



@dataclass
class ChatConfig:
    top_p: float = 0.8
    temperature: float = 0.7
    repetition_penalty: float = 1.05
    max_tokens: int = 512


class ChatBotDarwin:
    def __init__(self, model_name: str):
        try:
            self.model, self.tokenizer = load(
                model_name, 
                tokenizer_config={"eos_token": "<|im_end|>"}
            )
        except Exception as e:
            raise RuntimeError(f"模型加载失败: {str(e)}")
        
    def chat(
        self, 
        prompt: Dict[str, str],
        config: Optional[ChatConfig] = None
    ) -> str:
        if not isinstance(prompt, dict) or not all(k in prompt for k in ['system_prompt', 'user_prompt']):
            raise ValueError("prompt 必须是包含 system_prompt 和 user_prompt 的字典")

        messages = [
            {"role": "system", "content": prompt['system_prompt']},
            {"role": "user", "content": prompt['user_prompt']}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        config = config or ChatConfig()
        
        try:
            response = generate(
                self.model, 
                self.tokenizer, 
                prompt=text, 
                verbose=False,
                top_p=config.top_p,
                temp=config.temperature,
                repetition_penalty=config.repetition_penalty,
                max_tokens=config.max_tokens
            )
            return response
        except Exception as e:
            logger.error(f"生成回答失败: {str(e)}")


class ChatBotLinux:
    def __init__(self, model_name: str):
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype="auto",
                device_map="auto"
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        except Exception as e:
            raise RuntimeError(f"模型加载失败: {str(e)}")
                
    def chat(
        self, 
        prompt: Dict[str, str],
        config: Optional[ChatConfig] = None
    ) -> str:
        if not isinstance(prompt, dict) or not all(k in prompt for k in ['system_prompt', 'user_prompt']):
            raise ValueError("prompt 必须是包含 system_prompt 和 user_prompt 的字典")

        messages = [
            {"role": "system", "content": prompt['system_prompt']},
            {"role": "user", "content": prompt['user_prompt']}
        ]

        config = config or ChatConfig()
        
        try:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=config.max_tokens,
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

            return response
        except Exception as e:
            logger.error(f"生成回答失败: {str(e)}")


def create_chatbot(model_name):
    if sys.platform == "darwin":
        chatbot = ChatBotDarwin(model_name)
    elif sys.platform == "linux" or sys.platform == "win32":
        chatbot = ChatBotLinux(model_name)

    return chatbot



if __name__ == "__main__":
    model_name = "mlx-community/deepseek-r1-distill-qwen-1.5b"
    # model_name="mlx-community/Qwen2.5-3B-Instruct-4bit"

    chatbot = create_chatbot(model_name)

    test_prompt = {
        "system_prompt": "你是一个有帮助的AI助手。",
        "user_prompt": "你是谁？"
    }
    try:
        response = chatbot.chat(test_prompt)
        print(f"AI回答: {response}")
    except Exception as e:
        print(f"错误: {str(e)}")