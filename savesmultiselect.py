import streamlit as st
from datetime import datetime
import json

# Mocked function to save conversation history to GitHub (for testing purposes)
def save_conversation_history_to_github(history):
    st.write("Saving conversation history to GitHub...")
    file_content = json.dumps(history, indent=4)
    st.write(f"File content: {file_content}")

# Streamlit app UI
st.title('College Information Assistant')

# Mock relevant schools
relevant_schools = [
    "Harvard University",
    "Stanford University",
    "Massachusetts Institute of Technology",
    "California Institute of Technology",
    "Princeton University"
]

st.session_state['relevant_schools'] = relevant_schools

# Form for user details and selecting interested schools
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
        st.session_state.get('relevant_schools', [])
    )
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
        st.write("Form data: ", form_data)  # Debugging form data

        # Save conversation history to GitHub
        history = {
            "timestamp": datetime.now().isoformat(),
            "query": "Mock query for testing",
            "results": [],
            "form_data": form_data
        }
        save_conversation_history_to_github(history)
        st.success("Your information has been submitted successfully.")
