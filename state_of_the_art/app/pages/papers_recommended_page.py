import datetime
import subprocess
from state_of_the_art.app.data import papers
from state_of_the_art.app.utils.render_papers import PapersRenderer
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

c1, c2 = st.columns([2, 1])
with c1:
    lookback_days = 1
    generate_clicked = False
    ca, cb = st.columns([1, 1])
    with ca:
        generate_clicked = st.button("Generate")
    with cb:
        lookback_days = st.number_input(
            "Lookback days", value=1, min_value=1, max_value=365
        )

    if generate_clicked:
        with st.status(f"Generating new recommendations for {lookback_days} days ... "):
            p = subprocess.Popen(
                f"sota InterestsRecommender generate -s -n {lookback_days} | tee /tmp/generator.log",
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

    with st.spinner("Loading latest recommendations ..."):

        recommendations_df = RecommendationsRunsTable().read(recent_first=True)
        recommendation_to_load = st.query_params.get("run_id", None)

        if recommendation_to_load:
            recommendations_df = recommendations_df[recommendations_df["tdw_uuid"] == recommendation_to_load].to_dict()
        else: 
            recommendations_df = recommendations_df.iloc[0].to_dict()
    
        papers = []
        papers_metadata = {}
        if recommendations_df["recommended_papers"]:
            structured = json.loads(recommendations_df["recommended_papers"].replace("'", '"'))
            for interest, interest_data in structured["interest_papers"].items():
                for paper in PapersLoader().load_papers_from_urls(
                    interest_data["papers"].keys()
                )[0:PAPER_PER_TOPIC_TO_RENDER]:
                    papers.append(paper)

            for topic, metadata in structured["interest_papers"].items():
                for paper in metadata["papers"]:
                    papers_metadata[paper] = (
                        {"labels": [topic]}
                        if paper not in papers_metadata
                        else {"labels": papers_metadata[paper]["labels"] + [topic]}
                    )


        recommendation_metadata = {
            "Papers from": recommendations_df["from_date"],
            "Papers to": recommendations_df["to_date"],
            "Generation started": recommendations_df["start_time"].split(".")[0],
            "papers_analysed_total": recommendations_df["papers_analysed_total"],
        }

        PapersRenderer().render_papers(
            papers,
            papers_metadata=papers_metadata,
            generated_date=generated_date,
            metadata=recommendation_metadata,
        )

with c2:
    st.markdown("""##### Previous ones""")
    recommendations_table = RecommendationsRunsTable()
    runs = recommendations_table.read(recent_first=True)
    MAX_RUNS_TO_SHOW = 5
    runs = runs[0:MAX_RUNS_TO_SHOW]

    for run in runs.to_dict(orient='records'):
        current_time = datetime.datetime.now()
        time_since_start = str(current_time - datetime.datetime.fromisoformat(run["start_time"])).split(".")[0]

        st.markdown(f"""
###### Started at {time_since_start} Status: {run['status']} Papers analysed: {run['papers_analysed_total']}
""")
        st.link_button("View", "/papers_recommended_page?run_id=" + run["tdw_uuid"])

        
