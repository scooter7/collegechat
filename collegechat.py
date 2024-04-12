import streamlit as st
import requests
import google.generativeai as genai

# Initialize Google Gemini with API Key
genai.configure(api_key=st.secrets["google_gen_ai"]["api_key"])

# List of banned keywords
banned_keywords = ['politics', 'violence', 'gambling', 'drugs', 'alcohol']

def is_query_allowed(query):
    # Check if the query contains any banned keywords
    return not any(keyword in query.lower() for keyword in banned_keywords)

# Example of a function to use Google Gemini
def interpret_query(query):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    response = chat.send_message(query)
    return response.text.strip() if response.text.strip() else "Please refine your query or try a different question."

# Function to fetch data from the College Scorecard API
def fetch_college_data(keyword):
    url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
    params = {
        'api_key': st.secrets["college_scorecard"]["api_key"],
        'school.name': keyword,
        'fields': 'school.name,school.city,school.state,latest.admissions.admission_rate.overall'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200 and response.json().get('results'):
        return response.json().get('results', [])
    return None

st.title('College Information Assistant')
query = st.text_input("Ask about colleges:")

if st.button("Ask"):
    if query:
        if not is_query_allowed(query):
            st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
        else:
            gemini_response = interpret_query(query)
            if gemini_response == "Please refine your query or try a different question.":
                st.error(gemini_response)
            else:
                results = fetch_college_data(gemini_response)
                if results:
                    for college in results:
                        st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")
    else:
        st.error("Please enter a query.")
