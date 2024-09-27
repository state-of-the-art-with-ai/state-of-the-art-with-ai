import streamlit as st

from state_of_the_art.tables.user_table import UserTable

st.title("Sign up")

c1, c2 = st.columns([1, 6])
with c1:
    st.write("Already have an account?")
with c2:
    st.link_button("Log in", "/login_page")

email = st.text_input("Email")
password = st.text_input("Password")

if st.button("Create account"):
    UserTable().add_user(email, password)
    st.success("Account created successfully")
