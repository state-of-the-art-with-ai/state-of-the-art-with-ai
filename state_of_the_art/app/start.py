import streamlit as st

pages = {
    "Papers": [
        st.Page("pages/papers_page.py", title="Papers"),
        st.Page("pages/paper_details_page.py", title="Dive into a Paper"),
    ],
}

pg = st.navigation(pages)
pg.run()
