# -*- coding: utf-8 -*-
import streamlit as st
import fitz
from ibm_watsonx_ai.client import APIClient
from ibm_watsonx_ai.foundation_models import ModelInference

# ========== 页面设置 ==========
st.set_page_config(page_title="KnightG · 贵族式申请助手", layout="wide")

# ========== 日/夜模式切换 ==========
mode = st.selectbox("🌗 Select Mode", ["Daylight Elegance", "Midnight Nobility"])
if mode == "Daylight Elegance":
    bg_color, text_color, logo = "#FDF6EC", "#5C4033", "logo_day_transparent.png"
else:
    bg_color, text_color, logo = "#0D1B2A", "#F5F5DC", "logo_night_transparent.png"

# ========== 自定义背景与样式 ==========
st.markdown(f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .reportview-container {{
        background: {bg_color};
    }}
    .block-container {{
        padding-top: 3rem;
        padding-bottom: 3rem;
    }}
    </style>
""", unsafe_allow_html=True)

# ========== 页面顶部 Logo 与标题 ==========
st.image(logo, width=160)
st.markdown(f"""
<h2 style='text-align: center; color: {text_color}; font-family: serif;'>
    🕯️ Welcome to KnightG<br>
    <small style='font-size:16px;'>Your Personal AI Curator for Global Excellence</small>
</h2>
""", unsafe_allow_html=True)

st.divider()

# ========== IBM Watsonx 设置 ==========
client = APIClient({
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": st.secrets["apikey"]
})
model = ModelInference(
    model_id="ibm/granite-3-3-8b-instruct",
    api_client=client,
    project_id="7ed76c84-2faa-42b7-8a66-b4413c955c87",
    params={"max_new_tokens": 800}
)

# ========== 简历 PDF 提取函数 ==========
def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

# ========== 主体区域：左右两栏 ==========
col1, col2 = st.columns(2)

# === 左栏：AI身份建议器 ===
with col1:
    st.markdown("### 👤 AI身份建议器 Identity Insight")
    st.markdown("上传你的简历或粘贴描述，我们将识别你的申请特质，推荐身份定位。")

    uploaded_cv = st.file_uploader("上传简历 PDF", type="pdf", key="cv")
    pasted_cv = st.text_area("或直接粘贴简历/背景内容", key="cv_text")

    if st.button("🔍 分析身份"):
        if uploaded_cv:
            raw_cv = extract_text_from_pdf(uploaded_cv)
        elif pasted_cv:
            raw_cv = pasted_cv
        else:
            st.warning("请提供简历内容")
            st.stop()

        prompt_id = f"""
You are an elite university application strategist.

Given the following applicant profile, analyze the academic/professional background and suggest the most suitable application identity (choose from: Academic Thinker, Creative Synthesizer, Practical Visionary, Cultural Curator, Global Identity Builder). Justify your recommendation and give suggestions on the appropriate tone for personal statements.

Profile:
{raw_cv}
"""
        with st.spinner("识别身份中..."):
            identity_result = model.generate(prompt=prompt_id)
        st.markdown("#### ✨ 推荐身份定位")
        st.markdown(identity_result)

# === 右栏：留学路径推荐器 ===
with col2:
    st.markdown("### 🌍 留学路径推荐器 Global Pathway Recommender")
    st.markdown("输入一段简述（中英文均可），我们将推荐适合你的留学国家与方向。")

    user_note = st.text_area("✍️ 请描述你的背景/兴趣/偏好")

    if st.button("📌 推荐国家与项目"):
        if not user_note:
            st.warning("请输入内容")
            st.stop()

        prompt_path = f"""
你是一个留学规划专家。根据以下用户自述，推荐最适合他的留学国家（最多三项）与项目方向（如研究型、实务型、品牌型等），并用一种优雅克制的语气给出建议。

用户信息：
{user_note}
"""
        with st.spinner("规划最适合的路径中..."):
            path_result = model.generate(prompt=prompt_path)
        st.markdown("#### 🎓 全球路径推荐")
        st.markdown(path_result)

# ========== 页面底部标识 ==========
st.divider()
st.markdown(f"""
<div style='text-align:center; font-size:14px; color:{text_color};'>
    ⸻<br>
    KnightG · Crafted for the Discerning Few
</div>
""", unsafe_allow_html=True)
