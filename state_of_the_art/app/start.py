import subprocess
import streamlit as st

from state_of_the_art.tables.data_sync_table import PushHistory

pages = {
    "Discover new Papers": [
        st.Page("pages/your_papers_page.py", title="Your Papers"),
        st.Page("pages/papers_recommended_page.py", title="New Papers Recommendations"),
        st.Page("pages/interests_page.py", title="Your Interests"),
        st.Page("pages/all_papers_page.py", title="All Papers"),
        #st.Page("pages/papers_report_page.py", title="Past Recomendations"),
        st.Page("pages/paper_details_page.py", title="Paper details "),
    ],
    "Settings": [
        st.Page("pages/admin_page.py", title="Admin"),
    ]
}


pg = st.navigation(pages)
st.set_page_config(layout="wide")

with st.sidebar:
    p = subprocess.Popen('uptime', shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, error  = p.communicate()
    time_up = out.split(" up ")[1].split(",")[0]
    st.markdown("#### Uptime: " + time_up)
    minutes = PushHistory().minutes_since_last_push()
    st.markdown("#### Min Since Last Push: " + str(round(minutes, 2)))




pg.run()
