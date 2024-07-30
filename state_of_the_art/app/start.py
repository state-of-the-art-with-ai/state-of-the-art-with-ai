import streamlit as st

pages = {
    "Pages": [
    st.Page("pages/papers_recommender.py", title="Get recommendations of papers"),
    st.Page("pages/paper_dive.py", title="Dive into a paper"),
    st.Page("pages/evaluations.py", title="Your Evalutions"),
    ],
    "Personalization": [
        st.Page("pages/profiles.py", title="Personalize your profile"),
        st.Page("pages/topics.py", title="Your Topics of Interest"),
    ]
}

pg = st.navigation(pages)
pg.run()
