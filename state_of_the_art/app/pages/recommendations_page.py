import datetime
import os
import time
from state_of_the_art.app.data import papers
from state_of_the_art.app.utils.login_utils import LoggedInUser
from state_of_the_art.app.utils.render_papers import PapersRenderer
from state_of_the_art.recommenders.interest_recommender.interest_recommender_generator import InterestPaperRecommender
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationsRunsTable,
)
import json
import streamlit as st

generated_date = None
topic_description = None

st.title("Recommendations")
from state_of_the_art.paper.papers_data_loader import PapersLoader

PAPER_PER_TOPIC_TO_RENDER = 3

def generate_new_recommendations(number_of_days_to_look_back):
    user_id = LoggedInUser().get_uuid()
    cmd = f"sota InterestsRecommender generate -n {number_of_days_to_look_back} -u {user_id} & "
    print(cmd)
    os.system(cmd)

c1, c2 = st.columns([2, 1])
with c1:

    ca, cb, cc = st.columns([1, 1, 1])
    time_to_sleep = 5
    with ca:
        if st.button("Generate 1 day recommendations"):
            generate_new_recommendations(1)
            st.success("Recommendations generation started ")
            time.sleep(time_to_sleep)
            st.rerun()

    with cb:
        if st.button("Generate 7 day recommendations"):
            generate_new_recommendations(7)
            st.success("Recommendations generation started ")
            time.sleep(time_to_sleep)
            st.rerun()
    with cc:
        if st.button("Generate 30 day recommendations"):
            generate_new_recommendations(30)
            st.success("Recommendations generation started ")
            time.sleep(time_to_sleep)
            st.rerun()

    with st.spinner("Loading latest recommendations ..."):

        base_recos_df = RecommendationsRunsTable().read(recent_first=True)
        id_to_load = st.query_params.get("run_id", None)

        if id_to_load:
            filtered_df = base_recos_df[base_recos_df["tdw_uuid"] == id_to_load].iloc[0].to_dict()
        else: 
            filtered_df = base_recos_df.iloc[0].to_dict()
    
        papers = []
        papers_metadata = {}
        if filtered_df["recommended_papers"]:
            structured = json.loads(filtered_df["recommended_papers"])
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
            "Id": filtered_df["tdw_uuid"][0:8],
            # first convert to date
            "Number of days": (datetime.datetime.fromisoformat(filtered_df["to_date"]) - datetime.datetime.fromisoformat(filtered_df["from_date"])).days,
            "Papers from": filtered_df["from_date"],
            "Papers to": filtered_df["to_date"],
            "Generation started": filtered_df["start_time"].split(".")[0],
            "papers_analysed_total": filtered_df["papers_analysed_total"],
        }

        PapersRenderer().render_papers(
            papers,
            papers_metadata=papers_metadata,
            generated_date=generated_date,
            metadata=recommendation_metadata,
            collapse_metadata=True,
        )

with c2:
    st.markdown("""##### Previous recommendations""")
    recommendations_table = RecommendationsRunsTable()
    runs = recommendations_table.read(recent_first=True)
    MAX_RUNS_TO_SHOW = 5
    runs = runs[0:MAX_RUNS_TO_SHOW]

    for run in runs.to_dict(orient='records'):
        current_time = datetime.datetime.now()
        days_covered = (datetime.datetime.fromisoformat(run["to_date"]) - datetime.datetime.fromisoformat(run["from_date"])).days
        time_since_start_in_minutes = (current_time - datetime.datetime.fromisoformat(run["start_time"])).total_seconds() / 60
        time_since_start_in_minutes = round(time_since_start_in_minutes, 2)


        c1, c2 = st.columns([3, 1])
        with c1:
            text = f'Run {run['tdw_uuid'][0:4]} {run['status']} {time_since_start_in_minutes} minutes ago, {days_covered} days covered {run['papers_analysed_total']} papers analysed'
            if run["status"] == "error":
                st.error(text)
            elif run["status"] == "success":
                st.success(text)
            elif run["status"] == "started":
                st.warning(text)
            else:
                raise ValueError(f"Unknown status: {run['status']}")
        with c2:
            st.link_button("View", "/recommendations_page?run_id=" + run["tdw_uuid"])

        
