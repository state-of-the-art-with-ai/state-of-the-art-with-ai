import streamlit as st

pages = {
    "Papers": [
        st.Page("pages/papers_recommender.py", title="Get Paper Recommendations"),
        st.Page("pages/paper_dive.py", title="Dive into a Paper"),
    ],
    "Personalization": [
        st.Page("pages/profiles.py", title="Profile"),
        st.Page("pages/topics.py", title="Topics of Interest"),
        st.Page("pages/evaluations.py", title="Your Evalutions"),
    ]
}

pg = st.navigation(pages)
pg.run()
