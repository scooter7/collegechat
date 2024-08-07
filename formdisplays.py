import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime
import json
from github import Github

# Initialize Google Gemini with API Key
genai.configure(api_key=st.secrets["google_gen_ai"]["api_key"])

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
def fetch_college_data(keyword):
    st.write(f"Fetching college data for keyword: {keyword}...")
    url = 'https://api.data.gov/ed/collegescorecard/v1/schools'
    params = {
        'api_key': st.secrets["college_scorecard"]["api_key"],
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
    return []

def save_conversation_history_to_github(query, results, form_data):
    st.write("Saving conversation history to GitHub...")
    history = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "results": results,
        "form_data": form_data
    }
    
    file_content = json.dumps(history, indent=4)
    file_name = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    repo_name = "scooter7/collegechat"  # Replace with your repository name
    folder_path = "data"  # Folder in the repository

    # Initialize Github instance
    try:
        g = Github(st.secrets["github"]["token"])
        repo = g.get_repo(repo_name)
        # Create the file in the repo
        repo.create_file(f"{folder_path}/{file_name}", f"Add {file_name}", file_content)
        st.write(f"File {file_name} saved to GitHub repository {repo_name}")
    except Exception as e:
        st.write(f"Failed to save file to GitHub: {e}")

# Streamlit app UI
st.title('College Information Assistant')
query = st.text_input("Ask about colleges:")

if st.button("Ask"):
    st.write("Ask button clicked")
    if query:
        st.write(f"User query: {query}")
        if not is_query_allowed(query):
            st.error("Your query contains topics that I'm not able to discuss. Please ask about colleges and universities.")
        else:
            # Interpret the query with Gemini
            try:
                gemini_response = interpret_query(query)
                keyword = gemini_response.text.strip()  # Simplified assumption
                st.write(f"Using keyword from Gemini: {keyword}")
            except Exception as e:
                st.write(f"Error interacting with Gemini: {e}")
                keyword = "engineering"  # Fallback keyword
            
            if not keyword:
                keyword = "engineering"  # Fallback keyword

            # Ensure the keyword is suitable for API call
            if len(keyword.split()) > 1:
                keyword = keyword.split()[-1]  # Use the last word as a fallback

            results = fetch_college_data(keyword)
            if results:
                st.write(f"Results found for: {keyword}")
                for college in results:
                    st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")

                # Display form directly for debugging
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
                        [college['school.name'] for college in results]
                    )
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
                        save_conversation_history_to_github(query, results, form_data)
                        st.success("Your information has been submitted successfully.")
            else:
                st.write("No results found for:", keyword)
    else:
        st.error("Please enter a query.")
