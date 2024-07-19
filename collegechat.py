from github import Github
from datetime import datetime
import json

def save_test_file_to_github():
    test_data = {
        "timestamp": datetime.now().isoformat(),
        "message": "This is a test file to verify GitHub saving functionality."
    }
    
    file_content = json.dumps(test_data, indent=4)
    file_name = f"test_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    repo_name = "scooter7/collegechat"  # Replace with your repository name
    folder_path = "data"  # Folder in the repository

    g = Github("YOUR_NEW_GITHUB_TOKEN")  # Use the new token directly
    repo = g.get_repo(repo_name)
    
    try:
        print(f"Attempting to save test file to GitHub: {file_name}")
        repo.create_file(f"{folder_path}/{file_name}", f"Add {file_name}", file_content)
        print(f"Test file {file_name} saved to GitHub repository {repo_name}")
    except Exception as e:
        print(f"Error saving test file to GitHub: {e}")

save_test_file_to_github()
