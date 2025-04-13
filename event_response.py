import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_event_response(event_description, question):
    """Fetch response for the event-specific question."""
    prompt = (
        f"You are an expert on the following event. "
        f"Only use the description provided to answer questions: \n"
        f"{event_description}\n\n"
        f"Answer questions strictly related to this event.\n\n"
        f"Question: {question}"
    )
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content([prompt])
    return response.text