import streamlit as st
import requests

# Define keywords or topics related to the College Scorecard data
allowed_topics = ['admission', 'tuition', 'graduation rate', 'financial aid', 'student population']

def is_query_relevant(query):
    """Check if the query contains allowed keywords."""
    return any(topic in query.lower() for topic in allowed_topics)

def fetch_college_scorecard_data(query):
    """Simulated function to fetch data from College Scorecard."""
    # This could be an API call or a database query depending on your setup
    return "Simulated response based on College Scorecard data."

def ask_gemini(query):
    """Ask a Gemini model and return the response."""
    # Assuming you have a function to send queries to the Gemini model
    return "Response from Gemini based on the query."

st.title("College Information Assistant")
user_query = st.text_input("Ask me about college statistics:")

if st.button("Ask"):
    if is_query_relevant(user_query):
        # Fetch data directly related to College Scorecard
        response = fetch_college_scorecard_data(user_query)
        st.write(response)
    else:
        # Optionally ask Gemini or give a predefined message
        st.write("Please ask questions relevant to college statistics such as admission, tuition, etc.")
