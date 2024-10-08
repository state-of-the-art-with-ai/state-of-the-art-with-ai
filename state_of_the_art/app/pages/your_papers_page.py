import streamlit as st
import itertools

from state_of_the_art.app.data import papers
from state_of_the_art.app.utils.render_papers import PapersRenderer
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.tables.tags_table import TagsTable

num_of_results = 15
lookback_days = None
topic_description = None
num_of_results = 15
papers = None
send_by_email = False

st.title("Your papers")

def load_tags_df():
    return TagsTable().read()

with st.spinner("Loading page"):
    all_tags_df = load_tags_df()
    all_tags = all_tags_df["tags"].to_list()
    all_tags = [tags.split(",") for tags in all_tags]

    merged = list(itertools.chain(*all_tags))
    unique = list(set(merged))

    selected_tags = st.selectbox("Filter By tags", options=['Select' ] + unique, index=0)

    if selected_tags == 'Select':
        selected_tags = unique
    else:
        selected_tags = [selected_tags]

all_papers_selected = all_tags_df[
    all_tags_df["tags"].str.contains("|".join(selected_tags))
]
all_papers_selected = all_papers_selected["paper_id"].to_list()

unique_papers = list(set(all_papers_selected))

papers = PapersLoader().load_papers_from_urls(unique_papers)
# sort papers by the bookmarked date
papers = sorted(
    papers,
    key=lambda x: all_tags_df[all_tags_df["paper_id"] == x.abstract_url][
        "tdw_timestamp"
    ].values[0],
    reverse=True,
)

with st.spinner("Rendering papers ..."):
    PapersRenderer(disable_save_button=True, enable_tags=True, enable_pagination=True).render_papers(papers)
