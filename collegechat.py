import streamlit as st
import requests
import google.generativeai as genai

genai.configure(api_key=st.secrets["google_gen_ai"]["api_key"])

banned_keywords = ['politics', 'violence', 'gambling', 'drugs', 'alcohol']

def is_query_allowed(query):
    query_words = query.lower().split()
    return not any(keyword in query_words for keyword in banned_keywords)

def interpret_query(query):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    try:
        response = chat.send_message(query)
        return response.text.strip()
    except genai.StopCandidateException:
        return "I'm unable to process your query due to content restrictions. Please modify your query."

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
    return None

st.title('College Information Assistant')
query = st.text_input("Ask about colleges:")

if st.button("Ask"):
    if query:
        if not is_query_allowed(query):
            st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
        else:
            interpreted_query = interpret_query(query)
            if interpreted_query == "I'm unable to process your query due to content restrictions. Please modify your query.":
                st.error(interpreted_query)
            else:
                results = fetch_college_data(interpreted_query)
                if results:
                    for college in results:
                        st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")
                else:
                    st.write("No results found for your query. Please check the name or try a different query.")
    else:
        st.error("Please enter a query.")
