import subprocess
from state_of_the_art.app.data import papers
from state_of_the_art.app.pages.render_papers import PapersRenderer
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationsRunsTable,
)
import json
import streamlit as st

generated_date = None
lookback_days = None
topic_description = None

st.title("Recommendations")
from state_of_the_art.paper.papers_data_loader import PapersLoader


PAPER_PER_TOPIC_TO_RENDER = 3


lookback_days = 1
generate_clicked = False
with st.expander("Generate new recommendations", expanded=False):
    lookback_days = st.number_input(
        "Lookback days", value=1, min_value=1, max_value=365
    )

    generate_clicked = st.button("Generate")

if generate_clicked:
    with st.status(f"Generating new recommendations for {lookback_days} days ... "):
        p = subprocess.Popen(
            f"sota InterestsRecommender generate -s -n {lookback_days} -r | tee /tmp/generator.log",
            shell=True,
            text=True,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
        for line in p.stdout:
            st.text(line)  # Continuously update the placeholder with the output

        for line in p.stderr:
            st.text(line)  # Continuously update the placeholder with the output

        p.stderr.close()
        p.stdout.close()

        p.wait()


@st.cache_data
def load_latest_recommendations():
    return RecommendationsRunsTable().last().to_dict()

with st.spinner("Loading latest recommendations ..."):
    recommendations = load_latest_recommendations()
    structured = json.loads(recommendations["recommended_papers"].replace("'", '"'))
    papers = []
    for interest, interest_data in structured["interest_papers"].items():
        for paper in PapersLoader().load_papers_from_urls(
            interest_data["papers"].keys()
        )[0:PAPER_PER_TOPIC_TO_RENDER]:
            papers.append(paper)

    recommendation_metadata = {
        "from_date": recommendations["from_date"],
        "to_date": recommendations["to_date"],
        "tdw_timestamp": str(recommendations["tdw_timestamp"]).split(".")[0],
        "papers_analysed_total": recommendations["papers_analysed_total"],
    }

    papers_metadata = {}
    for topic, metadata in structured["interest_papers"].items():
        for paper in metadata["papers"]:
            papers_metadata[paper] = (
                {"labels": [topic]}
                if paper not in papers_metadata
                else {"labels": papers_metadata[paper]["labels"] + [topic]}
            )

    PapersRenderer().render_papers(
        papers,
        papers_metadata=papers_metadata,
        generated_date=generated_date,
        metadata=recommendation_metadata,
    )
