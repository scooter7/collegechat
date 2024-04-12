import streamlit as st
import requests
import google.generativeai as genai

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Configure Google API using Streamlit's secrets management
genai.configure(api_key=st.secrets["google_gen_ai"]["api_key"])

# Function to fetch college data from College Scorecard API
def get_college_data(name):
    url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
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

# Start a new chat session with the Gemini model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_response(question):
    # This ensures that the input is formatted as expected by the model
    response = chat.send_message(question, stream=True)
    full_response = ''
    for chunk in response:
        full_response += chunk.text + ' '
    return full_response.strip()

st.title('College Information Hub')

# College Scorecard Search
st.header('College Scorecard Search')
college_name = st.text_input('Enter the name of the college for data:')
if st.button('Search Colleges'):
    if college_name:
        results = get_college_data(college_name)
        if results:
            for college in results:
                st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")
        else:
            st.write("No results found")
    else:
        st.error("Please enter a college name")

# AI Chatbot Interface
st.header('Ask the AI Chatbot')
question = st.text_input("What would you like to know about colleges?")
if st.button('Ask AI Chatbot'):
    if question:
        response = get_response(question)
        st.session_state['chat_history'].append(("You", question))
        st.session_state['chat_history'].append(("Bot", response))
        st.write(response)
    else:
        st.error("Please enter a question to ask the chatbot.")

st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    st.markdown(f"**{role}:** {text}")
