
import streamlit as st
from utils import extract_text_from_file, init_model

st.set_page_config(page_title="KnightG · 智能申请建议器", layout="wide")
st.title("🎓 KnightG · 全能申请建议助手")

tab1, tab2, tab3, tab4 = st.tabs(["🌍 留学路径推荐", "🧾 简历分析", "📊 成绩单分析", "👤 身份建议"])

def handle_tab(tab_title, prompt_instruction, input_key):
    with tab_title:
        file = st.file_uploader("上传文件（PDF, Word, Excel, CSV 等）", type=["pdf", "csv", "xls", "xlsx", "txt", "docx"], key=input_key+"_file")
        text = st.text_area("或直接粘贴内容", key=input_key+"_text")

        if st.button("✦ 生成建议", key=input_key+"_btn"):
            if file:
                raw = extract_text_from_file(file)
            elif text:
                raw = text
            else:
                st.warning("请上传文件或填写内容")
                st.stop()

            model = init_model(st.secrets["apikey"])

            prompt = f"""{prompt_instruction}

用户内容：
{raw}
"""

            with st.spinner("请稍候，正在分析..."):
                result = model.generate(prompt=prompt)

            st.markdown("## 🌟 推荐结果")
            st.markdown(result["results"][0]["generated_text"])

handle_tab(tab1, 
    "你是一个留学规划专家。根据以下用户自述，推荐最适合他的留学国家（最多三项）与项目方向（如研究型、实务型、品牌型等），并用一种优雅克制的语气给出建议。",
    "input1")

handle_tab(tab2,
    "请根据以下简历内容，判断该申请人的背景优势，并提出写作建议或结构化改进方向。",
    "input2")

handle_tab(tab3,
    "你是一个留学成绩分析专家，请根据以下课程和成绩信息，分析该学生的学术强项与不足，并提供选校建议方向。",
    "input3")

handle_tab(tab4,
    "你是一个顶尖大学申请顾问，请根据以下背景，推荐该申请人适合的申请身份 archetype（Academic Thinker, Creative Synthesizer, Practical Visionary, Cultural Curator, Global Identity Builder），并解释理由。",
    "input4")
