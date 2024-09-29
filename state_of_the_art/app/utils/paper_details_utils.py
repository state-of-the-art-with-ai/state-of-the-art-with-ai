from streamlit_tags import st_tags
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.tables.arxiv_paper_table import PaperTable
from state_of_the_art.tables.paper_metadata_from_user_table import PaperMetadataFromUser
from state_of_the_art.tables.tags_table import TagsTable
import streamlit as st
from state_of_the_art.insight_extractor.insight_extractor import (
    InsightExtractor,
    SupportedModels,
)
from state_of_the_art.tables.questions_table import QuestionsTable


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


@st.dialog("Questions")
def create_new(paper_url):
    st.write("New paper")
    title = st.text_input("Title")
    paper_url = st.text_input("Url", paper_url)
    if st.button("Save"):
        st.success("Paper saved successfully")
        paper_table = PaperTable()
        paper_table.add(
            abstract_url=paper_url, title=title, published=None, institution=""
        )
        tags_table = TagsTable()
        tags_table.add_tag_to_paper(paper_url, "Manually Created")
        st.query_params["paper_url"] = paper_url
        st.rerun()


def render_tags_for_paper(paper: ArxivPaper):

    tags_table = TagsTable()
    tags_table_df = tags_table.read()

    existing_tags = []
    existing_tags_df = tags_table_df[tags_table_df["paper_id"] == paper.abstract_url]
    if not existing_tags_df.empty:
        existing_tags = existing_tags_df.iloc[0]["tags"].split(",")
    currently_selected_tags = st_tags(
        label="", value=existing_tags, key=f'tags_{paper.abstract_url}', suggestions=TagsTable.DEFAULT_TAGS
    )
    currently_selected_tags = [tag.strip().lower() for tag in currently_selected_tags]


    if set(currently_selected_tags) != set(existing_tags):
        if not currently_selected_tags:
            tags_table.delete_by(
                column="paper_id",
                value=paper.abstract_url,
            )
            st.success("Tags deleted successfully")
        else:
            tags_table.update_or_create(
                by_key="paper_id",
                by_value=paper.abstract_url,
                new_values={"tags": ",".join(currently_selected_tags)},
            )
            st.success("Tags updated successfully")


def render_reading_progress(paper):
    query_progress = PaperMetadataFromUser().load_with_value(
        "abstract_url", paper.abstract_url
    )
    if not query_progress.empty:
        current_progress = int(query_progress.iloc[0]["progress"])
    else:
        current_progress = 0

    new_set_progress = st.select_slider(
        "Reading progress", options=tuple(range(0, 105, 5)), value=current_progress
    )
    if new_set_progress != current_progress:
        PaperMetadataFromUser().update_or_create(
            by_key="abstract_url",
            by_value=paper.abstract_url,
            new_values={"progress": new_set_progress},
        )
        st.success("Progress updated successfully")


@st.dialog("Load a different paper")
def load_different_paper():
    default_url = st.query_params.get("paper_url", "")
    url = st.text_input(
        "Paper URL",
        value=default_url,
        key="paper_url",
        help="Type the URL of the paper to be loaded",
    )
    if url:
        url = url.strip()
        if ArxivPaper.is_abstract_url(url):
            url = url.replace("https", "http")
        url = url.replace("file:///", "/")
        url = url.replace("/pdf/", "/abs/")
        url = url.replace("www.", "")
        st.query_params.paper_url = url
    c1, c2 = st.columns([1, 1])
    with c1:
        load = st.button("Load Paper")
        if load:
            st.rerun()
    with c2:
        add = st.button("Add new Paper")
        if add:
            create_new(url)
