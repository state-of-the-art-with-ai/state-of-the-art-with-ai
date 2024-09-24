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



st.markdown("### Debug shell")

shell_cmd = st.text_input("Shell command")

if shell_cmd:
    st.write(subprocess.check_output(shell_cmd, shell=True, text=True))




