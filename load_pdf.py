# coding=utf-8
'''
Author: sanford courageux_san@wechat.com
Date: 2024-12-27 23:46:02
LastEditors: sanford courageux_san@wechat.com
LastEditTime: 2025-01-05 13:38:42
FilePath: /script/StockeRewards/load_pdf.py
Description: 
'''
import requests
from pathlib import Path
from typing import Optional
from langchain_community.document_loaders import PyPDFLoader
from util.init_log import logger



CURRENT_DIRECTORY = Path(__file__).parent

def load_pdf(pdf_url: str) -> Optional[str]:
    """
    从URL下载并加载PDF文件内容
    
    Args:
        pdf_url: PDF文件的URL
    
    Returns:
        str: PDF文件的文本内容
        None: 如果处理失败
    """
    try:
        # 使用 Path 处理文件路径
        pdf_filename = pdf_url.split('/')[-1]
        pdf_path = CURRENT_DIRECTORY / 'data' / pdf_filename

        # 确保数据目录存在
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # 下载文件（如果不存在）
        if not pdf_path.exists():
            logger.info(f"Downloading PDF from {pdf_url}")
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            pdf_path.write_bytes(response.content)
            logger.info(f"PDF saved to {pdf_path}")

        # 加载PDF内容
        loader = PyPDFLoader(
            file_path=str(pdf_path),
            extract_images=False,
        )
        
        # 使用列表推导式和join优化文本处理
        texts = ' '.join(
            page.page_content.replace('\n', ' ').strip()
            for page in loader.lazy_load()
        )

        return texts.strip()

    except requests.RequestException as e:
        logger.error(f"Failed to download PDF: {e} pdf: {pdf_url}")
        return None
    except Exception as e:
        logger.error(f"Error processing PDF: {e} pdf: {pdf_url}")
        return None

if __name__ == "__main__":
    test_url = 'https://disc.static.szse.cn/download/disc/disk03/finalpage/2025-01-04/8ae1b97b-3484-4f43-9817-cb13ce0b0bbb.PDF'
    result = load_pdf(test_url)
    print(result)