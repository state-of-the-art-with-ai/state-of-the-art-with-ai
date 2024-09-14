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

st.title("Discover Papers by Interest")
papers = None
send_by_email = False

topics = InterestsTable()
topics_df = topics.read()
topics_names = topics_df["name"].tolist()

default_interest = (
    0
    if "interest" not in st.query_params
    else topics_names.index(st.query_params["interest"])
)

selected_interest = st.selectbox(
    "Existing Interest", topics_names, index=default_interest
)

st.query_params["interest"] = selected_interest
interest_name = topics_df[topics_df["name"] == selected_interest].iloc[0]["name"]
topic_description = topics_df[topics_df["name"] == selected_interest].iloc[0][
    "description"
]

topic_description = st.text_area("Query / Description", value=topic_description)
interest_name = st.text_input("Interest name", value=interest_name)

c1, c2 = st.columns(2)
with c1:
    if st.button("Save Interest"):
        topics.add(name=interest_name, description=topic_description)
        st.query_params["interest"] = interest_name
        st.success("Interest saved successfully")
        st.rerun()
with c2:
    if st.button("Delete Interest"):
        topics.delete_by(column="name", value=interest_name)
        del st.query_params["interest"]
        st.rerun()
        st.success("Interest deleted successfully")

c1, c2 = st.columns([3, 1])
with c1:
    current_profile = st.selectbox("Profile", ["jean", "gdp", "mlp", "mlops"])
with c2:
    if st.button("Manage Profile"):
        edit_profile(current_profile)

st.divider()

with st.spinner("Loading papers"):
    papers = PapersLoader().get_all_papers()
    papers = Bm25Search(papers).search(interest_name + " " + topic_description)

# render all papeers
render_papers(papers, generated_date=generated_date)
