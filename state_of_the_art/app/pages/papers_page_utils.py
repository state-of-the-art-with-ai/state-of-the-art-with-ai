from enum import Enum
from state_of_the_art.paper.papers_data_loader import PapersDataLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.recommender.generator import RecommenderTable
import streamlit as st


@st.dialog("Edit profile")
def edit_profile(name):
    name = st.text_input("Name", name)
    email = st.text_input("Email")
    description = st.text_area("Description")
    st.button("Save")
    st.button("Delete")


def load_papers_from_insights(load_no):
    from tiny_data_warehouse import DataWarehouse

    tdw = DataWarehouse()
    df = tdw.event("sota_paper_insight").sort_values(
        by="tdw_timestamp", ascending=False
    )

    df = df[["abstract_url", "tdw_timestamp"]]
    df = df.drop_duplicates(subset=["abstract_url"])
    papers = df.to_dict(orient="records")[0:load_no]
    papers_urls = [paper["abstract_url"] for paper in papers]
    papers = PapersDataLoader().load_papers_from_urls(papers_urls)

    return papers


def get_papers_from_summary(num_of_results):
    latest_summary = RecommenderTable().get_latest().to_dict()
    latest_urls = PapersUrlsExtractor().extract_urls(latest_summary["summary"])
    papers = PapersDataLoader().load_papers_from_urls(latest_urls)[0:num_of_results]

    return papers, latest_summary["tdw_timestamp"]


class RecommenationTypes(str, Enum):
    recommendation = "Recommendations"
    by_interest = "Interests"
    insights_history = "Insights history"
    by_tags = "By Tags"
