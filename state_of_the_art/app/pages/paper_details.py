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


c1, c2, c3 = st.columns([1, 1, 3])
with c1:
    load = st.button("Load Paper")





if load or url:
    paper = PapersDataLoader().load_paper_from_url(url)

    st.markdown(f"### {paper.title}")
    st.markdown(f"[{url}](url)     [PDF]({paper.pdf_url})")
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

        c1, c2  = st.columns([1, 3])
        with c1:
            st.write("Predicted Score: ", insight['predicted_score'])
        with c2:
            feedback_received = st.feedback(options="faces", key=insight["tdw_uuid"])
        if feedback_received:
            InsightsTable().update_score(insight["tdw_uuid"], feedback_received)

    already_rendered = True

question = st.text_input("Your question")
st.write("The queston is: ", question)

c1, c2, = st.columns([1, 3])
with c1:
    send_to_email = st.checkbox("Send to email", value=False)
with c2:
    extract_insights = st.button("Extract Insights")

if extract_insights:
    InsightExtractor().extract_from_url(url, email_skip=not send_to_email, disable_pdf_open=True, question=question)

