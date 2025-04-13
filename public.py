import os
import json
import streamlit as st
import google.generativeai as genai
from event_response import get_event_response,EVENTS_FILE,load_events_from_file

# Load environment variables


def public_page():
    """Public page for event-specific Q&A."""
    st.title("Event Q&A Bot")

    # Load events
    events = load_events_from_file()
    if not events:
        st.warning("No events available. Please check back later.")
        return

    # Event selection
    selected_event = st.selectbox("Select an Event", list(events.keys()))
    question = st.text_input("Ask a question about this event:")

    if st.button("Submit Question"):
        if question:
            response = get_event_response(events[selected_event], question)
            st.subheader("Response")
            st.write(response)
        else:
            st.error("Please enter a question.")



if __name__ == "__main__":
    public_page()
