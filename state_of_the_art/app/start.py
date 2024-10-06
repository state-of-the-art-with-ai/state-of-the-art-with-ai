import streamlit as st

from state_of_the_art.config import config
title = 'State of the Art with AI' if config.is_production() else 'DEV State of the Art with AI'
st.set_page_config(page_title=title, layout="wide", initial_sidebar_state='expanded', menu_items=None)


from state_of_the_art.app.utils.login_utils import LoggedInUser, logout, setup_login


pages = {
    "": [
        st.Page("pages/all_papers_page.py", title="All Papers"),
        st.Page("pages/interests_page.py", title="Your Interests"),
        st.Page("pages/papers_recommended_page.py", title="Recommendations For You"),
        st.Page("pages/your_papers_page.py", title="Your Papers"),
        st.Page("pages/paper_details_page.py", title="Load a paper"),
        st.Page("pages/profile_page.py", title="Your Profile"),
    ],
}

pg = st.navigation(pages)

setup_login()
is_admin = LoggedInUser().is_admin()

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
    st.link_button(
        "Give us Feedback",
        "https://docs.google.com/forms/d/e/1FAIpQLSffU-t3PBVLaqsW_5QF9JqnO8oFXGyHjLw0I6nfYvJ6QSztVA/viewform",
    )
        

pg.run()
