from state_of_the_art.app.data import insights
import uuid;
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor
from state_of_the_art.insight_extractor.insiths_table import InsightsTable
from state_of_the_art.paper.papers_data import PapersDataLoader
import streamlit as st
from state_of_the_art.relevance_model.inference import Inference

url = st.text_input("Paper URL", value='', key='paper_url', help="Enter the URL of the paper") 
url = url.strip()
if st.button("Extract New Insights"):
    InsightExtractor().extract_from_url(url)

if st.button("Load"):
    paper = PapersDataLoader().load_paper_from_url(url)


    st.markdown(f"### Paper: {paper.title}")
    st.markdown(f"Url: {url}")
    st.markdown('Published: ' + paper.published_date_str())
    st.markdown("#### Insights")

    insights = InsightsTable().read().sort_values(by='tdw_timestamp', ascending=False)

    insights = insights[insights['paper_id'] == url]
    inference = Inference()
    for insight in insights.to_dict(orient="records"):
        st.markdown('- ' + insight['insight'])

        st.write('Predicted Score: ', inference.predict(insight['insight']))

        feedback_received = st.feedback(options="faces", key=insight['tdw_uuid'])
        if feedback_received:
            InsightsTable().update_score(insight['tdw_uuid'], feedback_received)
    

    st.markdown(f"Abstract: {paper.abstract}")