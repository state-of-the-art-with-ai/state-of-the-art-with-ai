import streamlit as st

st.title("Sign up")

st.button("Alread have an account? Log in")

email = st.text_input("Email")
password = st.text_input("Password")

if st.button("Create account")
    st.success("Account created successfully")
