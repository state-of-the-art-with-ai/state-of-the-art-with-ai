from state_of_the_art.paper.email_paper import EmailAPaper
from state_of_the_art.register_papers.register_paper import PaperRegister
import streamlit as st
from streamlit_tags import st_tags
from state_of_the_art.app.data import insights
from state_of_the_art.app.pages.paper_details_utils import new_paper, questions
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor
from state_of_the_art.tables.insights_table import InsightsTable
from state_of_the_art.tables.comments_table import Comments
from state_of_the_art.paper.local_paper_copy import open_paper_locally
from state_of_the_art.tables.paper_metadata_from_user_table import PaperMetadataFromUser
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.tables.tags_table import TagsTable
from state_of_the_art.relevance_model.inference import Inference

default_url = st.query_params.get("paper_url", "")
url = st.text_input(
    "Paper URL",
    value=default_url,
    key="paper_url",
    help="Type the URL of the paper to be loaded",
)
if url:
    url = url.strip()
    url = url.replace("https", "http")
    st.query_params.paper_url = url


c1, c2 = st.columns([1, 7])
with c1:
    load = st.button("Load Paper")
with c2:
    add = st.button("Add new Paper")
    if add:
        new_paper(url)

if not url:
    st.error("Load a paper to see details")
    st.stop()

insights_table = InsightsTable()
if not PaperRegister().is_paper_registered(url):
    with st.spinner("Registering paper..."):
        PaperRegister().register_by_url(url)
        st.rerun()

paper = PapersLoader().load_paper_from_url(url)

st.markdown(f"### {paper.title}")
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.markdown(f"[{url}](url)")
    st.markdown(
        f"###### Institution ({insights_table.get_lastest_answer('Institution', url)})"
    )
    st.markdown("Published: " + paper.published_date_str())
with c2:
    st.markdown(f"[Online PDF]({paper.pdf_url})")
    st.markdown(
        f"###### Conference ({insights_table.get_lastest_answer('Conference', url)})"
    )

with c3:
    if st.button("Open paper locally"):
        open_paper_locally(paper)

    if st.button("Send papert to email"):
        with st.spinner("Sending paper to email..."):
            if EmailAPaper().send(paper):
                st.success("Paper sent successfully")

with st.expander("Abstract"):
    st.markdown(paper.abstract)

c1, c2 = st.columns([1, 5])
with c1:
    extract_insights = st.button("Generate Insights")
with c2:
    if st.button("Edit questions"):
        questions(url)

if extract_insights:
    with st.spinner("Extracting insights..."):
        InsightExtractor().extract_insights_from_paper_url(
            url, email_skip=True, disable_pdf_open=True
        )
    st.rerun()

tags_table = TagsTable()
tags_table_df = tags_table.read()
existing_tags = []
existing_tags_df = tags_table_df[tags_table_df["paper_id"] == paper.abstract_url]
if not existing_tags_df.empty:
    existing_tags = existing_tags_df.iloc[0]["tags"].split(",")
selected_tags = st_tags(
    label="", value=existing_tags, suggestions=TagsTable.DEFAULT_TAGS
)
if selected_tags:
    tags_table.update_or_create(
        by_key="paper_id",
        by_value=paper.abstract_url,
        new_values={"tags": ",".join(selected_tags)},
    )
    st.success("Tags updated successfully")

query_progress = PaperMetadataFromUser().load_with_value(
    "abstract_url", paper.abstract_url
)
if not query_progress.empty:
    current_progress = int(query_progress.iloc[0]["progress"])
else:
    current_progress = 0

progress = st.select_slider(
    "Reading progress", options=tuple(range(0, 105, 5)), value=current_progress
)
if progress:
    PaperMetadataFromUser().update_or_create(
        by_key="abstract_url",
        by_value=paper.abstract_url,
        new_values={"progress": progress},
    )
    st.success("Progress updated successfully")


comments = Comments()
df_comments = comments.load_with_value(
    column="paper_url", value=paper.abstract_url, recent_first=True
)
comments_list = list(df_comments.iterrows())
with st.expander("Comments", expanded=True if comments_list else False):
    for index, comment in comments_list:
        st.markdown(
            f"{str(comment['tdw_timestamp']).split('.')[0]}  " + comment["message"]
        )

    c1, c2 = st.columns([2, 1])
    with c1:
        message = st.text_input("New comment")
    with c2:
        if st.button("Save new comment"):
            comments.add(message=message, paper_url=paper.abstract_url)
            st.success("Comment added successfully")
            st.rerun()

st.markdown("### Existing Insights")

insights = insights_table.read()
insights = insights[insights["paper_id"] == url]
insights = insights.sort_values(by="tdw_timestamp", ascending=False)

st.markdown(f""" ##### Structure
{insights_table.get_lastest_answer("DeepSummaryOfStructure", url)}
""")

st.markdown(f""" ##### Outcomes
{insights_table.get_lastest_answer("Outcomes", url)}
""")

with st.expander("Top insights", expanded=True):
    defintions = insights_table.get_all_answers("TopInsights", url)
    for definition in defintions:
        st.markdown(" - " + definition)

with st.expander("Definitions"):
    defintions = insights_table.get_all_answers("Definitions", url)
    for definition in defintions:
        st.markdown(" - " + definition)

with st.expander("Resources", expanded=True):
    defintions = insights_table.get_all_answers("Resources", url)
    for definition in defintions:
        st.markdown(" - " + definition)

st.markdown("### All Insights")
with st.spinner("Loading insights..."):
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
