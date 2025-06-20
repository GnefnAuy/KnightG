# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 21:40:14 2025

@author: yf1623
"""

import streamlit as st
import fitz
import re
import pandas as pd
from ibm_watsonx_ai.client import APIClient
from ibm_watsonx_ai.foundation_models import ModelInference

# === IBM Watsonx Credentials ===
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

# === Helper Functions ===
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def extract_gpa(text):
    match = re.search(r"GPA[:\s]*([0-4]\.\d{1,2})", text, re.IGNORECASE)
    return float(match.group(1)) if match else None

def recommend_programs_ibm(text, gpa):
    prompt = f"""
You are a global university admissions advisor.

Student transcript below:
{text}

1. Identify the likely major.
2. Assess academic strength.
3. Suggest 3–5 top-fit universities.
4. Give 2 tips to improve the application.

GPA: {gpa}
Be clear, concise, and specific.
"""
    result = model.generate(prompt)
    if isinstance(result, dict) and "results" in result:
        return result["results"][0].get("generated_text", "⚠️ No result.")
    return str(result)

def analyze_profile(name, gpa, test_score, major, extras):
    prompt = f"""
You are a university admissions advisor.

Student name: {name}
GPA: {gpa}
Language score: {test_score}
Preferred major: {major}
Other background: {extras}

Please:
1. Identify best-fit countries and programs.
2. Estimate admission difficulty.
3. Give top 3 personalized suggestions to strengthen the profile.
"""
    result = model.generate(prompt)
    if isinstance(result, dict) and "results" in result:
        return result["results"][0].get("generated_text", "⚠️ No result.")
    return str(result)

# === Page Styling ===
st.set_page_config(page_title="KnightG | AI University Recommender", layout="wide", page_icon="🎓")
st.markdown("""
    <style>
    body {
        background-color: #eaf4ff;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# === Branding ===
st.image("logo.png", width=100)  # Make sure 'logo.png' exists in the same folder as app7.py
st.title("KnightG – AI University Recommender")
st.caption("🔬 Powered by Watsonx | Built by KnightG Team")

# === Sidebar ===
st.sidebar.title("KnightG Menu")
page = st.sidebar.radio("Choose Page", ["Transcript Analyzer", "Profile Advisor"])

# === Transcript Analyzer Page ===
if page == "Transcript Analyzer":
    st.header("📄 Transcript Analyzer")
    uploaded_files = st.file_uploader("Upload Transcript PDF(s)", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        results = []
        for uploaded in uploaded_files:
            st.info(f"📘 Processing: {uploaded.name}")
            text = extract_text_from_pdf(uploaded)
            gpa = extract_gpa(text)

            if gpa:
                st.success(f"✅ GPA Found: {gpa}")
            else:
                st.warning("⚠️ GPA not found.")

            with st.spinner("🔍 Analyzing with IBM Watsonx..."):
                result = recommend_programs_ibm(text, gpa)

            st.text_area(f"🎓 Recommendation for {uploaded.name}:", result, height=300)

            results.append({
                "filename": uploaded.name,
                "gpa": gpa,
                "recommendation": result
            })

        df = pd.DataFrame(results)
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Results (CSV)",
            data=csv_data,
            file_name="transcript_recommendations.csv",
            mime="text/csv"
        )

# === Profile Advisor Page ===
elif page == "Profile Advisor":
    st.header("🧠 Profile Advisor")

    name = st.text_input("👤 Name")
    gpa = st.text_input("📊 GPA (e.g. 3.85)")
    test_score = st.text_input("📄 Language Score (e.g. IELTS 7.5 / TOEFL 105)")
    major = st.text_input("🎯 Target Major")
    extras = st.text_area("🏅 Other Background (Internships, Awards, Projects)")

    if st.button("Run Analysis"):
        with st.spinner("🔍 Thinking with Watsonx..."):
            profile_result = analyze_profile(name, gpa, test_score, major, extras)
        st.success("✅ Profile Analysis Complete")
        st.text_area("🎓 Recommendation Result:", profile_result, height=400)
