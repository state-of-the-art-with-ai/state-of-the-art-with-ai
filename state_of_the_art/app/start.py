import streamlit as st

import subprocess
from state_of_the_art.config import config
title = 'State of the Art with AI' if config.is_production() else 'DEV State of the Art with AI'
st.set_page_config(page_title=title, layout="wide", initial_sidebar_state='expanded', menu_items=None)


from state_of_the_art.app.utils.login_utils import LoggedInUser, logout, setup_login


pages = {
    "": [
        st.Page("pages/all_papers_page.py", title="Latest Papers"),
        st.Page("pages/interests_page.py", title="Your Interests"),
        st.Page("pages/recommendations_page.py", title="Recommendations"),
        st.Page("pages/your_papers_page.py", title="Your Papers"),
        st.Page("pages/paper_details_page.py", title="Load a paper"),
        st.Page("pages/profile_page.py", title="Your Profile"),
    ],
}

pg = st.navigation(pages)

setup_login()
is_admin = LoggedInUser().is_admin()


@st.dialog("Help")
def help_modal():
    st.markdown("""
Welcome to State of the Art with AI!

You can use the sidebar to navigate to different pages.

To get recommendations, you need to have defined some interests. You can do this by clicking on the "Your Interests" page.

You can also load your own papers into the app.

If you need help, please contact us at support@stateofart.ai

If you have any feedback, please let us know!
    """)

    st.link_button(
        "Give us Feedback",
        "https://docs.google.com/forms/d/e/1FAIpQLSffU-t3PBVLaqsW_5QF9JqnO8oFXGyHjLw0I6nfYvJ6QSztVA/viewform",
    )
        
@st.cache_data
def get_last_release_date():
    p = subprocess.Popen(
        "uptime", shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    out, error = p.communicate()
    time_up = out.split(" up ")[1].split(",")[0]
    return time_up


with st.sidebar:
    username = LoggedInUser.get_instance().get_user_data().get("name", "")
    if username:
        st.text("Welcome " + username + "!")
    if is_admin or True:
        if st.button("Admin"):
            from state_of_the_art.app.utils.admin_utils import admin_panel
            admin_panel()

    if st.button("Logout"):
        logout()

    st.button("Get help", on_click=help_modal)
    st.link_button(
        "Give us Feedback",
        "https://docs.google.com/forms/d/e/1FAIpQLSffU-t3PBVLaqsW_5QF9JqnO8oFXGyHjLw0I6nfYvJ6QSztVA/viewform",
    )

    # get uptime of system and display it in a nice format
    st.info(f"Last release: {get_last_release_date()}")

pg.run()
