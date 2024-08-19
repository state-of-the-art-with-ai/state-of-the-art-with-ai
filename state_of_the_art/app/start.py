import streamlit as st

pages = {
    "Pages": [
        st.Page("pages/papers_page.py", title="Discover Papers"),
        st.Page("pages/paper_details_page.py", title="Dive into a Paper"),
        st.Page("pages/reports_page.py", title="Past Recomendations"),
    ],
}

pg = st.navigation(pages)

with st.sidebar:
    st.link_button("Find Papers By Interest", "/?search_type=Interests")
    st.link_button("Find Papers By Tags", "/?search_type=By Tags")


pg.run()
