from state_of_the_art.app.data import insights
from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor
from state_of_the_art.insight_extractor.insights_table import InsightsTable
from state_of_the_art.paper.comments import Comments
from state_of_the_art.paper.local_paper_copy import open_paper_locally
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.questions_table import QuestionsTable
from state_of_the_art.paper.tags_table import TagsTable
import streamlit as st
from streamlit_tags import st_tags
from state_of_the_art.relevance_model.inference import Inference
import pandas as pd


default_url = st.query_params.get("paper_url", "")
url = st.text_input(
    "Paper URL", value=default_url, key="paper_url", help="Type the URL of the paper to be loaded"
)
if url:
    url = url.strip()
    st.query_params.paper_url = url


load = st.button("Load Paper")

if load or url:

    paper = PapersDataLoader().load_paper_from_url(url)

    st.markdown(f"### {paper.title}")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown(f"[{url}](url)")
    with c2:
        st.markdown(f"[PDF]({paper.pdf_url})")

    with c3:
        if st.button("Open paper locally"):
            open_paper_locally(paper.abstract_url)



    tags_table = TagsTable()
    tags_table_df = tags_table.read()
    existing_tags = []
    existing_tags_df = tags_table_df[tags_table_df['paper_id'] == paper.abstract_url]
    if not existing_tags_df.empty:
        existing_tags = existing_tags_df.iloc[0]['tags'].split(',')
    selected_tags = st_tags(label='', value=existing_tags, suggestions=TagsTable.DEFAULT_TAGS)
    if selected_tags:
        tags_table.update_or_create(by_key='paper_id', by_value=paper.abstract_url, new_values={'tags': ','.join(selected_tags)})


    st.markdown("Published: " + paper.published_date_str())
    st.markdown(f"Abstract: {paper.abstract[0:280]} ...")
    if len(paper.abstract) > 280:  
        with st.expander("Full abstract"):
            st.markdown(paper.abstract)



    st.markdown("**Comments**: ")
    with st.expander("Add Comments"):
        comments = Comments()
        df_comments = comments.load_with_value(column='paper_url', value=paper.abstract_url, recent_first=True)

        c1, c2 = st.columns([2, 1])
        with c1:
            message = st.text_input('New comment')
        with c2:
            if st.button("Add"):
                comments.add(message=message, paper_url=paper.abstract_url)

    for index, comment in df_comments.iterrows():
        st.markdown(f"{str(comment['tdw_timestamp']).split('.')[0]}  " + comment['message'])

    st.divider()


    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("#### Generated Insights")
    with c2:
        extract_insights = st.button("Generate Insights")

    with st.expander("Questions"):
        tab1, tab2 = st.tabs(["Custom question", "Default questions"])


        with tab1:
            custom_question = st.text_input("Type the quesiton here")

        with tab2:
            question_table = QuestionsTable()
            df = question_table.read()
            df_updated = st.data_editor(df, width=800, num_rows='dynamic')
            if st.button("Save"):
                question_table.replace(df_updated, dry_run=False)



    if extract_insights:
        InsightExtractor().extract_insights_from_paper_url(
            url, email_skip=True, disable_pdf_open=True, question=custom_question
        )
        st.rerun()


    insights = InsightsTable().read()
    insights = insights[insights["paper_id"] == url]
    insights = insights.sort_values(by="tdw_timestamp", ascending=False)

    inference = Inference()
    insights_list = insights.to_dict(orient="records")
    for insight in insights_list:
        insight["predicted_score"] = inference.predict(insight["tdw_uuid"])

    for insight in insights_list:
        c1, c2 = st.columns([3, 1])
        with c1:
            insight_len = len(insight["insight"])
            appendix = ""
            if insight_len > 200:
                appendix = "..."

            st.markdown(f"**{insight["question"]}**: {insight["insight"][0:200]} {appendix}")
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
