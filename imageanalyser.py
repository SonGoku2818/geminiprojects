import streamlit as st
from PIL import Image
import google.generativeai as genai
import os
import time
from io import BytesIO
import base64
import json
from datetime import datetime
import glob
from dotenv import load_dotenv  # Added for .env support

# Load environment variables from .env file
load_dotenv()

# Configure the app
st.set_page_config(
    page_title="Gemini Flash 2.0 Image Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")  # Create a style.css file in the same directory

# History directory setup
HISTORY_DIR = "chat_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# Initialize Gemini using environment variable
def initialize_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("No GEMINI_API_KEY found in environment variables")
    
    genai.configure(api_key=api_key)
    
    # Get model name from .env or default to gemini-1.5-flash
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    return genai.GenerativeModel(model_name)

# Function to display image with animation
def display_image(image):
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.image(image, caption="Uploaded Image", use_column_width=True)

# Function to get image description
def get_image_description(model, image):
    with st.spinner('Analyzing image...'):
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_data = base64.b64encode(img_bytes.getvalue()).decode()
        
        response = model.generate_content([
            "Describe this image in detail. Include objects, colors, actions, and any text present.",
            {"mime_type": "image/png", "data": img_data}
        ])
        return response.text

# Function to answer questions
def answer_question(model, image, question, history):
    with st.spinner('Generating answer...'):
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_data = base64.b64encode(img_bytes.getvalue()).decode()
        
        # Include chat history for context
        context = "\n".join([f"Q: {q}\nA: {a}" for q, a in history])
        
        prompt = f"""
        Context from previous conversation:
        {context}
        
        New question: {question}
        
        Answer the question based on the image and previous context.
        """
        
        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": img_data}
        ])
        return response.text

# Function to save conversation to history
def save_to_history(description, history, image_name=None):
    if not image_name:
        image_name = f"image_{int(time.time())}"
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{HISTORY_DIR}/{image_name}_{timestamp}.json"
    
    data = {
        "image_name": image_name,
        "timestamp": timestamp,
        "description": description,
        "conversation": history
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filename

# Function to load history files
def load_history_files():
    files = glob.glob(f"{HISTORY_DIR}/*.json")
    files.sort(key=os.path.getmtime, reverse=True)
    return files

# Function to load a specific history file
def load_history_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Function to display history in sidebar
def display_history_sidebar():
    with st.sidebar:
        st.markdown("## 📜 Conversation History")
        
        history_files = load_history_files()
        
        if not history_files:
            st.info("No history available yet.")
            return None
        
        selected_file = st.selectbox(
            "Select a past conversation:",
            options=history_files,
            format_func=lambda x: os.path.basename(x).replace('.json', ''),
            key="history_selector"
        )
        
        if st.button("Load Selected Conversation"):
            return selected_file
        
        return None

# Main app function
def main():
    # Sidebar with dark theme
    with st.sidebar:
        st.title("🔑 Menu")
        
        # Display history section
        file_to_load = display_history_sidebar()
        
        st.markdown("---")
        st.markdown("### How to use:")
        st.markdown("1. Upload an image")
        st.markdown("2. View the automatic description")
        st.markdown("3. Ask questions about the image")
        st.markdown("4. Conversations are automatically saved")
        
        st.markdown("---")
        st.markdown("Made with [Gemini Flash 2.0](https://ai.google.dev/)")

    # Main content area
    st.title("🔍 Gemini Flash 2.0 Image Analyzer")
    st.markdown("Upload an image and get a detailed description with AI analysis!")

    try:
        model = initialize_gemini()
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        st.info("Please create a .env file with your GEMINI_API_KEY")
        return
    except Exception as e:
        st.error(f"Error initializing Gemini: {e}")
        return
    
    # Check if loading from history
    if file_to_load:
        try:
            history_data = load_history_file(file_to_load)
            
            st.success(f"Loaded conversation from {history_data['timestamp']}")
            
            # Display the description
            with st.expander("📝 Image Description", expanded=True):
                st.markdown(f"<div class='description-box'>{history_data['description']}</div>", unsafe_allow_html=True)
            
            # Display the conversation history
            st.markdown("## 💬 Previous Conversation")
            
            for q, a in history_data['conversation']:
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    st.markdown(a)
            
            # Don't process new image if loading history
            return
            
        except Exception as e:
            st.error(f"Error loading history: {e}")
    
    # File uploader with custom styling
    uploaded_file = st.file_uploader(
        "Choose an image...", 
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=False,
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            image_name = uploaded_file.name.split('.')[0]  # Get filename without extension
            
            # Display the uploaded image with animation
            display_image(image)
            
            # Initialize session state for chat history
            if 'history' not in st.session_state:
                st.session_state.history = []
            
            if 'description' not in st.session_state:
                st.session_state.description = get_image_description(model, image)
            
            # Display description in an expandable section
            with st.expander("📝 Image Description", expanded=True):
                st.markdown(f"<div class='description-box'>{st.session_state.description}</div>", unsafe_allow_html=True)
                
                # Download button for description
                st.download_button(
                    label="Download Description",
                    data=st.session_state.description,
                    file_name=f"{image_name}_description.txt",
                    mime="text/plain",
                    key="desc_download"
                )
            
            # Question-answer section
            st.markdown("## 💬 Ask About the Image")
            
            # Display chat history
            for q, a in st.session_state.history:
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    st.markdown(a)
            
            # Input for new question
            question = st.chat_input("Ask a question about the image...")
            
            if question:
                # Add user question to chat
                with st.chat_message("user"):
                    st.markdown(question)
                
                # Get and display answer
                answer = answer_question(model, image, question, st.session_state.history)
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                
                # Update history
                st.session_state.history.append((question, answer))
                
                # Save to history after each question
                save_to_history(
                    st.session_state.description,
                    st.session_state.history,
                    image_name
                )
                
        except Exception as e:
            st.error(f"Error processing image: {e}")

if __name__ == "__main__":
    main()