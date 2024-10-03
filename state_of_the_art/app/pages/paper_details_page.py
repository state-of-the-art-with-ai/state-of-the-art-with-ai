import streamlit as st
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.email_paper import EmailAPaper
from state_of_the_art.paper.url_sanitizer import UrlSanitizer
from state_of_the_art.register_papers.register_paper import PaperCreator
from state_of_the_art.app.data import insights
from state_of_the_art.app.utils.paper_details_utils import (
    create_custom_paper,
    load_arxiv_paper,
    questions,
    render_reading_progress,
    render_tags_for_paper,
)
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor
from state_of_the_art.tables.insights_table import InsightsTable
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.relevance_model.inference import Inference
from state_of_the_art.text_feedback.feedback_elements import render_feedback

with st.expander("Create or load a paper"):
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("Load an arxiv paper"):
            load_arxiv_paper()
    with c2:
        if st.button("Create external paper"):
            create_custom_paper()


url = st.query_params.get("paper_url", "")
url = UrlSanitizer().sanitize(url)

if not url:
    st.write("Load a paper to see details")
    st.stop()

if not PaperCreator().is_paper_registered(url):
    with st.spinner("Registering paper..."):
        if ArxivPaper.is_arxiv_url(url):
            PaperCreator().register_by_url(url)
            st.rerun()
        else:
            st.write(f"Paper '{url}' not registered and not created. Create this paper before.")
            st.stop()

paper = PapersLoader().load_paper_from_url(url)

insights_table = InsightsTable()
insights = insights_table.read()
insights = insights[insights["paper_id"] == paper.abstract_url]
insights = insights.sort_values(by="tdw_timestamp", ascending=False)
has_insights = not insights.empty

st.title(paper.title)
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    render_feedback(paper.title, type='paper_title', context={'paper_id': paper.abstract_url})
with c2:
    st.markdown(f"[{paper.abstract_url}]({paper.abstract_url})")
with c3:
    st.markdown(f"[Online PDF]({paper.pdf_url})")

c1, c2 = st.columns([1, 1])
with c1:
    render_tags_for_paper(paper)
with c2:
    render_reading_progress(paper)

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    extract_insights = st.button("Generate AI Insights")
with c2:
    edit_questions = st.button("Edit questions")
with c3:
    if st.button("Send paper to email"):
        with st.spinner("Sending..."):
            if EmailAPaper().send(paper):
                st.success("Paper sent successfully")

if edit_questions:
    questions(url)

if extract_insights:
    with st.spinner("Extracting insights..."):
        InsightExtractor().extract_insights_from_paper_url(
            url, email_skip=True, disable_pdf_open=True
        )
    st.rerun()

c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.markdown("Published: " + paper.published_date_str())
with c2:
    institution = insights_table.get_lastest_answer("Institution", url)
    if institution:
        st.markdown(f"###### Institution ({institution})")
with c3:
    conference = insights_table.get_lastest_answer("Conference", url)
    if conference:
        st.markdown(f"###### Conference ({conference})")

with st.expander("Abstract", expanded=not has_insights):
    st.markdown(paper.abstract)
    render_feedback(paper.abstract, type='paper_insight', context={'paper_id': paper.abstract_url})


with st.expander("Top insights", expanded=True):
    defintions = insights_table.get_all_answers("TopInsights", url)
    for definition in defintions:
        st.markdown(" - " + definition)
        render_feedback(definition, type="paper_insight", context={'paper_id': paper.abstract_url})


outcomes = insights_table.get_lastest_answer("Outcomes", url)
if outcomes:
    st.markdown(
        f""" ##### Outcomes
    {outcomes}
    """
    )
    render_feedback(outcomes, type="paper_insight", context={'paper_id': paper.abstract_url})

structure = insights_table.get_lastest_answer("DeepSummaryOfStructure", url)
if structure:
    st.markdown(
        f""" ##### Structure
    {structure}
    """
    )
    render_feedback(structure, type="paper_insight", context={'paper_id': paper.abstract_url})

with st.expander("Definitions"):
    defintions = insights_table.get_all_answers("Definitions", url)
    for definition in defintions:
        st.markdown(" - " + definition)
        render_feedback(definition, type="paper_insight", context={'paper_id': paper.abstract_url})

with st.expander("Resources", expanded=True):
    defintions = insights_table.get_all_answers("Resources", url)
    for definition in defintions:
        st.markdown(" - " + definition)
        render_feedback(definition, type="paper_insight", context={'paper_id': paper.abstract_url})

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
    insight_len = len(insight["insight"])
    appendix = ""
    if insight_len > 200:
        appendix = "..."

    st.markdown(
        f"**{insight["question"]}**: {insight["insight"][0:200]} {appendix}"
    )
    if len(insight["insight"]) > 200:
        st.expander("Read more").markdown(insight["insight"])
    render_feedback(insight['insight'], type="paper_insight", context={'paper_id': paper.abstract_url})

    


already_rendered = True
