import streamlit as st

pages = {
    "Discover new Papers": [
        st.Page("pages/all_papers_page.py", title="All Papers"),
        st.Page("pages/interests_page.py", title="Your Interests"),
        st.Page("pages/papers_recommended_page.py", title="Papers Recommendations"),
    ],
    "Your Papers": [
        st.Page("pages/your_papers_page.py", title="Your Papers by Tags"),
        st.Page("pages/paper_details_page.py", title="Dive into a Paper"),
        st.Page("pages/papers_report_page.py", title="Past Recomendations"),
    ],
}


pg = st.navigation(pages)
st.set_page_config(layout="wide")


pg.run()
