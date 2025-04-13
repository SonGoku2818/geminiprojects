from dotenv import load_dotenv
import os
import io
import base64
import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def setup_css():
    """Add custom dark theme CSS for styling"""
    st.markdown(
        """
        <style>
            :root {
                --primary: #6C5CE7;
                --secondary: #A29BFE;
                --accent: #00CEFF;
                --dark: #1E1E1E;
                --darker: #121212;
                --light: #E0E0E0;
                --lighter: #F5F5F5;
                --success: #00B894;
                --warning: #FDCB6E;
                --danger: #D63031;
                --text: #E0E0E0;
                --text-secondary: #B0B0B0;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: var(--dark);
                color: var(--text);
            }
            
            .stApp {
                background: var(--darker);
            }
            
            .main-header {
                text-align: center;
                color: var(--primary);
                font-size: 2.8rem;
                margin-bottom: 1.5rem;
                font-weight: 700;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
                padding: 0.5rem;
                background: rgba(30, 30, 30, 0.8);
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .stRadio > div {
                display: flex;
                justify-content: center;
                gap: 1rem;
                margin-bottom: 2rem;
            }
            
            .stRadio > div > label {
                background: rgba(40, 40, 40, 0.8);
                color: var(--text);
                padding: 0.8rem 1.5rem;
                border-radius: 50px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                cursor: pointer;
                border: 2px solid transparent;
            }
            
            .stRadio > div > label:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                background: rgba(50, 50, 50, 0.8);
            }
            
            .stRadio > div > label[data-baseweb="radio"] > div:first-child {
                border-color: var(--primary) !important;
            }
            
            .stRadio > div > label[data-baseweb="radio"] > div:first-child > div {
                background-color: var(--primary) !important;
            }
            
            .custom-button {
                background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
                color: white;
                padding: 0.8rem 1.8rem;
                font-size: 1rem;
                font-weight: 600;
                border: none;
                border-radius: 50px;
                cursor: pointer;
                margin: 0.5rem 0;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .custom-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.3);
                background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
            }
            
            .stFileUploader > div > div {
                border: 2px dashed var(--primary) !important;
                border-radius: 10px !important;
                background: rgba(40, 40, 40, 0.5) !important;
                padding: 2rem !important;
                color: var(--text) !important;
            }
            
            .stFileUploader > div > div:hover {
                border-color: var(--secondary) !important;
                background: rgba(50, 50, 50, 0.5) !important;
            }
            
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea {
                border-radius: 10px !important;
                border: 2px solid rgba(255,255,255,0.1) !important;
                padding: 0.8rem !important;
                background-color: rgba(40, 40, 40, 0.5) !important;
                color: var(--text) !important;
            }
            
            .stTextInput > div > div > input:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: var(--primary) !important;
                box-shadow: 0 0 0 2px rgba(108,92,231,0.3) !important;
                background-color: rgba(50, 50, 50, 0.7) !important;
            }
            
            .stImage {
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                margin: 1rem 0;
                border: 5px solid rgba(40, 40, 40, 0.8);
            }
            
            .stAlert {
                border-radius: 10px !important;
                background-color: rgba(40, 40, 40, 0.8) !important;
                border: 1px solid rgba(255,255,255,0.1) !important;
            }
            
            .stSubheader {
                color: var(--primary) !important;
                font-weight: 600 !important;
                margin-top: 1.5rem !important;
                border-bottom: 2px solid var(--primary);
                padding-bottom: 0.5rem;
            }
            
            .response-container {
                background: rgba(40, 40, 40, 0.8);
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                border-left: 5px solid var(--primary);
                color: var(--text);
            }
            
            .tool-description {
                background: rgba(40, 40, 40, 0.8);
                border-radius: 10px;
                padding: 1rem;
                margin: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                font-size: 0.95rem;
                color: var(--text-secondary);
                border: 1px solid rgba(255,255,255,0.1);
            }
            
            .stSpinner > div > div {
                border-color: var(--primary) transparent transparent transparent !important;
            }
            
            hr {
                border-color: rgba(255,255,255,0.1) !important;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .stMarkdown {
                animation: fadeIn 0.5s ease-out;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: rgba(30, 30, 30, 0.5);
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--primary);
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--secondary);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_gemini_response(input, content, prompt):
    """Fetch response from Gemini 2.0 Flash model."""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([input, content[0], prompt])
    return response.text

def input_image_setup(uploaded_file):
    """Process uploaded image for invoice analysis."""
    bytes_data = uploaded_file.getvalue()
    image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
    return image_parts

def input_pdf_setup(uploaded_file):
    """Process uploaded PDF for resume analysis."""
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    first_page = images[0]
    img_byte_arr = io.BytesIO()
    first_page.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    pdf_parts = [{"mime_type": "image/jpeg", "data": base64.b64encode(img_byte_arr).decode()}]
    return pdf_parts

def show_invoice_analyzer():
    """Render the Invoice Analyzer section with dark theme."""
    st.subheader("📄 Invoice Analyzer")
    st.markdown(
        '<div class="tool-description">Upload an invoice image and ask questions to extract information from it.</div>',
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns([3, 2])
    with col1:
        input_text = st.text_input("What would you like to know about the invoice?", key="invoice_input")
    with col2:
        uploaded_file = st.file_uploader("Choose an invoice image...", type=["jpg", "jpeg", "png"], key="invoice_upload")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Invoice", use_column_width=True)
    
    if st.button("🔍 Analyze Invoice", key="analyze_invoice", help="Click to analyze the uploaded invoice"):
        if uploaded_file and input_text.strip():
            with st.spinner("Analyzing invoice..."):
                try:
                    image_data = input_image_setup(uploaded_file)
                    input_prompt = """
                    You are an expert in understanding invoices.
                    You will receive input images as invoices and answer questions based on the input image.
                    Provide detailed, accurate responses with extracted values when possible.
                    """
                    response = get_gemini_response(input_prompt, image_data, input_text)
                    st.subheader("Analysis Results")
                    st.markdown('<div class="response-container">', unsafe_allow_html=True)
                    st.write(response)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please upload an image and enter a question to analyze.")

def show_resume_analyzer():
    """Render the Resume Analyzer section with dark theme."""
    st.subheader("📝 Resume Analyzer")
    st.markdown(
        '<div class="tool-description">Upload your resume and job description to get a professional evaluation.</div>',
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"], key="resume_upload")
    
    if uploaded_file:
        st.success("✅ Resume uploaded successfully!")
    
    input_text = st.text_area("Paste the job description here:", key="resume_input", height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 Analyze Resume", key="analyze_resume", help="Get detailed evaluation of your resume"):
            if uploaded_file and input_text.strip():
                with st.spinner("Analyzing resume..."):
                    try:
                        pdf_content = input_pdf_setup(uploaded_file)
                        input_prompt = """
                        You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against 
                        the job description, highlight strengths and weaknesses, and provide professional evaluation.
                        Be specific about skills matching and areas for improvement.
                        """
                        response = get_gemini_response(input_prompt, pdf_content, input_text)
                        st.subheader("Resume Evaluation")
                        st.markdown('<div class="response-container">', unsafe_allow_html=True)
                        st.write(response)
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please upload a resume and provide a job description.")
    
    with col2:
        if st.button("📊 Match Percentage", key="match_percentage", help="See how well your resume matches the job"):
            if uploaded_file and input_text.strip():
                with st.spinner("Calculating match..."):
                    try:
                        pdf_content = input_pdf_setup(uploaded_file)
                        input_prompt = """
                        You are a skilled ATS scanner. Evaluate the resume against the provided job description, give the percentage 
                        match, list missing keywords, and provide final thoughts.
                        Format your response with clear sections for percentage, missing keywords, and recommendations.
                        """
                        response = get_gemini_response(input_prompt, pdf_content, input_text)
                        st.subheader("ATS Match Results")
                        st.markdown('<div class="response-container">', unsafe_allow_html=True)
                        st.write(response)
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please upload a resume and provide a job description.")

def main():
    setup_css()
    st.markdown("<div class='main-header'>Gemini Document Analyzer</div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align: center; margin-bottom: 2rem; color: var(--text-secondary); font-size: 1.1rem;">'
        'AI-powered tools for invoice and resume analysis'
        '</div>',
        unsafe_allow_html=True
    )
    
    # Tool selection with animated tabs
    selected_tool = st.radio(
        "Select a tool:",
        ("Invoice Analyzer", "Resume Analyzer"),
        key="tool_selector",
        horizontal=True,
        label_visibility="hidden"
    )
    
    st.markdown("---")
    
    if selected_tool == "Invoice Analyzer":
        show_invoice_analyzer()
    elif selected_tool == "Resume Analyzer":
        show_resume_analyzer()

if __name__ == "__main__":
    main()