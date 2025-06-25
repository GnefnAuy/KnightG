
import fitz
import pandas as pd
from ibm_watsonx_ai.client import APIClient
from ibm_watsonx_ai.foundation_models import ModelInference

# PDF 提取
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# 表格读取（支持 xlsx, csv）
def extract_text_from_file(file):
    if file.name.endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.name.endswith('.csv'):
        df = pd.read_csv(file)
    elif file.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file)
    else:
        return file.read().decode("utf-8", errors="ignore")
    return df.to_string(index=False)

# WatsonX API 初始化
def init_model(apikey):
    client = APIClient({
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": apikey
    })
    return ModelInference(
        model_id="ibm/granite-3-3-8b-instruct",
        api_client=client,
        project_id="7ed76c84-2faa-42b7-8a66-b4413c955c87",
        params={"max_new_tokens": 800}
    )
