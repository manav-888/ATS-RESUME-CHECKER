import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini API
def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input)
    return response.text

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text

# Function to parse the response string
def parse_response(response):
    jd_match = response.split('"JD Match":"')[1].split('"')[0]
    missing_keywords = response.split('"MissingKeywords":[')[1].split(']')[0].replace('"', '')
    profile_summary = response.split('"Profile Summary":"')[1].split('"}')[0]
    return jd_match, missing_keywords, profile_summary

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage matching based 
on JD and
the missing keywords with high accuracy
resume:{text}
description:{jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords:[]","Profile Summary":""}}
"""

# Streamlit app
st.set_page_config(page_title="Smart ATS", layout="wide")
st.title("Smart ATS: Improve Your Resume for ATS")

st.markdown("### Upload Your Resume and Paste the Job Description to Get Started")

# Use columns to organize the input fields
col1, col2 = st.columns(2)

with col1:
    jd = st.text_area("Paste the Job Description", help="Copy and paste the job description you want to match your resume with.")

with col2:
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf", help="Please upload your resume in PDF format.")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None and jd.strip() != "":
        with st.spinner("Processing..."):
            resume_text = input_pdf_text(uploaded_file)
            prompt = input_prompt.format(text=resume_text, jd=jd)
            response = get_gemini_response(prompt)
            jd_match, missing_keywords, profile_summary = parse_response(response)

        # Display the results in an organized manner
        st.success("Analysis Complete!")
        
        st.markdown("### Results")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("JD Match")
            st.metric(label="Match Percentage", value=jd_match)
        
        with col2:
            st.subheader("Missing Keywords")
            st.write(missing_keywords if missing_keywords else "None")
        
        st.subheader("Profile Summary")
        st.write(profile_summary)
    else:
        st.error("Please upload a resume and paste a job description.")
