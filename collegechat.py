import streamlit as st
import requests
import google.generativeai as genai

# Initialize Google Gemini with API Key
genai.configure(api_key=st.secrets["google_gen_ai"]["api_key"])

def interpret_query(query):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    response = chat.send_message(query)
    return response.text.strip()

def fetch_college_data(keyword):
    url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
    params = {
        'api_key': st.secrets["college_scorecard"]["api_key"],
        'school.name': keyword,
        'fields': 'school.name,school.city,school.state,latest.admissions.admission_rate.overall'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json().get('results', [])
        return data
    else:
        # Log the error or handle it appropriately
        return None

st.title('College Information Assistant')
query = st.text_input("Ask about colleges:")

if st.button("Ask"):
    if query:
        interpreted_query = interpret_query(query)
        results = fetch_college_data(interpreted_query)
        if results:
            for college in results:
                st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")
        else:
            # Instead of showing a potentially confusing message with the keyword, show a more generic error message.
            st.write("No results found for your query. Please check the name or try a different query.")
    else:
        st.error("Please enter a query.")
