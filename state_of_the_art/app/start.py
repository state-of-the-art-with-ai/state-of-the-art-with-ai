import streamlit as st

pages = {
    "Papers": [
        st.Page("pages/papers_recommender.py", title="Get Paper Recommendations"),
        st.Page("pages/paper_details.py", title="Dive into a Paper"),
        st.Page("pages/history.py", title="Your Insights History"),
    ],
    "Personalization": [
        st.Page("pages/profiles.py", title="Profiles"),
        st.Page("pages/topics.py", title="Topics of Interest"),
    ]
}

pg = st.navigation(pages)
pg.run()
