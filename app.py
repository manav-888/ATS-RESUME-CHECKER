from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

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
    jd_match = response.split('"JD Match":"')[1].split('"')[0].strip('%')
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
{{"JD Match":"","MissingKeywords":[ ],"Profile Summary":""}}
"""

# Flask route for the homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        jd = request.form['job_description']
        resume_file = request.files['resume']

        if resume_file and jd.strip():
            # Extract text from uploaded PDF
            resume_text = input_pdf_text(resume_file)
            
            # Create the prompt for the Gemini API
            prompt = input_prompt.format(text=resume_text, jd=jd)
            
            # Get response from the Gemini API
            response = get_gemini_response(prompt)
            
            # Parse the response
            jd_match, missing_keywords, profile_summary = parse_response(response)
            
            # Return the results to the user
            return render_template('result.html', jd_match=jd_match, missing_keywords=missing_keywords, profile_summary=profile_summary)
    
    # On GET request, show the upload form
    return render_template('index.html')

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
