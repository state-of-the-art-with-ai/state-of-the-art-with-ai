from state_of_the_art.app.utils.login_utils import LoggedInUser
from state_of_the_art.infrastructure.s3 import S3
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.tables.data_sync_table import PushHistory
import streamlit as st
from state_of_the_art.tables.text_feedback_table import TextFeedbackTable

@st.dialog("Admin panel")
def admin_panel():
    import subprocess

    tab1, tab2, tab3 = st.tabs(["Stats & Shell", 'Actions', "Logs"])

    with tab1:
        st.text("Authenticated user details: " + str(LoggedInUser.get_instance().get_uuid()))
        st.write(f"Number of feedbacks: {TextFeedbackTable().len()}")

        p = subprocess.Popen("free -h", shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, error  = p.communicate()
        st.write(f"Memory: {out}, {error}")

        p = subprocess.Popen(
            "uptime", shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        out, error = p.communicate()
        time_up = out.split(" up ")[1].split(",")[0]
        st.markdown("#### Uptime: " + time_up)
        minutes = PushHistory().minutes_since_last_push()
        hours = int(minutes / 60)
        remaining_minutes = round(minutes % 60)

        st.markdown(f"#### Time since last push: {hours} hours {remaining_minutes} minutes")

        st.markdown("### Debug shell")

        shell_cmd = st.text_input("Shell command")
        if shell_cmd:
            with st.spinner("Running shell command"):
                p = subprocess.Popen(
                    shell_cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
                )
                out, error = p.communicate()
                st.write(error)
                st.write(out)
    with tab2:
        if st.button("Mine new papers"):
            with st.spinner("Mining all keywords"):
                ArxivMiner().mine_all_keywords()

        if st.button("Push data"):
            with st.spinner("Pushing data"):
                out, error = S3().push_local_events_data()
                st.write(error)
                st.write(out)

        if st.button("Pull data"):
            with st.spinner("Pushing data"):
                for out in S3().pull_events_data():
                    st.write(out)

    with tab3:
        if st.button("Show recommnder log"):
            with st.spinner("Loading logs"):
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

        if st.button("Show scheduler"):
            with st.spinner("Loading logs"):
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
