import streamlit as st
from datetime import datetime
import requests
import google.generativeai as genai
import json
from github import Github
import re

# Initialize API Keys
genai_api_key = st.secrets.get("google_gen_ai", {}).get("api_key", None)
college_scorecard_api_key = st.secrets.get("college_scorecard", {}).get("api_key", None)
github_token = st.secrets.get("github", {}).get("token", None)

if not genai_api_key:
    st.error("Google Gemini API key is missing.")
if not college_scorecard_api_key:
    st.error("College Scorecard API key is missing.")
if not github_token:
    st.error("GitHub token is missing.")

# Initialize Google Gemini with API Key
genai.configure(api_key=genai_api_key)

# List of banned keywords
banned_keywords = ['politics', 'violence', 'gambling', 'drugs', 'alcohol']

def is_query_allowed(query):
    return not any(keyword in query.lower() for keyword in banned_keywords)

# Function to interpret the query using Google Gemini with chunking
def interpret_query(query):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    chunks = [query[i:i+1000] for i in range(0, len(query), 1000)]
    responses = []
    for chunk in chunks:
        response = chat.send_message(chunk)
        if hasattr(response, 'text'):
            responses.append(response.text)
        else:
            st.error(f"Error interacting with Gemini: {getattr(response, 'finish_reason', 'Unknown error')}")
            break
    return ' '.join(responses)

# Function to fetch data from the College Scorecard API
def fetch_college_data(state, keyword):
    url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
    params = {
        'api_key': college_scorecard_api_key,
        'school.state': state,
        'school.name': keyword,
        'fields': 'school.name,school.city,school.state,latest.admissions.admission_rate.overall'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

# Function to save conversation history to GitHub
def save_conversation_history_to_github(history):
    file_content = json.dumps(history, indent=4)
    file_name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    repo_name = "scooter7/collegechat"  # Replace with your repository name
    folder_path = "data"  # Folder in the repository

    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)

        # Check if the folder exists, if not create it
        try:
            repo.get_contents(folder_path)
        except:
            repo.create_file(f"{folder_path}/.gitkeep", "Create folder", "")

        # Create the file in the repo
        repo.create_file(f"{folder_path}/{file_name}", f"Add {file_name}", file_content)
    except Exception as e:
        st.error(f"Failed to save file to GitHub: {e}")

# Streamlit app UI
st.title('College Information Assistant')

query = st.text_input("Ask about colleges:")
submitted_query = st.session_state.get('submitted_query', '')

if st.button("Ask"):
    if query:
        st.session_state['submitted_query'] = query
        submitted_query = query

if submitted_query:
    if not is_query_allowed(submitted_query):
        st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
    else:
        gemini_response_text = ""
        relevant_schools = []

        try:
            gemini_response_text = interpret_query(submitted_query)
            st.write(f"Bot Response: {gemini_response_text}")  # Display the bot response
            # Extract unique, valid school names
            relevant_schools = list(set(re.findall(r'\b[\w\s]+University\b|\b[\w\s]+College\b', gemini_response_text)))
            relevant_schools = [school for school in relevant_schools if school.strip() and school != " College"]
            # Initialize relevant_schools in session state if not already present
            if 'relevant_schools' not in st.session_state:
                st.session_state['relevant_schools'] = relevant_schools
            else:
                st.session_state['relevant_schools'] = list(set(st.session_state['relevant_schools'] + relevant_schools))
        except Exception as e:
            st.error(f"Error interacting with Gemini: {e}")

        # Define state and keyword with default values
        state = ""
        keyword = "engineering"  # Default fallback keyword

        if not relevant_schools:
            if "in" in submitted_query:
                parts = re.split(r'\bin\b', submitted_query)
                if len(parts) > 1:
                    keyword = parts[0].strip()
                    state_match = re.search(r'\b(\w{2})\b', parts[1])
                    if state_match:
                        state = state_match.group(1).upper()

            results = fetch_college_data(state, keyword)
            if results:
                for college in results:
                    school_name = college['school.name']
                    if school_name not in relevant_schools:
                        relevant_schools.append(school_name)
                    st.write(f"Name: {school_name}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")
            else:
                st.write(f"No results found for: {keyword}")

        # Debugging: Check the extracted school names
        st.write("Extracted Schools:", st.session_state['relevant_schools'])

# Ensure session state is initialized for selected schools
if 'selected_schools' not in st.session_state:
    st.session_state['selected_schools'] = []

# Display checkboxes for school selection outside the form
if 'relevant_schools' in st.session_state and st.session_state['relevant_schools']:
    st.write("Select the schools you are interested in:")
    for school in st.session_state['relevant_schools']:
        if school not in st.session_state:
            st.session_state[school] = False
        st.session_state[school] = st.checkbox(school, value=st.session_state[school])
        if st.session_state[school]:
            if school not in st.session_state['selected_schools']:
                st.session_state['selected_schools'].append(school)
        else:
            if school in st.session_state['selected_schools']:
                st.session_state['selected_schools'].remove(school)

# Always show form for user details and selected schools
with st.form(key="user_details_form"):
    st.write("Please fill out the form below to learn more about the colleges.")
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email Address")
    dob = st.date_input("Date of Birth")
    graduation_year = st.number_input("High School Graduation Year", min_value=1900, max_value=datetime.now().year, step=1)
    zip_code = st.text_input("5-digit Zip Code")

    submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not st.session_state['selected_schools']:
            st.error("Please select at least one school to continue.")
        else:
            form_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "dob": dob.strftime("%Y-%m-%d"),
                "graduation_year": graduation_year,
                "zip_code": zip_code,
                "interested_schools": st.session_state['selected_schools']
            }

            # Save conversation history to GitHub
            history = {
                "timestamp": datetime.now().isoformat(),
                "query": submitted_query,
                "results": st.session_state.get('relevant_schools', []),
                "form_data": form_data
            }
            save_conversation_history_to_github(history)
            st.success("Your information has been submitted successfully.")

        # Debugging: Check selected schools after submission
        st.write("Selected Schools (after check):", st.session_state['selected_schools'])
