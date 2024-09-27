import streamlit as st

from state_of_the_art.tables.user_table import UserTable

st.title("Login page")

c1, c2 = st.columns([1, 6])
with c1:
    st.write("Dont have an account?")
with c2:
    st.link_button("Create account", "/signup_page")

email = st.text_input("Email")
password = st.text_input("Password")

if st.button("Login"):
    UserTable().add_user(email, password)
    st.success("Account created successfully")
