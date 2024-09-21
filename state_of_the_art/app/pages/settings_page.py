import streamlit as st
from state_of_the_art.ci_cd import S3

st.title("Settings")

if st.button("Pull latest data"):
    with st.spinner("Pulling data"):
        S3().pull_data()

if st.button("Push data"):
    with st.spinner("Pushing data"):
        S3().push_local_data()


