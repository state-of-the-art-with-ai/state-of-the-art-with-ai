from enum import Enum
import streamlit as st
from state_of_the_art.app.data import papers
from state_of_the_art.app.pages.papers_page_utils import (
    get_papers_from_summary,
    load_papers_from_insights,
)
from state_of_the_art.app.pages.render_papers import render_papers
from state_of_the_art.paper.papers_data_loader import PapersDataLoader
from state_of_the_art.paper.tags_table import TagsTable

num_of_results = 15
lookback_days = None
topic_description = None
num_of_results = 15
papers = None
send_by_email = False

st.title("Your papers")


class RecommenationTypes(str, Enum):
    by_tags = "My Tags"
    insights_history = "Insights history"


search_types = [item.value for item in RecommenationTypes]
default_search_index = 0
if "search_type" in st.query_params:
    default_ui = st.query_params["search_type"]
    default_search_index = search_types.index(default_ui)


selected_ui = st.selectbox("Search Types", search_types, index=default_search_index)
st.query_params["search_type"] = selected_ui
with st.expander("Search options", expanded=True):
    if selected_ui == RecommenationTypes.insights_history:
        load_no = st.selectbox("Number of papers to load", [50, 100, 200])
        papers = load_papers_from_insights(load_no=load_no)

    if selected_ui == RecommenationTypes.by_tags:
        all_tags_df = TagsTable().read()
        all_tags = all_tags_df["tags"].to_list()
        all_tags = [tags.split(",") for tags in all_tags]
        import itertools

        merged = list(itertools.chain(*all_tags))
        unique = list(set(merged))

        default_tags = []
        if "tags" in st.query_params:
            default_tags = st.query_params["tags"]

        elif st.checkbox("Select all", key="all_tags", value=True):
            default_tags = unique

        selected_tags = st.multiselect("Tags", unique, default_tags)
        num_of_results = st.selectbox("Num of results", [15, 50, 100])
        if selected_tags:
            st.query_params["tags"] = selected_tags

        all_papers_selected = all_tags_df[
            all_tags_df["tags"].str.contains("|".join(selected_tags))
        ]
        all_papers_selected = all_papers_selected["paper_id"].to_list()

        unique_papers = list(set(all_papers_selected))

        papers = PapersDataLoader().load_papers_from_urls(unique_papers)[
            0:num_of_results
        ]

    generated_date = None
    if not papers:
        papers, generated_date = get_papers_from_summary(num_of_results=num_of_results)


st.divider()

render_papers(papers, generated_date=generated_date)
