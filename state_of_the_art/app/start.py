import streamlit as st
st.set_page_config(page_title='State of the Art with AI', layout="wide", initial_sidebar_state='expanded', menu_items=None)

import subprocess
from state_of_the_art.app.utils.admin_utils import admin_panel
from state_of_the_art.app.utils.paper_details_utils import create_custom_paper

from state_of_the_art.app.utils.login_utils import LoggedInUser, logout, setup_login
from state_of_the_art.infrastructure.s3 import S3
from state_of_the_art.tables.data_sync_table import PushHistory


pages = {
    "Papers": [
        st.Page("pages/all_papers_page.py", title="Browse Latest"),
        st.Page("pages/interests_page.py", title="Your Interests"),
        st.Page("pages/papers_recommended_page.py", title="Recommendations"),
        st.Page("pages/your_papers_page.py", title="Your Papers"),
        st.Page("pages/paper_details_page.py", title="Load a paper"),
    ],
    "Settings": [
        st.Page("pages/profile_page.py", title="Profile Page"),
],
}

pg = st.navigation(pages)

setup_login()
is_admin = LoggedInUser().is_admin()
with st.sidebar:
    if is_admin or True:
        if st.button("Admin"):
            admin_panel()

    if st.button("Logout"):
        logout()
    st.link_button(
        "Give us Feedback",
        "https://docs.google.com/forms/d/e/1FAIpQLSffU-t3PBVLaqsW_5QF9JqnO8oFXGyHjLw0I6nfYvJ6QSztVA/viewform",
    )
        

pg.run()
