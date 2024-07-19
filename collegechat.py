import streamlit as st
from datetime import datetime
import json
from github import Github

# Initialize keys and tokens
genai_api_key = st.secrets.get("google_gen_ai", {}).get("api_key", None)
college_scorecard_api_key = st.secrets.get("college_scorecard", {}).get("api_key", None)
github_token = st.secrets.get("github", {}).get("token", None)

if not genai_api_key:
    st.error("Google Gemini API key is missing.")
if not college_scorecard_api_key:
    st.error("College Scorecard API key is missing.")
if not github_token:
    st.error("GitHub token is missing.")

# Dummy data for relevant schools
relevant_schools = [
    "University of Minnesota - Twin Cities",
    "Augsburg University",
    "Carleton College",
    "Hamline University",
    "Macalester College",
    "Saint Mary's University of Minnesota",
    "Saint Olaf College",
    "University of Saint Thomas"
]

# Store relevant schools in session state if not already set
if 'relevant_schools' not in st.session_state:
    st.session_state['relevant_schools'] = relevant_schools

# Streamlit app UI
st.title('College Information Assistant')

# Display form
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
    st.write(f"Options in multiselect: {st.session_state['relevant_schools']}")
    st.write(f"Selected schools before submit: {interested_schools}")
    submit_button = st.form_submit_button("Submit")

if submit_button:
    st.write("Form submitted")
    st.write(f"Selected schools after submit: {interested_schools}")
    form_data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "dob": dob.strftime("%Y-%m-%d"),
        "graduation_year": graduation_year,
        "zip_code": zip_code,
        "interested_schools": interested_schools
    }
    st.write("Form data before saving: ", form_data)  # Debugging form data

    # Save form_data in session state
    st.session_state["form_data"] = form_data

    # Display form data for debugging purposes
    st.json(form_data)

# Function to save conversation history to GitHub
def save_conversation_history_to_github(history):
    st.write("Saving conversation history to GitHub...")
    file_content = json.dumps(history, indent=4)
    file_name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    repo_name = "scooter7/collegechat"  # Replace with your repository name
    folder_path = "data"  # Folder in the repository

    st.write(f"File content:\n{file_content}")
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

# Add a button to save the conversation history to GitHub for testing purposes
if st.button("Save to GitHub"):
    # Example static history data
    history = {
        "timestamp": datetime.now().isoformat(),
        "query": "graduate physics programs in Minnesota",
        "response_text": "University of Minnesota - Twin Cities\n\n* Ph.D. in Physics\n* Master of Science (M.S.) in Physics\n\nAugsburg University\n\n* Master of Science in Applied Physics\n\nCarleton College\n\n* Bachelor of Arts (B.A.) in Physics\n* Minor in Physics\n\nHamline University\n\n* Bachelor of Arts (B.A.) in Physics\n\nMacalester College\n\n* Bachelor of Arts (B.A.) in Physics\n* Minor in Physics\n\nSaint Mary's University of Minnesota\n\n* Master of Science in Teaching Physics\n* Minor in Physics\n\nSaint Olaf College\n\n* Bachelor of Arts (B.A.) in Physics\n* Minor in Physics\n\nUniversity of Saint Thomas\n\n* Master of Science in Medical Physics\n* Minor in Physics",
        "form_data": st.session_state.get("form_data", {})
    }
    st.write(f"History to be saved: {history}")
    save_conversation_history_to_github(history)
