

from state_of_the_art.app.data import papers
from state_of_the_art.app.pages.render_papers import render_papers
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
import datetime
from state_of_the_art.tables.recommendations_history_table import RecommendationsHistoryTable
import streamlit as st

generated_date = None
lookback_days = None
topic_description = None

st.title("Papers recommended")

papers = None

from state_of_the_art.paper.papers_data_loader import PapersLoader

history = RecommendationsHistoryTable().read().sort_values(by='tdw_timestamp', ascending=False)
recommendation = history.iloc[0]
papers_urls = PapersUrlsExtractor().extract_urls(recommendation["recommended_papers"])
papers = PapersLoader().load_papers_from_urls(papers_urls)

st.divider()
render_papers(papers, generated_date=generated_date)