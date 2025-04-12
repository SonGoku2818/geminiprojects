from dotenv import load_dotenv
load_dotenv() ## loading all the environment variables

import streamlit as st
import os
import google.generativeai as genai

# Configure generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Gemini Pro model and get responses
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

# Function to determine if the question is IT-related and respond if it is
def handle_it_question(question):
    classification_prompt = (
        "You are an AI expert. Determine if the following question is related to the IT field, "
        "which includes areas such as AI, ML, software development, web development, networking, data science, etc. "
        "If it is IT-related, provide a detailed response. If not, say 'Sorry, out of context question.'\n\n"
        f"Question: {question}\n"
    )
    response = chat.send_message(classification_prompt, stream=True)
    final_response = ""
    for chunk in response:
        final_response += chunk.text
    return final_response

# Function to log user questions
def log_question(question):
    with open("abc.txt", "a") as log_file:
        log_file.write(question + "\n")

# Initialize Streamlit app
st.set_page_config(page_title="Q&A Demo")
st.header("Gemini LLM Application")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

input = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

if submit and input:
    log_question(input)  # Log the user's question

    response = handle_it_question(input)
    st.session_state['chat_history'].append(("You", input))
    st.subheader("The Response is")
    st.write(response)
    st.session_state['chat_history'].append(("Bot", response))

st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")
