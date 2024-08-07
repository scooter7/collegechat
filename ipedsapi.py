import streamlit as st
from datetime import datetime
import google.generativeai as genai
from pypeds import ipeds
import pandas as pd
import json
from github import Github
import re

# Initialize API Keys
genai_api_key = st.secrets.get("google_gen_ai", {}).get("api_key", None)
github_token = st.secrets.get("github", {}).get("token", None)

if not genai_api_key:
    st.error("Google Gemini API key is missing.")
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

# Function to fetch data from IPEDS using pypeds
def fetch_ipeds_data(years):
    try:
        # Instantiate the survey of interest
        hd = ipeds.HD(years=years)
        # Extract, or download the surveys
        hd.extract()
        # Load the surveys as a pandas dataframe
        df = hd.load()
        return df
    except Exception as e:
        st.error(f"Error fetching IPEDS data: {e}")
        return pd.DataFrame()

# Function to filter IPEDS data based on relevant school names
def filter_ipeds_data(ipeds_data, relevant_schools):
    if ipeds_data.empty or not relevant_schools:
        return pd.DataFrame()
    pattern = '|'.join(relevant_schools)
    filtered_data = ipeds_data[ipeds_data['INSTNM'].str.contains(pattern, case=False, na=False)]
    return filtered_data

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
years = st.multiselect("Select years for IPEDS data:", options=list(range(2000, 2024)), default=[2022, 2023])

if st.button("Ask"):
    if query:
        if not is_query_allowed(query):
            st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
        else:
            try:
                # Interpret the query using Google Gemini
                gemini_response_text = interpret_query(query)
                st.write(f"Bot Response: {gemini_response_text}")

                # Extract school names from the bot response
                relevant_schools = list(set(re.findall(r'\b[\w\s]+University\b|\b[\w\s]+College\b', gemini_response_text)))
                relevant_schools = [school.strip() for school in relevant_schools if school.strip()]

                # Display the extracted school names
                st.write("Extracted Schools:", relevant_schools)

                # Fetch data from IPEDS using pypeds
                ipeds_data = fetch_ipeds_data(years)

                # Filter the IPEDS data based on the relevant school names
                filtered_ipeds_data = filter_ipeds_data(ipeds_data, relevant_schools)
                st.write("Filtered IPEDS Data:", filtered_ipeds_data)

                # Save conversation history to GitHub
                history = {
                    "timestamp": datetime.now().isoformat(),
                    "query": query,
                    "response": gemini_response_text,
                    "relevant_schools": relevant_schools,
                    "filtered_ipeds_data": filtered_ipeds_data.to_dict(orient='records')  # Convert DataFrame to dict for JSON serialization
                }
                save_conversation_history_to_github(history)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.write("Please enter a query.")
