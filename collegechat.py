import streamlit as st
import json
from datetime import datetime

# Dummy data for relevant schools
relevant_schools = [
    "Columbia Business School",
    "New York University Stern School of Business",
    "Cornell University Johnson Graduate School of Management",
    "Fordham University Gabelli School of Business",
    "CUNY Baruch College Zicklin School of Business",
    "Rochester Institute of Technology Saunders College of Business",
    "Syracuse University Whitman School of Management",
    "Hofstra University Frank G. Zarb School of Business",
    "Long Island University Post C.W. Post Campus School of Professional Studies",
    "Bentley University - New York City Campus",
    "Pace University Lubin School of Business",
    "St. John's University Tobin College of Business"
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
