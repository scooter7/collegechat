import streamlit as st
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

def get_college_data(name):
    url = 'http://api.data.gov/ed/collegescorecard/v1/schools'
    params = {
        'api_key': st.secrets["college_scorecard"]["api_key"],
        'school.name': name,
        'fields': 'school.name,school.city,school.state,latest.admissions.admission_rate.overall'
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        st.error(f"Failed to fetch data: {response.status_code} {response.text}")
        return []
    data = response.json()
    return data['results'] if 'results' in data else []

def ask_google(question):
    google_api_key = st.secrets["google_gen_ai"]["api_key"]
    genai.configure(api_key=google_api_key)
    model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key, temperature=0.3)
    messages = [{'role': 'user', 'content': question}]
    response = model.generate(messages=messages)
    return response.text.strip()

st.title('College Information Hub')

st.header('College Scorecard Search')
college_name = st.text_input('Enter the name of the college for data:')
if st.button('Search Colleges'):
    if college_name:
        results = get_college_data(college_name)
        if results:
            for college in results:
                st.write(f"Name: {college['school.name']}")
                st.write(f"City: {college['school.city']}")
                st.write(f"State: {college['school.state']}")
                st.write(f"Admission Rate: {college['latest.admissions.admission_rate.overall']}")
        else:
            st.write("No results found")
    else:
        st.error("Please enter a college name")

st.header('Ask the AI Chatbot')
question = st.text_input("What would you like to know?")
if st.button('Ask'):
    if question:
        answer = ask_google(question)
        st.write(answer)
    else:
        st.error("Please enter a question to ask the chatbot.")
