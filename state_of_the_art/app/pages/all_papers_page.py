from state_of_the_art.app.pages.render_papers import PapersRenderer
from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import (
    InterestPaperRecommender,
)
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
import datetime
from state_of_the_art.relevance_model.inference import Inference
from state_of_the_art.search.bm25_search import Bm25Search
from state_of_the_art.tables.mine_history import ArxivMiningHistory
import streamlit as st

generated_date = None
lookback_days = None
topic_description = None

st.title("All Papers")
MAX_PAPERS_TO_RENDER = 70

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
    date_filter = st.date_input("Filter By Day", value=default_date_filter)
    st.query_params["date"] = date_filter

    search_query = st.text_input("Enter your Search Query", value="")

@st.cache_data
def load_papers():
    return PapersLoader().load_papers_df()


def filter(papers_df):
    if not search_query:
        papers_df = papers_df[papers_df["published"].dt.date == date_filter]
        filters["Date"] = date_filter.isoformat()
    papers = PapersLoader().to_papers(papers_df)

    if search_query:
        papers = Bm25Search(papers).search_returning_papers(search_query)
    papers = papers[:MAX_PAPERS_TO_RENDER]
    
    inference = Inference()
    # sort papers by inference score
    papers = sorted(papers, key=lambda paper: inference.predict(paper.title), reverse=True)

    return papers

if search_query:
    filters["Query"] = search_query
    filters["Total Papers"] = len(papers_df.index)

st.divider()
with st.spinner("Rendering papers..."):
    papers_df = load_papers()
    papers = filter(papers_df)
    PapersRenderer().render_papers(papers, metadata=filters, generated_date=generated_date)
