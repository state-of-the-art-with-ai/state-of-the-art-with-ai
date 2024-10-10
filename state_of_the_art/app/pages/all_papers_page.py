from typing import List
from state_of_the_art.app.utils.cached_data import load_all_papers_df
from state_of_the_art.app.utils.render_papers import PapersRenderer
from state_of_the_art.paper.paper_entity import Paper
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
import datetime
from state_of_the_art.relevance_model.text_evaluation_inference import TextEvaluationInference
from state_of_the_art.search.bm25_search import Bm25Search
import streamlit as st

generated_date = None
lookback_days = None
topic_description = None

st.title("Latest Papers")

papers_df = None
filters = {}

from state_of_the_art.paper.papers_data_loader import PapersLoader


@st.cache_data
def fetch_latest_date_with_papers():
    return ArxivMiner().latest_date_with_papers()


with st.spinner("Fetching metadata about papers..."):
    latest_date_with_papers = fetch_latest_date_with_papers()

if "date" in st.query_params:
    default_date_filter = st.query_params["date"]
    default_date_filter = datetime.datetime.strptime(
        default_date_filter, "%Y-%m-%d"
    ).date()
else:
    default_date_filter = latest_date_with_papers



with st.expander("Date Filter"):
    c1, c2 = st.columns([1,1])

    with c1:
        if st.button("Previous Day"):
            default_date_filter = default_date_filter - datetime.timedelta(days=1)
            st.query_params["date"] = default_date_filter
    with c2:    
        if st.button("Next Day"):
            default_date_filter = default_date_filter + datetime.timedelta(days=1)
            st.query_params["date"] = default_date_filter

    date_filter = st.date_input("Filter By Day", value=default_date_filter)


st.query_params["date"] = date_filter


metadata = {}
def fetch_and_filter():
    papers_df = load_all_papers_df()
    papers_df = papers_df[papers_df["published"].dt.date == date_filter]
    metadata["Papers found for date"] = len(papers_df.index)
    paper_list = PapersLoader().to_papers(papers_df)
    if paper_list:
        inference = TextEvaluationInference()
        papers_scored = inference.predict_batch([paper.title for paper in paper_list])
        # sort papers by inference score
        paper_list = [paper for _, paper in sorted(zip(papers_scored, paper_list), key=lambda pair: pair[0], reverse=True)]
    return paper_list

renderer = PapersRenderer(enable_pagination=True)
renderer.render_papers(fetch_and_filter(), metadata=metadata, generated_date=generated_date)
