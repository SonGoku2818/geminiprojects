from dotenv import load_dotenv
import os
import streamlit as st
import google.generativeai as genai

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def setup_css():
    """Add custom CSS for styling"""
    st.markdown(
        """
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f9f9f9;
            }
            .main-header {
                text-align: center;
                color: #4A90E2;
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            .button-container {
                display: flex;
                justify-content: center;
                margin-top: 2rem;
            }
            .custom-button {
                background-color: #4A90E2;
                color: white;
                padding: 0.8rem 1.5rem;
                font-size: 1rem;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 0 10px;
            }
            .custom-button:hover {
                background-color: #357ABD;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def admin_page():
    """Admin page for managing events"""
    st.subheader("Admin Panel: Manage Events")

    if "events" not in st.session_state:
        st.session_state["events"] = {}

    with st.form("add_event_form"):
        event_name = st.text_input("Event Name")
        event_description = st.text_area("Event Description")
        submitted = st.form_submit_button("Add/Update Event")

        if submitted:
            if event_name and event_description:
                st.session_state["events"][event_name] = event_description
                st.success(f"Event '{event_name}' added/updated successfully!")
            else:
                st.error("Please fill in all fields.")

    if st.session_state["events"]:
        st.subheader("Existing Events")
        for event_name in list(st.session_state["events"].keys()):
            with st.expander(event_name):
                if st.button(f"Delete '{event_name}'", key=f"delete_{event_name}"):
                    del st.session_state["events"][event_name]
                    st.success(f"Event '{event_name}' deleted.")
                    st.experimental_rerun()

def public_page():
    """Public page for event-specific Q&A"""
    st.subheader("Event Q&A Bot")

    if "events" not in st.session_state or not st.session_state["events"]:
        st.warning("No events available. Please check back later.")
        return

    selected_event = st.selectbox("Select an Event", list(st.session_state["events"].keys()))

    question = st.text_input("Ask a question about this event:")
    if st.button("Submit Question"):
        if question:
            response = get_event_response(selected_event, question)
            st.subheader("Response")
            st.write(response)
        else:
            st.error("Please enter a question.")

def get_event_response(event_name, question):
    """Fetch response for the event-specific question"""
    event_description = st.session_state["events"].get(event_name, "")
    prompt = (
        f"You are an expert on the event '{event_name}'. Only use the following description to answer questions: \n"
        f"{event_description}\n\n"
        f"Answer questions strictly related to this event and do not use any other source of information.\n\n"
        f"Question: {question}"
    )
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([prompt])
    return response.text

def main():
    setup_css()
    st.markdown("<div class='main-header'>Event Q&A Bot</div>", unsafe_allow_html=True)

    mode = st.radio("Select Mode", ("Public", "Admin"), key="mode_selector")

    if mode == "Admin":
        admin_page()
    elif mode == "Public":
        public_page()

if __name__ == "__main__":
    main()
