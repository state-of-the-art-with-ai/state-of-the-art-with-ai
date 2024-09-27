from state_of_the_art.app.data import papers, topics
from state_of_the_art.app.pages.papers_page_utils import (
    edit_profile,
)
from state_of_the_art.app.pages.render_papers import render_papers
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.search.bm25_search import Bm25Search
from state_of_the_art.tables.interest_table import InterestsTable
import streamlit as st

generated_date = None
lookback_days = None
topic_description = None

st.title("Your Interests")
papers = None
send_by_email = False

topics = InterestsTable()
topics_df = topics.read()
topics_names = topics_df["name"].tolist()

c1, c2 = st.columns([1, 2])
with c1:
    for topic in topics_names:
        try:
            if st.button(topic, key=f't{topic}'):
                st.query_params["interest"] = topic
                selected_interest = topic
        except:
            pass
with c2:

    if 'interest' in st.query_params:
        selected_interest = st.query_params['interest'] 
    else:
        selected_interest = topics_names[-1]

    interest_name = topics_df[topics_df["name"] == selected_interest].iloc[0]["name"]
    topic_description = topics_df[topics_df["name"] == selected_interest].iloc[0][
        "description"
    ]

    topic_description = st.text_area("Query / Description", value=topic_description)
    interest_name = st.text_input("Interest name", value=interest_name)

    c1, c2 = st.columns([1,7])
    with c1:
        if st.button("Save"):
            topics.add(name=interest_name, description=topic_description)
            st.query_params["interest"] = interest_name
            st.success("Interest saved successfully")
            st.rerun()
    with c2:
        if st.button("Delete"):
            topics.delete_by(column="name", value=interest_name)
            del st.query_params["interest"]
            st.rerun()
            st.success("Interest deleted successfully")

st.divider()

if st.button("Fetch Papers"):
    with st.spinner("Loading papers"):
        papers = PapersLoader().get_all_papers()
        papers = Bm25Search(papers).search_returning_papers(interest_name + " " + topic_description)

    # render all papeers
    render_papers(papers, generated_date=generated_date)
