import streamlit as st
from datetime import datetime

# Streamlit app UI
st.title('College Information Assistant')

# Placeholder for user query
query = "Example query for testing"

# Placeholder for results
results = [
    {"school.name": "Example College", "school.city": "Sample City", "school.state": "CA", "latest.admissions.admission_rate.overall": 0.75},
    {"school.name": "Test University", "school.city": "Demo City", "school.state": "TX", "latest.admissions.admission_rate.overall": 0.65}
]

# Display results
if results:
    st.write("Results found for:", query)
    for college in results:
        st.write(f"Name: {college['school.name']}, City: {college['school.city']}, State: {college['school.state']}, Admission Rate: {college['latest.admissions.admission_rate.overall']}")

    # Create form after displaying the results
    st.write("Displaying form...")
    with st.form("user_details_form"):
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
            form_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "dob": dob.strftime("%Y-%m-%d"),
                "graduation_year": graduation_year,
                "zip_code": zip_code,
                "interested_schools": interested_schools
            }
            st.write("Form data submitted:")
            st.write(form_data)
else:
    st.write("No results found for:", query)
