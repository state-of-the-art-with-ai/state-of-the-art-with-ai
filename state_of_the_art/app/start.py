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
    st.button("Insights History")


pg.run()
