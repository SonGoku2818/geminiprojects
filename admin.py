import os
import json
import streamlit as st

EVENTS_FILE = "events.json"

def save_events_to_file(events):
    """Save events to a JSON file."""
    with open(EVENTS_FILE, "w") as file:
        json.dump(events, file)

def load_events_from_file():
    """Load events from a JSON file."""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, "r") as file:
            return json.load(file)
    return {}

def admin_page():
    """Admin page for managing events."""
    st.title("Admin Panel: Manage Events")

    # Load existing events
    events = load_events_from_file()

    # Add or update events
    with st.form("add_event_form"):
        event_name = st.text_input("Event Name")
        event_description = st.text_area("Event Description")
        submitted = st.form_submit_button("Add/Update Event")

        if submitted:
            if event_name and event_description:
                events[event_name] = event_description
                save_events_to_file(events)
                st.success(f"Event '{event_name}' added/updated successfully!")
            else:
                st.error("Please fill in all fields.")

    # Display existing events
    if events:
        st.subheader("Existing Events")
        for event_name in list(events.keys()):
            with st.expander(event_name):
                st.write(events[event_name])
                if st.button(f"Delete '{event_name}'", key=f"delete_{event_name}"):
                    del events[event_name]
                    save_events_to_file(events)
                    st.success(f"Event '{event_name}' deleted.")
                    st.experimental_rerun()

if __name__ == "__main__":
    admin_page()
