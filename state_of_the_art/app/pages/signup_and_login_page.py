import streamlit as st

from state_of_the_art.tables.user_table import UserTable

st.title("Sign up")

st.button("Alread have an account? Log in")

email = st.text_input("Email")
password = st.text_input("Password")

if st.button("Create account"):
    UserTable().add_user(email, password)
    st.success("Account created successfully")
