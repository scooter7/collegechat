import streamlit as st
import requests
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Configure the Google API (assuming it has been set elsewhere or does not need to be in secrets)
api_key = st.secrets["google_gen_ai"]["api_key"]
genai.configure(api_key=api_key)

# Function to fetch college data from the College Scorecard API
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

# Function to ask questions to Google's Gemini Pro via LangChain
def ask_google(question):
    model = ChatGoogleGenerativeAI(model="gemini-pro", client=genai, temperature=0.3)
    response = model.generate(prompt=question)
    return response.text.strip()

st.title('College Information Hub')

# College Scorecard Search Section
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

# Google Gemini Pro Chatbot Section
st.header('Ask About Colleges via AI Chatbot')
user_query = st.text_input("Ask me anything about colleges:", key="chatbot_query")
if st.button('Ask AI Chatbot', key="ask_button"):
    if user_query:
        with st.spinner('Getting response...'):
            answer = ask_google(user_query)
            st.write(answer)
    else:
        st.error("Please enter a question to ask the chatbot.")
