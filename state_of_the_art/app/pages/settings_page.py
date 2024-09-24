import os
from state_of_the_art.tables.user_table import UserTable
import streamlit as st
import subprocess 
from state_of_the_art.ci_cd import S3

st.title("Settings")

if st.button("Pull latest data"):
    with st.status("Pulling data"):
        for log in S3().pull_data():
            st.write(log)

if st.button("Push data"):
    with st.spinner("Pushing data"):
        S3().push_local_data()



import streamlit as st

st.markdown("### Debug shell")

shell_cmd = st.text_input("Shell command")

if shell_cmd:
    p = subprocess.Popen(shell_cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, error  = p.communicate()

    st.write(error)
    st.write(out)




def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if UserTable().check_password("root", st.session_state["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop() 


st.title("After password")