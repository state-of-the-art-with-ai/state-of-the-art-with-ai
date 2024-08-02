from state_of_the_art.app.data import insights
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor
from state_of_the_art.insight_extractor.insights_table import InsightsTable
from state_of_the_art.paper.papers_data import PapersDataLoader
import streamlit as st
from state_of_the_art.relevance_model.inference import Inference


default_url = st.query_params.get("paper_url", "")
url = st.text_input(
    "Paper URL", value=default_url, key="paper_url", help="Enter the URL of the paper"
)
if url:
    url = url.strip()
    st.query_params.paper_url = url

load = st.button("Load Paper")


if st.button("Extract New Insights"):
    InsightExtractor().extract_from_url(url)

if load or url:
    paper = PapersDataLoader().load_paper_from_url(url)

    st.markdown(f"### Paper: {paper.title}")
    st.markdown(f"Url: {url}")
    st.markdown("Published: " + paper.published_date_str())
    st.markdown(f"Abstract: {paper.abstract}")
    st.markdown("#### Insights")

    insights = InsightsTable().read()
    insights = insights[insights["paper_id"] == url]
    insights = insights.sort_values(by="tdw_timestamp", ascending=False)

    inference = Inference()
    insights_list = insights.to_dict(orient="records")
    for insight in insights_list:
        insight["predicted_score"] = inference.predict(insight["tdw_uuid"])
    
    insights_list =sorted(insights_list, key=lambda x: x['predicted_score'], reverse=True)

    for insight in insights_list:
        st.markdown(f"- ({insight['question']}) " + insight["insight"])
        st.write("Predicted Score: ", insight['predicted_score'])

        feedback_received = st.feedback(options="faces", key=insight["tdw_uuid"])
        if feedback_received:
            InsightsTable().update_score(insight["tdw_uuid"], feedback_received)

    already_rendered = True
