import streamlit as st
import requests
import os
import joblib
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai

# Load and configure API key
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Function to fetch college data
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
    return response.json().get('results', [])

# Initialize chat history and load previous chats
try:
    past_chats = joblib.load('data/past_chats_list')
except FileNotFoundError:
    past_chats = {}

# Sidebar for past chats
with st.sidebar:
    chat_id = st.selectbox('Pick a past chat', options=[f'New Chat - {time.time()}'] + list(past_chats.keys()), index=0)
    if 'chat' not in st.session_state or st.session_state.chat_id != chat_id:
        st.session_state.chat_id = chat_id
        st.session_state.messages = past_chats.get(chat_id, [])

st.title('College Information Hub')

# User interaction for college data
college_name = st.text_input('Enter the name of the college for data:')
if st.button('Search Colleges'):
    if college_name:
        results = get_college_data(college_name)
        if results:
            for college in results:
                st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")
        else:
            st.write("No results found")

# AI Chatbot interaction
st.header('Ask the AI Chatbot')
user_input = st.text_input("What would you like to know?")
if st.button('Ask AI Chatbot') and user_input:
    if user_input not in st.session_state.messages:
        st.session_state.messages.append(user_input)
        response = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY).generate(messages=[{'role': 'user', 'content': user_input}])
        st.session_state.messages.append(response)
        st.write(response)

# Save chat to history
joblib.dump(st.session_state.messages, f'data/{st.session_state.chat_id}_chat_messages')
