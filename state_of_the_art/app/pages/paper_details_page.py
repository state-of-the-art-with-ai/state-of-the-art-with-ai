from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.email_paper import EmailAPaper
from state_of_the_art.register_papers.register_paper import PaperCreator
import streamlit as st
from state_of_the_art.app.data import insights
from state_of_the_art.app.pages.paper_details_utils import (
    load_different_paper,
    questions,
    render_reading_progress,
    render_tags,
)
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor
from state_of_the_art.tables.insights_table import InsightsTable
from state_of_the_art.tables.comments_table import Comments
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.tables.tags_table import TagsTable
from state_of_the_art.relevance_model.inference import Inference

if st.button("Load a paper"):
    load_different_paper()


url = st.query_params.get("paper_url", "")
if not url:
    st.write("Load a paper to see details")
    st.stop()

if not PaperCreator().is_paper_registered(url):
    with st.spinner("Registering paper..."):
        if ArxivPaper.is_arxiv_url(url):
            PaperCreator().register_by_url(url)
            st.rerun()
        else:
            st.write("Not registered and not created. Create this paper before.")
            st.stop()

paper = PapersLoader().load_paper_from_url(url)

insights_table = InsightsTable()
insights = insights_table.read()
insights = insights[insights["paper_id"] == paper.abstract_url]
insights = insights.sort_values(by="tdw_timestamp", ascending=False)
has_insights = not insights.empty

st.markdown(f"### {paper.title}")
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.markdown(f"[{paper.abstract_url}]({paper.abstract_url})")
    extract_insights = st.button("Generate AI Insights")

with c2:
    st.markdown(f"[Online PDF]({paper.pdf_url})")
    edit_questions = st.button("Edit questions")
with c3:
    st.markdown("Published: " + paper.published_date_str())
    if st.button("Send paper to email"):
        with st.spinner("Sending..."):
            if EmailAPaper().send(paper):
                st.success("Paper sent successfully")

c1, c2 = st.columns([1, 1])
with c1:
    render_tags(paper)
with c2:
    render_reading_progress(paper)

if edit_questions:
    questions(url)

if extract_insights:
    with st.spinner("Extracting insights..."):
        InsightExtractor().extract_insights_from_paper_url(
            url, email_skip=True, disable_pdf_open=True
        )
    st.rerun()

c1, c2 = st.columns([1, 1])
with c1:
    institution = insights_table.get_lastest_answer("Institution", url)
    if institution:
        st.markdown(f"###### Institution ({institution})")
with c2:
    conference = insights_table.get_lastest_answer("Conference", url)
    if conference:
        st.markdown(f"###### Conference ({conference})")

with st.expander("Abstract", expanded=not has_insights):
    st.markdown(paper.abstract)


with st.expander("Top insights", expanded=True):
    defintions = insights_table.get_all_answers("TopInsights", url)
    for definition in defintions:
        st.markdown(" - " + definition)


st.markdown(
    f""" ##### Outcomes
{insights_table.get_lastest_answer("Outcomes", url)}
"""
)

st.markdown(
    f""" ##### Structure
{insights_table.get_lastest_answer("DeepSummaryOfStructure", url)}
"""
)

with st.expander("Definitions"):
    defintions = insights_table.get_all_answers("Definitions", url)
    for definition in defintions:
        st.markdown(" - " + definition)

with st.expander("Resources", expanded=True):
    defintions = insights_table.get_all_answers("Resources", url)
    for definition in defintions:
        st.markdown(" - " + definition)

st.markdown("### More insights by relevance")

with st.spinner("Loading more insights..."):
    inference = Inference()
    insights_list = insights.to_dict(orient="records")
    for insight in insights_list:
        insight["predicted_score"] = inference.predict(insight["tdw_uuid"])

insights_list = sorted(
    insights_list, key=lambda el: el["predicted_score"], reverse=True
)
IGNORED_INSIGHTS = [
    "DeepSummaryOfStructure",
    "Institution",
    "Conference",
    "Definitions",
    "Resources",
    "Outcomes",
]

insights_list = filter(lambda x: x["question"] not in IGNORED_INSIGHTS, insights_list)


for insight in insights_list:
    c1, c2 = st.columns([3, 1])
    with c1:
        insight_len = len(insight["insight"])
        appendix = ""
        if insight_len > 200:
            appendix = "..."

        st.markdown(
            f"**{insight["question"]}**: {insight["insight"][0:200]} {appendix}"
        )
        if len(insight["insight"]) > 200:
            st.expander("Read more").markdown(insight["insight"])
    with c2:
        c1, c2 = st.columns(2)
        with c1:
            feedback_received = st.feedback(options="faces", key=insight["tdw_uuid"])
            if feedback_received:
                InsightsTable().update_score(insight["tdw_uuid"], feedback_received)
        with c2:
            st.write("PS: ", insight["predicted_score"])

already_rendered = True
