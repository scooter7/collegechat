import streamlit as st
from datetime import datetime
import requests
import google.generativeai as genai
import json
from github import Github
import re
import os
import bcrypt

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
        st.error(f"Failed to save file to GitHub.")

# Function to load user profile from JSON file
def load_user_profile(username):
    try:
        with open(f"user_profiles/{username}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# Function to save user profile to JSON file
def save_user_profile(username, profile):
    os.makedirs("user_profiles", exist_ok=True)
    with open(f"user_profiles/{username}.json", "w") as f:
        json.dump(profile, f, indent=4)

# Function to hash a password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Function to verify a password
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# Login or Register Screen
def login_screen():
    st.title("Login or Sign Up")
    option = st.selectbox("Select an option", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if option == "Login":
        if st.button("Login"):
            user_profile = load_user_profile(username)
            if user_profile and verify_password(password, user_profile.get("password")):
                st.session_state['username'] = username
                st.session_state['profile'] = user_profile
                st.success("Logged in successfully")
            else:
                st.error("Invalid username or password")
    else:
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email Address")
        dob = st.date_input("Date of Birth", value=datetime.now())
        graduation_year = st.number_input("High School Graduation Year", min_value=1900, max_value=datetime.now().year, step=1)
        zip_code = st.text_input("5-digit Zip Code")

        if st.button("Sign Up"):
            if load_user_profile(username):
                st.error("Username already exists")
            else:
                hashed_password = hash_password(password)
                user_profile = {
                    "username": username,
                    "password": hashed_password,  # Store the hashed password
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "dob": dob.strftime("%Y-%m-%d"),
                    "graduation_year": graduation_year,
                    "zip_code": zip_code,
                    "selected_schools": []
                }
                save_user_profile(username, user_profile)
                st.session_state['username'] = username
                st.session_state['profile'] = user_profile
                st.success("Signed up successfully")

# Main App
def main_app():
    st.title('College Information Assistant')

    if st.button("Logout"):
        del st.session_state['username']
        del st.session_state['profile']
        st.experimental_set_query_params()
        st.stop()

    query = st.text_input("Ask about colleges:")
    submitted_query = st.session_state.get('submitted_query', '')

    if st.button("Ask"):
        if query:
            st.session_state['submitted_query'] = query
            submitted_query = query

            # Reset relevant session state variables
            st.session_state['gemini_response_text'] = ""
            st.session_state['relevant_schools'] = []

    if submitted_query:
        if not is_query_allowed(submitted_query):
            st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
        else:
            gemini_response_text = ""
            relevant_schools = []

            try:
                gemini_response_text = interpret_query(submitted_query)
                st.session_state['gemini_response_text'] = gemini_response_text
                st.write(f"Bot Response: {gemini_response_text}")  # Display the bot response
                # Extract unique, valid school names
                relevant_schools = list(set(re.findall(r'\b[\w\s]+University\b|\b[\w\s]+College\b', gemini_response_text)))
                relevant_schools = [school for school in relevant_schools if school.strip() and school != " College"]
                # Initialize relevant_schools in session state if not already set
                if 'relevant_schools' not in st.session_state or not st.session_state['relevant_schools']:
                    st.session_state['relevant_schools'] = relevant_schools
            except Exception as e:
                st.error(f"Error interacting with Gemini.")

            # Debugging: Check the extracted school names
            st.write("Extracted Schools:", st.session_state['relevant_schools'])

    # Ensure session state is initialized for selected schools
    if 'selected_schools' not in st.session_state:
        st.session_state['selected_schools'] = st.session_state['profile'].get('selected_schools', [])

    # Display the stored bot response if available
    if 'gemini_response_text' in st.session_state:
        st.write(f"Bot Response: {st.session_state['gemini_response_text']}")

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

    # Save the selected schools to the user profile
    st.session_state['profile']['selected_schools'] = st.session_state['selected_schools']
    save_user_profile(st.session_state['username'], st.session_state['profile'])

    # Form to save selected schools
    with st.form(key="school_selection_form"):
        submit_button = st.form_submit_button("Save Selection")

        if submit_button:
            if not st.session_state['selected_schools']:
                st.error("Please select at least one school to continue.")
            else:
                # Save conversation history to GitHub
                history = {
                    "timestamp": datetime.now().isoformat(),
                    "query": submitted_query,
                    "results": st.session_state.get('relevant_schools', []),
                    "form_data": st.session_state['profile']
                }
                save_conversation_history_to_github(history)
                st.success("Your selection has been saved successfully")

            # Debugging: Check selected schools after submission
            st.write("Selected Schools (after check):", st.session_state['selected_schools'])

# Main Logic
if 'username' not in st.session_state:
    login_screen()
else:
    main_app()
