from enum import Enum
import streamlit as st
from state_of_the_art.app.data import papers
from state_of_the_art.app.pages.papers_page_utils import (
    load_papers_from_last_report,
    load_papers_from_insights,
)
from state_of_the_art.app.pages.render_papers import render_papers
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.tables.tags_table import TagsTable

num_of_results = 15
lookback_days = None
topic_description = None
num_of_results = 15
papers = None
send_by_email = False

st.title("Your papers")

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

all_papers_selected = all_tags_df[
    all_tags_df["tags"].str.contains("|".join(selected_tags))
]
all_papers_selected = all_papers_selected["paper_id"].to_list()

unique_papers = list(set(all_papers_selected))

papers = PapersLoader().load_papers_from_urls(unique_papers)

st.divider()

render_papers(papers)
