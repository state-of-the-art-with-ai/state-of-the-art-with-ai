from state_of_the_art.app.pages.render_papers import render_papers
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
import datetime
from state_of_the_art.search.bm25_search import Bm25Search
from state_of_the_art.tables.mine_history import ArxivMiningHistory
import streamlit as st

generated_date = None
lookback_days = None
topic_description = None

st.title("All Papers")

papers_df = None

from state_of_the_art.paper.papers_data_loader import PapersLoader

latest_date_with_papers = ArxivMiner().latest_date_with_papers()

c1, c2 = st.columns([1, 1])
with c1:
    st.metric("Latest date with papers in arxiv", str(latest_date_with_papers))
with c2:
    last_mine = ArxivMiningHistory().last().to_dict()
    st.metric("Latest date mined", str(last_mine["tdw_timestamp"]).split(".")[0])

if "date" in st.query_params:
    default_date_filter = st.query_params["date"]
    default_date_filter = datetime.datetime.strptime(
        default_date_filter, "%Y-%m-%d"
    ).date()
else:
    default_date_filter = latest_date_with_papers
date_filter = st.date_input("By Day", value=default_date_filter)
st.query_params["date"] = date_filter

search_query = st.text_input("Enter your Query", value="")
filters = {}

with st.spinner("Fetching papers..."):
    papers_df = PapersLoader().load_papers_df()
    if not search_query:
        papers_df = papers_df[papers_df["published"].dt.date == date_filter]
        filters['Date'] = date_filter.isoformat()
    papers = PapersLoader().to_papers(papers_df)

    if search_query:
        papers = Bm25Search(papers).search_returning_papers(search_query)
        filters['Query']  = search_query

    st.divider()
    render_papers(papers, metadata=filters,generated_date=generated_date)
