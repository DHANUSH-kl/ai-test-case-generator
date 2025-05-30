import streamlit as st
import requests
from docx import Document

st.title("🧪 AI Test Case Generator")
st.markdown("Upload your **SRS document** to generate test cases using AI.")

uploaded_file = st.file_uploader("Upload SRS (.txt or .docx)", type=["txt", "docx"])

srs_text = ""

if uploaded_file:
    if uploaded_file.name.endswith(".txt"):
        srs_text = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        srs_text = "\n".join([para.text for para in doc.paragraphs])

    st.subheader("📄 Extracted SRS Content:")
    st.text_area("SRS", srs_text, height=300)

    if st.button("Generate Test Cases"):
        with st.spinner("Generating test cases..."):
            response = requests.post("http://localhost:8000/generate_test_cases", json={"srs": srs_text})
            if response.status_code == 200:
                test_cases = response.json().get("test_cases", [])
                st.subheader("✅ Generated Test Cases")
                for i, tc in enumerate(test_cases, 1):
                    st.write(f"**TC-{i:03}:** {tc}")
            else:
                st.error("Failed to generate test cases.")
