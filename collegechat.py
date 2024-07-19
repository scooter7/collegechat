import streamlit as st
from datetime import datetime

# Streamlit app UI
st.title('College Information Assistant')

# Temporary static results for testing purposes
results = [
    {"school.name": "Engineering College A", "school.city": "City A", "school.state": "State A", "latest.admissions.admission_rate.overall": 0.5},
    {"school.name": "Engineering College B", "school.city": "City B", "school.state": "State B", "latest.admissions.admission_rate.overall": 0.6}
]

st.write("Displaying form below to learn more about the colleges.")
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
        st.success("Your information has been submitted successfully.")
