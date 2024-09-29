import os
from state_of_the_art.tables.text_feedback_table import TextFeedbackTable
from state_of_the_art.tables.user_table import UserTable
import streamlit as st
import subprocess
from state_of_the_art.infrastructure.s3 import S3

st.title("Settings")

c1, c2 = st.columns([1, 1])
with c1:
    if st.button("Pull latest data"):
        with st.status("Pulling data"):
            for log in S3().pull_events_data():
                st.write(log)
with c2:
    if st.button("Push data"):
        with st.spinner("Pushing data"):
            out, error = S3().push_local_events_data()
            st.write(error)
            st.write(out)

st.markdown("### Stats")
st.write(f"Number of feedbacks: {TextFeedbackTable().len()}")

st.markdown("### Debug shell")

shell_cmd = st.text_input("Shell command")

if shell_cmd:
    p = subprocess.Popen(
        shell_cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, error = p.communicate()

    st.write(error)
    st.write(out)

c1, c2 = st.columns([1, 1])
with c1:
    if st.button("Show recommnder log"):
        with st.expander("Log"):
            import subprocess

            p = subprocess.Popen(
                f"cat /tmp/generator.log",
                shell=True,
                text=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            out, error = p.communicate()
            st.write(error)
            st.write(out)

with c2:
    if st.button("Show scheduler"):
        with st.expander("Log"):
            import subprocess

            p = subprocess.Popen(
                f"cat /tmp/scheduler.log",
                shell=True,
                text=True,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
            out, error = p.communicate()
            st.write(error)
            st.write(out)
