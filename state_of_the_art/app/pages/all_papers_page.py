from state_of_the_art.app.pages.render_papers import render_papers
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
import datetime
from state_of_the_art.tables.mine_history import ArxivMiningHistory
import streamlit as st

generated_date = None
lookback_days = None
topic_description = None

st.title("All Arxiv Papers")

papers = None

from state_of_the_art.paper.papers_data_loader import PapersLoader

latest_date_with_papers = ArxivMiner().latest_date_with_papers()

c1, c2 = st.columns([1, 1])
with c1:
    st.metric(f"Latest date with papers in arxiv", str(latest_date_with_papers))
with c2:
    last_mine = ArxivMiningHistory().last().to_dict()
    st.metric(f"Latest date mined", str(last_mine['tdw_timestamp']).split(".")[0])

if "date" in st.query_params:
    default_date_filter = st.query_params["date"]
    default_date_filter = datetime.datetime.strptime(
        default_date_filter, "%Y-%m-%d"
    ).date()
else:
    default_date_filter = latest_date_with_papers
date_filter = st.date_input("By Day", value=default_date_filter)
st.query_params["date"] = date_filter

papers = PapersLoader().load_papers()
papers = papers[papers["published"].dt.date == date_filter]
papers = PapersLoader().to_papers(papers)

st.divider()
render_papers(papers, generated_date=generated_date)
