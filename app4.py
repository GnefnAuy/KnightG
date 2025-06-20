# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 20:48:51 2025

@author: yf1623
"""

import streamlit as st
import fitz
import re
import pandas as pd
from ibm_watsonx_ai.client import APIClient
from ibm_watsonx_ai.foundation_models import ModelInference

# 🔐 IBM watsonx Credentials (Inline)
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

# === Helpers ===
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

# === Streamlit App ===
st.caption("🔬 Powered by KnightAI | IBM watsonx backend")
st.title("📄 AI University Recommender")

st.sidebar.title("KnightG Menu")
page = st.sidebar.radio("Select Page", ["Transcript Analyzer", "Profile Advisor"])

if page == "Transcript Analyzer":
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

        # Export as CSV
        df = pd.DataFrame(results)
        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇️ Download All Results (CSV)",
            data=csv_data,
            file_name="transcript_analysis_summary.csv",
            mime="text/csv"
        )

elif page == "Profile Advisor":
    st.header("🧐 AI Profile Evaluator")

    name = st.text_input("Name")
    gpa = st.text_input("GPA (e.g., 3.7)")
    test_score = st.text_input("Language Score (e.g., IELTS 7.5)")
    major = st.text_input("Preferred Major")
    extras = st.text_area("Other Info (Projects, Awards, Background)")

    if st.button("Analyze Profile"):
        with st.spinner("🧠 Thinking with Watsonx..."):
            profile_result = analyze_profile(name, gpa, test_score, major, extras)
        st.success("🎓 Profile Analysis Complete")
        st.text_area("Result", profile_result, height=350)
