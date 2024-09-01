from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.tables.recommendations_history_table import RecommendationsHistoryTable
import streamlit as st


@st.dialog("Edit profile")
def edit_profile(name):
    name = st.text_input("Name", name)
    email = st.text_input("Email")
    description = st.text_area("Description")
    st.button("Save")
    st.button("Delete")


def load_papers_from_insights(load_no):
    from tiny_data_warehouse import DataWarehouse

    tdw = DataWarehouse()
    df = tdw.event("sota_paper_insight").sort_values(
        by="tdw_timestamp", ascending=False
    )

    df = df[["abstract_url", "tdw_timestamp"]]
    df = df.drop_duplicates(subset=["abstract_url"])
    papers = df.to_dict(orient="records")[0:load_no]
    papers_urls = [paper["abstract_url"] for paper in papers]
    papers = PapersLoader().load_papers_from_urls(papers_urls)

    return papers


def load_papers_from_last_report(report_id=None, max_num_of_results = None):
    
    report_df = RecommendationsHistoryTable().read()
    if report_id:
        report_df = report_df[report_df["tdw_uuid"] == report_id].iloc[-1]
    else:
        report_df = report_df.iloc[-1]
    
    latest_summary = report_df.to_dict()


    latest_urls = PapersUrlsExtractor().extract_urls(latest_summary["summary"])
    papers = PapersLoader().load_papers_from_urls(latest_urls)
    if max_num_of_results:
        papers = papers[0:max_num_of_results]

    return papers, latest_summary["tdw_timestamp"]
