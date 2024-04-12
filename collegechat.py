import streamlit as st
import requests
import google.generativeai as genai

# Initialize Google Gemini with API Key
genai.configure(api_key=st.secrets["google_gen_ai"]["api_key"])

# Example of a function to use Google Gemini
def interpret_query(query):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    response = chat.send_message(query)
    return response

# Function to fetch data from the College Scorecard API
def fetch_college_data(keyword):
    url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
    params = {
        'api_key': st.secrets["college_scorecard"]["api_key"],
        'school.name': keyword,
        'fields': 'school.name,school.city,school.state,latest.admissions.admission_rate.overall'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    return None

st.title('College Information Assistant')
query = st.text_input("Ask about colleges:")

if st.button("Ask"):
    if query:
        # Interpret the query with Gemini
        gemini_response = interpret_query(query)
        # Assuming the response contains keywords to search
        keyword = gemini_response.text.strip()  # Simplified assumption
        results = fetch_college_data(keyword)
        if results:
            for college in results:
                st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")
        else:
            st.write("No results found for:", keyword)
    else:
        st.error("Please enter a query.")
