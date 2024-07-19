import streamlit as st
from datetime import datetime
import json

# Dummy data for relevant schools
relevant_schools = [
    "University of Minnesota, Twin Cities",
    "University of Minnesota, Duluth",
    "Saint Mary's University of Minnesota",
    "Carleton College",
    "Hamline University",
    "University of Wisconsin-Eau Claire",
    "University of Wisconsin-River Falls",
    "University of Wisconsin-Stout",
    "University of Wisconsin-Superior",
    "North Dakota State University"
]

# Store the relevant schools in session state
if 'relevant_schools' not in st.session_state:
    st.session_state['relevant_schools'] = relevant_schools

# Streamlit app UI
st.title('College Information Assistant')

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

        # Display form data for debugging purposes
        st.json(form_data)

# Save conversation history to GitHub
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
        from github import Github
        github_token = st.secrets.get("github", {}).get("token", None)
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
    history = {
        "timestamp": datetime.now().isoformat(),
        "query": "graduate physics programs in Minnesota",
        "response_text": "University of Minnesota, Twin Cities\n\n* Department of Physics and Astronomy\n* PhD in Physics\n* MS in Physics\n* MA in Physics Education\n\nUniversity of Minnesota, Duluth\n\n* Department of Physics and Astronomy\n* MS in Physics\n* MA in Physics Education\n\nSaint Mary's University of Minnesota\n\n* Department of Physics, Mathematics, and Computer Science\n* MS in Physics\n\nCarleton College\n\n* Department of Physics and Astronomy\n* MA in Physics (for educators)\n\nHamline University\n\n* Department of Physics and Astronomy\n* AAPT Master of Arts in Physics (for educators)\n\nOther Programs in the Region\n\n* University of Wisconsin-Eau Claire: MA in Physics Education\n* University of Wisconsin-River Falls: MA in Physics Education\n* University of Wisconsin-Stout: MS in Physics (for educators)\n* University of Wisconsin-Superior: MS in Physics (for educators)\n* North Dakota State University: MS in Physics",
        "form_data": form_data
    }
    st.write(f"History to be saved: {history}")
    save_conversation_history_to_github(history)
