

import json
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
recommendations = history.iloc[0].to_dict()
structured = json.loads(recommendations['recommended_papers'].replace("'", "\""))

papers_urls = PapersUrlsExtractor().extract_urls(recommendations["recommended_papers"])
papers = PapersLoader().load_papers_from_urls(papers_urls)

papers_metadata = {}
for topic, metadata in structured.items():
    for paper in metadata['papers']:
        papers_metadata[paper] = {"labels": [topic]}



papers_urls = PapersUrlsExtractor().extract_urls(recommendations["recommended_papers"])
st.divider()
render_papers(papers, papers_metadata=papers_metadata, generated_date=generated_date)