import os
from state_of_the_art.tables.user_table import UserTable
import streamlit as st
import subprocess 
from state_of_the_art.ci_cd import S3

st.title("Settings")

c1, c2 = st.columns([1, 1])
with c1:
    if st.button("Pull latest data"):
        with st.status("Pulling data"):
            for log in S3().pull_data():
                st.write(log)
with c2:
    if st.button("Push data"):
        with st.spinner("Pushing data"):
            out, error = S3().push_local_data()
            st.write(error)
            st.write(out)



st.markdown("### Debug shell")

shell_cmd = st.text_input("Shell command")

if shell_cmd:
    p = subprocess.Popen(shell_cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, error  = p.communicate()

    st.write(error)
    st.write(out)

def check_password():
    """Returns `True` if the user had the correct password."""

    if st.session_state.get("password_correct") == True:
        return True

    def password_entered(password):
        """Checks whether a password entered by the user is correct."""
        if UserTable().check_password("root", password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    password = st.text_input(
        "Password", type="password", key="password"
    )
    if password:
        password_entered(password)

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop() 


st.title("After password")