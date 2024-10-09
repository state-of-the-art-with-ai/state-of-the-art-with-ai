from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.tables.tags_table import TagsTable
import streamlit as st


@st.cache_data(ttl=60*60)
def load_all_papers_df():
    return PapersLoader().load_papers_df()
