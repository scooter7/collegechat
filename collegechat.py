import streamlit as st
import requests
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

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
    try:
        data = response.json()
        return data['results'] if 'results' in data else []
    except JSONDecodeError as e:
        st.error(f"Failed to decode JSON: {e}")
        return []

def ask_google(context, question):
    model = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=st.secrets["google_gen_ai"]["api_key"], temperature=0.3)
    messages = [{'role': 'user', 'content': question}]
    response = model.generate(messages=messages)
    return response.text.strip()

st.title('College Information Hub')

st.header('College Scorecard Search')
college_name = st.text_input('Enter the name of the college for data:', key="college_search")
if st.button('Search Colleges', key="search_button"):
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

st.header('Ask About Colleges via AI Chatbot')
context = st.text_area("Context for your question:", "Type the context here...")
question = st.text_input("Your question:", "Type your question here...")
if st.button('Ask AI Chatbot', key="ask_button"):
    if context and question:
        answer = ask_google(context, question)
        st.write(answer)
    else:
        st.error("Please provide both context and a question.")
