import streamlit as st
from state_of_the_art.tables.text_feedback_table import TextFeedbackTable

@st.dialog("Admin panel")
def admin_panel():
    import subprocess

    tab1, tab2 = st.tabs(["Stats & Shell", "Logs"])

    with tab1:
        st.write(f"Number of feedbacks: {TextFeedbackTable().len()}")


        p = subprocess.Popen("free -h", shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, error  = p.communicate()
        st.write(f"Memory: {out}, {error}")

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
