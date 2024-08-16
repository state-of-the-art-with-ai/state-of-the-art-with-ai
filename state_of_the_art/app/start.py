import streamlit as st

pages = {
    "Pages": [
        st.Page("pages/papers_page.py", title="Papers"),
        st.Page("pages/paper_details_page.py", title="Dive into a Paper"),
    ],
}

pg = st.navigation(pages)

with st.sidebar:
    st.button("Open by tags")
    st.button("Insights History")


pg.run()
