
import streamlit as st
from utils_multilang import extract_text_from_file, init_model, translate_text

st.set_page_config(page_title="KnightG · Global Application Advisor", layout="centered")

# 语言切换
lang = st.selectbox("🌐 Language", ["English", "Chinese", "German", "Spanish"])

st.title("🎓 KnightG · Global Application Advisor")

tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Global Pathway Recommender",
    "🧾 Profile Advisor",
    "📊 Transcript Analyzer",
    "👤 Identity Insight"
])

def handle_tab(tab, prompt_instruction, key_prefix):
    with tab:
        file = st.file_uploader("Upload your file (PDF, Word, Excel, CSV, etc.):", type=["pdf", "csv", "xls", "xlsx", "txt", "docx"], key=key_prefix+"_file")
        text = st.text_area("Or paste your text below:", key=key_prefix+"_text")

        if st.button("✦ Generate Advice", key=key_prefix+"_btn"):
            if file:
                raw = extract_text_from_file(file)
            elif text:
                raw = text
            else:
                st.warning("Please upload a file or enter text.")
                st.stop()

            model = init_model(st.secrets["apikey"])

            prompt = f"""{prompt_instruction}

User input:
{raw}
"""

            with st.spinner("Analyzing..."):
                result = model.generate(prompt=prompt)
                output = result["results"][0]["generated_text"]

            translated = translate_text(output, lang, model)

            st.markdown("## 🌟 Recommendation")
            st.markdown(translated)

handle_tab(tab1, 
    "You are a study abroad planning expert. Based on the user's description, recommend the most suitable countries (up to 3) and project types (e.g., research-based, practice-oriented, brand-driven). Use a refined and graceful tone.",
    "input1")

handle_tab(tab2,
    "You are an expert in application coaching. Please evaluate the following resume or background information and suggest how to structure it for a successful application.",
    "input2")

handle_tab(tab3,
    "You are an academic transcript analysis expert. Based on the following courses and grades, analyze the applicant's academic strengths and weaknesses and suggest suitable schools or programs.",
    "input3")

handle_tab(tab4,
    "You are a top-tier university admissions strategist. Based on the background provided, recommend the most suitable application identity archetype (Academic Thinker, Creative Synthesizer, Practical Visionary, Cultural Curator, Global Identity Builder) and explain why.",
    "input4")
