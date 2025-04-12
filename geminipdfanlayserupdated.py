import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
# Use standard FAISS import if possible, otherwise keep specific one if needed
# from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS # More common import path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import io # Needed for PdfReader with uploaded files

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Basic check for API key
if not api_key:
    st.error("Google API Key not found. Please set it in your .env file or environment variables.")
    st.stop()

try:
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"Error configuring Google Generative AI: {e}")
    st.stop()

# --- Core Functions ---

def get_pdf_text(pdf_docs):
    """Extracts text from a list of uploaded PDF files."""
    text = ""
    if not pdf_docs:
        return ""
    for pdf in pdf_docs:
        try:
            # PyPDF2 reads file-like objects
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text: # Add text only if extraction was successful
                    text += page_text
        except Exception as e:
            st.warning(f"Could not read text from {pdf.name}: {e}. It might be scanned or corrupted.")
            # Optionally skip the file or handle differently
    return text

def get_text_chunks(text):
    """Splits text into manageable chunks."""
    if not text:
        return []
    # Smaller chunk size might be better for detailed retrieval and staying within context limits
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    """Creates and saves a FAISS vector store from text chunks."""
    if not text_chunks:
        st.warning("No text chunks found to create vector store.")
        return False # Indicate failure
    try:
        # Ensure model name is correct, "models/embedding-001" is common
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        vector_store.save_local("faiss_index")
        return True # Indicate success
    except Exception as e:
        st.error(f"Error creating vector store: {e}")
        return False

def get_conversational_chain():
    """Creates the Q&A chain with an improved prompt."""

    # Modified prompt to encourage explanation and synthesis
    prompt_template = """
    Based on the provided context from the document(s), answer the following question.
    Do not just copy text verbatim. Explain the answer in your own words while staying true to the information in the context.
    If the answer cannot be found or inferred from the provided context, clearly state that the information is not available in the document(s).
    Do not provide speculative or incorrect answers.

    Context:\n{context}\n
    Question: \n{question}\n

    Answer:
    """

    # Use a generally capable model like gemini-pro. Adjust temperature for more creativity.
    # Temperature 0.5-0.7 might yield more explanatory results than 0.3
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.6)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    # "stuff" chain is simple but can hit token limits with large contexts.
    # Consider "map_reduce" or "refine" for very large documents if needed.
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def analyze_sentiment_chain():
    """Creates a chain specifically for sentiment analysis."""
    prompt_template = """
    Analyze the overall sentiment of the following text.
    Describe the dominant sentiment (e.g., Positive, Negative, Neutral, Mixed) and briefly explain why, citing examples from the text if possible.

    Text:\n{text}\n

    Sentiment Analysis:
    """
    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.4) # Slightly lower temp for analysis
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])
    # For analysis, we might not need a specific chain type like load_qa_chain,
    # we can invoke the model directly with the prompt, but using a chain keeps consistency.
    # We'll create a simple chain structure manually for this.
    # This is a simplified approach; a dedicated sentiment analysis model might be better
    # but this uses the existing LLM.

    # Langchain LCEL (Langchain Expression Language) approach
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser

    sentiment_chain = (
        {"text": RunnablePassthrough()} # Pass the input text directly
        | prompt
        | model
        | StrOutputParser()
    )
    return sentiment_chain


def handle_user_input(user_question):
    """Processes user question, retrieves context, and gets answer."""
    if 'vector_store_ready' not in st.session_state or not st.session_state.vector_store_ready:
        st.warning("Please upload and process PDF files first.")
        return

    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        # Load the vector store
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True) # Be cautious with this flag
        # Retrieve relevant documents
        docs = new_db.similarity_search(user_question, k=5) # Retrieve top 5 relevant chunks

        if not docs:
            st.write("Reply: Could not find relevant information in the documents for your question.")
            return

        # Get the Q&A chain
        chain = get_conversational_chain()

        # Run the chain
        response = chain(
            {"input_documents": docs, "question": user_question},
            return_only_outputs=True
        )

        # Display the response
        st.write("Reply: ", response["output_text"])

    except FileNotFoundError:
         st.error("Could not find the 'faiss_index'. Please process the PDF files again.")
    except Exception as e:
        st.error(f"An error occurred during question processing: {e}")


def perform_sentiment_analysis():
    """Performs sentiment analysis on the full text stored in session state."""
    if 'raw_text' not in st.session_state or not st.session_state.raw_text:
        st.warning("Please upload and process PDF files first to analyze sentiment.")
        return

    if not st.session_state.raw_text.strip():
         st.warning("No text was extracted from the PDFs to analyze.")
         return

    st.subheader("Sentiment Analysis")
    with st.spinner("Analyzing sentiment..."):
        try:
            chain = analyze_sentiment_chain()
            # Provide the full text stored in session state
            # Limit text length if necessary to avoid exceeding model token limits
            max_len = 20000 # Adjust based on model context window and typical PDF size
            text_to_analyze = st.session_state.raw_text[:max_len]
            if len(st.session_state.raw_text) > max_len:
                 st.info(f"Analyzing sentiment on the first {max_len} characters due to length limitations.")

            response = chain.invoke(text_to_analyze)
            st.write(response)
        except Exception as e:
            st.error(f"An error occurred during sentiment analysis: {e}")


# --- Streamlit App ---

def main():
    st.set_page_config(page_title="Chat & Analyze PDF", layout="wide")
    st.header("Chat with & Analyze PDF using Gemini💁")

    # Initialize session state variables
    if 'vector_store_ready' not in st.session_state:
        st.session_state.vector_store_ready = False
    if 'raw_text' not in st.session_state:
        st.session_state.raw_text = ""

    # --- Sidebar for PDF Upload and Processing ---
    with st.sidebar:
        st.title("Menu:")
        pdf_docs = st.file_uploader("Upload PDF Files", accept_multiple_files=True, type=["pdf"])

        if st.button("Process Uploaded PDFs"):
            if pdf_docs:
                with st.spinner("Processing PDFs... Extracting text, chunking, embedding..."):
                    # 1. Extract Text
                    st.session_state.raw_text = get_pdf_text(pdf_docs)
                    if not st.session_state.raw_text.strip():
                         st.error("No text could be extracted from the provided PDF(s). They might be image-based or empty.")
                         st.session_state.vector_store_ready = False # Reset flag
                    else:
                        # 2. Get Text Chunks
                        text_chunks = get_text_chunks(st.session_state.raw_text)
                        if not text_chunks:
                            st.warning("Text was extracted, but could not be split into chunks.")
                            st.session_state.vector_store_ready = False # Reset flag
                        else:
                            # 3. Create Vector Store
                            success = get_vector_store(text_chunks)
                            if success:
                                st.session_state.vector_store_ready = True
                                st.success("Processing Complete! Vector store created.")
                            else:
                                st.error("Failed to create vector store.")
                                st.session_state.vector_store_ready = False # Reset flag
            else:
                st.warning("Please upload at least one PDF file.")

        # Add Sentiment Analysis Button (enabled only after processing)
        if st.session_state.get('vector_store_ready', False): # Check if processed
             if st.button("Analyze Sentiment of PDFs"):
                 perform_sentiment_analysis() # Call the analysis function defined above
        else:
             st.info("Process PDFs to enable Sentiment Analysis.")


    # --- Main Area for Q&A ---
    st.subheader("Ask Questions about the PDF Content")
    user_question = st.text_input("Your question:")

    if user_question:
        handle_user_input(user_question)


if __name__ == "__main__":
    main()