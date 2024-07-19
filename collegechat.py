import streamlit as st
from datetime import datetime
import json
from github import Github

# Function to save a test file to GitHub
def save_test_file_to_github():
    st.write("Saving test file to GitHub...")
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "message": "This is a test file to verify GitHub saving functionality."
    }
    
    file_content = json.dumps(test_data, indent=4)
    file_name = f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    repo_name = "scooter7/collegechat"  # Replace with your repository name
    folder_path = "data"  # Folder in the repository

    # Initialize Github instance
    g = Github(st.secrets["github"]["token"])
    repo = g.get_repo(repo_name)
    # Create the file in the repo
    try:
        st.write(f"Attempting to save test file to GitHub: {file_name}")
        repo.create_file(f"{folder_path}/{file_name}", f"Add {file_name}", file_content)
        st.write(f"Test file {file_name} saved to GitHub repository {repo_name}")
    except Exception as e:
        st.write(f"Error saving test file to GitHub: {e}")

# Streamlit app UI
st.title('GitHub Save Function Test')

if st.button("Run GitHub Save Test"):
    save_test_file_to_github()
