import subprocess
from state_of_the_art.app.utils.paper_details_utils import create_custom_paper
import streamlit as st

st.set_page_config(page_title='State of the Art with AI', layout="wide", initial_sidebar_state='expanded', menu_items=None)

from state_of_the_art.app.utils.login_utils import LoggedInUser, logout, setup_login
from state_of_the_art.infrastructure.s3 import S3
from state_of_the_art.tables.data_sync_table import PushHistory

settings_pages = [
        st.Page("pages/profile_page.py", title="Profile Page"),
]

pages = {
    "Papers": [
        st.Page("pages/all_papers_page.py", title="Browse All"),
        st.Page("pages/interests_page.py", title="Your Interests"),
        st.Page("pages/papers_recommended_page.py", title="Recommendations"),
        st.Page("pages/your_papers_page.py", title="Your Papers"),
        st.Page("pages/paper_details_page.py", title="Load a paper"),
    ],
    "Settings": settings_pages,
}

pg = st.navigation(pages)

setup_login()
is_admin = LoggedInUser().is_admin()
if is_admin:
    settings_pages.append(st.Page("pages/admin_page.py", title="Admin"))
    pg = st.navigation(pages)
# login should be after navigation

with st.sidebar:
    if is_admin:
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
        if st.button("Push data"):
            with st.spinner("Pushing data"):
                out, error = S3().push_local_events_data()
                st.write(error)
                st.write(out)
    st.link_button(
        "Give us Feedback",
        "https://docs.google.com/forms/d/e/1FAIpQLSffU-t3PBVLaqsW_5QF9JqnO8oFXGyHjLw0I6nfYvJ6QSztVA/viewform",
    )

    if st.button("Logout"):
        logout()
        

pg.run()
