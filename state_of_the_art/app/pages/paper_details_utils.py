import streamlit as st
from state_of_the_art.insight_extractor.insight_extractor import (
    InsightExtractor,
    SupportedModels,
)
from state_of_the_art.paper.questions_table import QuestionsTable


@st.dialog("Questions")
def questions(paper_url):
    tab1, tab2 = st.tabs(["Custom question", "Default questions"])

    with tab1:
        custom_question = st.text_input("Type the question here")

    with tab2:
        question_table = QuestionsTable()
        df = question_table.read()
        df_updated = st.data_editor(df, width=800, num_rows="dynamic")
        if st.button("Save"):
            question_table.replace(df_updated, dry_run=False)
            st.success("Successfully saved")

    supported_models = [model.value for model in SupportedModels]
    selected_model = st.selectbox(
        "Select a model",
        supported_models,
        index=supported_models.index(SupportedModels.gpt_4o.value),
    )
    extract_insights = st.button("Generate Insights", key="generate_insights_dialog")
    if extract_insights:
        InsightExtractor().extract_insights_from_paper_url(
            paper_url,
            email_skip=True,
            disable_pdf_open=True,
            question=custom_question,
            selected_model=selected_model,
        )
        st.rerun()
