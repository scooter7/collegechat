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
    st.write("Checking if the query contains banned keywords...")
    result = not any(keyword in query.lower() for keyword in banned_keywords)
    st.write(f"Query allowed: {result}")
    return result

# Function to interpret the query using Google Gemini
def interpret_query(query):
    model = genai.GenerativeModel("gemini-pro")
    chat = model.start_chat(history=[])
    response = chat.send_message(query)
    return response

# Function to fetch data from the College Scorecard API
def fetch_college_data(state, keyword):
    st.write(f"Fetching college data for state: {state}, keyword: {keyword}...")
    url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
    params = {
        'api_key': college_scorecard_api_key,
        'school.state': state,
        'school.name': keyword,
        'fields': 'school.name,school.city,school.state,latest.admissions.admission_rate.overall'
    }
    response = requests.get(url, params=params)
    st.write(f"College Scorecard API response status code: {response.status_code}")
    if response.status_code == 200:
        results = response.json().get('results', [])
        st.write(f"College Scorecard API results: {results}")
        return results
    else:
        st.write("Failed to fetch data from College Scorecard API")
        st.write(f"Response: {response.text}")
    return []

# Function to save conversation history to GitHub
def save_conversation_history_to_github(history):
    st.write("Saving conversation history to GitHub...")
    file_content = json.dumps(history, indent=4)
    file_name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    repo_name = "scooter7/collegechat"  # Replace with your repository name
    folder_path = "data"  # Folder in the repository

    st.write(f"File content: {file_content}")
    st.write(f"File name: {file_name}")
    st.write(f"Repository name: {repo_name}")
    st.write(f"Folder path: {folder_path}")

    # Initialize Github instance
    try:
        g = Github(github_token)
        st.write("GitHub instance created.")
        repo = g.get_repo(repo_name)
        st.write(f"Authenticated to GitHub repository: {repo_name}")

        # Check if the folder exists
        try:
            contents = repo.get_contents(folder_path)
            st.write(f"Folder {folder_path} exists in the repository.")
        except:
            st.write(f"Folder {folder_path} does not exist in the repository. Creating the folder.")
            repo.create_file(f"{folder_path}/.gitkeep", "Create folder", "")
        
        # Create the file in the repo
        repo.create_file(f"{folder_path}/{file_name}", f"Add {file_name}", file_content)
        st.write(f"File {file_name} saved to GitHub repository {repo_name}")
    except Exception as e:
        st.write(f"Failed to save file to GitHub: {e}")
        st.write(f"Error details: {e}")

# Streamlit app UI
st.title('College Information Assistant')

query = st.text_input("Ask about colleges:")
submitted_query = st.session_state.get('submitted_query', '')

if st.button("Ask"):
    if query:
        st.session_state['submitted_query'] = query
        submitted_query = query
        st.session_state['relevant_schools'] = []  # Reset the relevant schools list
        st.write("New query submitted, relevant_schools reset.")

if submitted_query:
    st.write(f"User query: {submitted_query}")
    if not is_query_allowed(submitted_query):
        st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
    else:
        # Interpret the query with Gemini
        try:
            gemini_response = interpret_query(submitted_query)
            keyword = gemini_response.text.strip()  # Simplified assumption
            st.write(f"Using keyword from Gemini: {keyword}")
        except Exception as e:
            st.write(f"Error interacting with Gemini: {e}")
            keyword = "engineering"  # Fallback keyword

        if not keyword:
            keyword = "engineering"  # Fallback keyword

        # Extract the state and keyword from the user query
        state = ""
        if "in" in submitted_query:
            parts = re.split(r'\bin\b', submitted_query)
            keyword = parts[0].strip()
            state_match = re.search(r'\b(\w{2})\b', parts[1])
            if state_match:
                state = state_match.group(1).upper()
            else:
                state = ""

        st.write(f"State: {state}, Keyword: {keyword}")  # Debug statement
        results = fetch_college_data(state, keyword)
        if results:
            relevant_schools = [college['school.name'] for college in results]
            st.session_state['relevant_schools'] = relevant_schools
        else:
            st.session_state['relevant_schools'] = ["No schools found"]

        st.write(f"Relevant schools: {st.session_state['relevant_schools']}")  # Debug statement

# Display form regardless of results
if 'relevant_schools' in st.session_state and st.session_state['relevant_schools']:
    st.write(f"Session state relevant schools: {st.session_state['relevant_schools']}")  # Debug statement
    with st.form(key="user_details_form"):
        st.write("Please fill out the form below to learn more about the colleges.")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email Address")
        dob = st.date_input("Date of Birth")
        graduation_year = st.number_input("High School Graduation Year", min_value=1900, max_value=datetime.now().year, step=1)
        zip_code = st.text_input("5-digit Zip Code")
        interested_schools = st.multiselect(
            "Schools you are interested in learning more about:",
            st.session_state['relevant_schools']
        )
        st.write(f"Options in multiselect: {st.session_state['relevant_schools']}")  # Debug statement
        st.write(f"Selected schools before submit: {interested_schools}")  # Debug statement
        submit_button = st.form_submit_button("Submit")

        if submit_button:
            st.write("Form submitted")
            form_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "dob": dob.strftime("%Y-%m-%d"),
                "graduation_year": graduation_year,
                "zip_code": zip_code,
                "interested_schools": interested_schools
            }
            st.write("Form data: ", form_data)  # Debugging form data

            # Save conversation history to GitHub
            history = {
                "timestamp": datetime.now().isoformat(),
                "query": submitted_query,
                "results": st.session_state['relevant_schools'],
                "form_data": form_data
            }
            save_conversation_history_to_github(history)
            st.success("Your information has been submitted successfully.")
else:
    st.write("No schools found. Please ask a different query.")
