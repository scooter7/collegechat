import streamlit as st
from datetime import datetime
import requests
import openai
import pypeds
import json
from github import Github
import re

# Initialize API Keys
openai_api_key = st.secrets.get("openai", {}).get("api_key", None)
github_token = st.secrets.get("github", {}).get("token", None)

if not openai_api_key:
    st.error("OpenAI API key is missing.")
if not github_token:
    st.error("GitHub token is missing.")

# Initialize OpenAI with API Key
openai.api_key = openai_api_key

# List of banned keywords
banned_keywords = ['politics', 'violence', 'gambling', 'drugs', 'alcohol']

def is_query_allowed(query):
    return not any(keyword in query.lower() for keyword in banned_keywords)

# Function to interpret the query using OpenAI
def interpret_query(query):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"User asked: {query}\nAnswer using IPEDS data:",
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Function to fetch data from IPEDS using pypeds
def fetch_ipeds_data(query):
    try:
        # Example IPEDS query using pypeds (adjust based on pypeds capabilities)
        data = pypeds.get_data(query)  # Replace with actual function and parameters
        return data
    except Exception as e:
        st.error(f"Error fetching IPEDS data: {e}")
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
st.title('IPEDS Data Chatbot')

query = st.text_input("Ask about colleges:")

if st.button("Ask"):
    if query:
        if not is_query_allowed(query):
            st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
        else:
            try:
                # Interpret the query using OpenAI
                gemini_response_text = interpret_query(query)
                st.write(f"Bot Response: {gemini_response_text}")

                # Fetch data from IPEDS using pypeds
                ipeds_data = fetch_ipeds_data(query)
                st.write("IPEDS Data:", ipeds_data)

                # Save conversation history to GitHub
                history = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "response": gemini_response_text,
                    "ipeds_data": ipeds_data
                }
                save_conversation_history_to_github(history)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.write("Please enter a query.")
