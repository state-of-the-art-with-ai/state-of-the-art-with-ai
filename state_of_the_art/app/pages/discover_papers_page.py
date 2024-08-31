from enum import Enum
from state_of_the_art.app.data import papers, topics
from state_of_the_art.app.pages.papers_page_utils import (
    edit_profile,
    load_papers_from_last_report,
)
from state_of_the_art.app.pages.render_papers import render_papers
from state_of_the_art.user_preferences.interest_table import Interests
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
import datetime
import streamlit as st


class DiscoveryPageTypes(str, Enum):
    all_latest = "All latest papers"
    by_interest = "Following your Interests"


generated_date = None
lookback_days = None
topic_description = None

st.title("Discover Papers")
papers = None
send_by_email = False


search_types = [item.value for item in DiscoveryPageTypes]
default_search_index = 0
if "search_type" in st.query_params:
    default_ui = st.query_params["search_type"]
    default_search_index = search_types.index(default_ui)


selected_ui = st.selectbox("Search Types", search_types, index=default_search_index)
st.query_params["search_type"] = selected_ui
with st.expander("Search options", expanded=True):
    if (
        selected_ui == DiscoveryPageTypes.by_interest
    ):
        if selected_ui == DiscoveryPageTypes.by_interest:
            topics = Interests()
            topics_df = topics.read()
            topics_names = [""] + topics_df["name"].tolist()

            default_interest = (
                0
                if "interest" not in st.query_params
                else topics_names.index(st.query_params["interest"])
            )

            selected_interest = st.selectbox(
                "Existing Interest", topics_names, index=default_interest
            )

            if selected_interest:
                st.query_params["interest"] = selected_interest

            interest_name = ""
            topic_description = ""
            if selected_interest:
                interest_name = topics_df[topics_df["name"] == selected_interest].iloc[
                    0
                ]["name"]
                topic_description = topics_df[
                    topics_df["name"] == selected_interest
                ].iloc[0]["description"]

            topic_description = st.text_area(
                "Query / Description", value=topic_description
            )
            interest_name = st.text_input("Interest name", value=interest_name)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save Interest"):
                    topics.add(name=interest_name, description=topic_description)
                    st.query_params["interest"] = interest_name
                    st.success("Interest saved successfully")
                    st.rerun()
            with c2:
                if st.button("Delete Interest"):
                    topics.delete_by(column="name", value=interest_name)
                    st.success("Interest deleted successfully")

        c1, c2 = st.columns([3, 1])
        with c1:
            current_profile = st.selectbox("Profile", ["jean", "gdp", "mlp", "mlops"])
        with c2:
            if st.button("Manage Profile"):
                edit_profile(current_profile)

        c1, c2 = st.columns([2, 3])

        with c1:
            generate_clicked = st.button("Generate new recommendations")

        with c2:
            mine_new_papers = st.toggle("Mine new papers", False)
            send_by_email = st.toggle("Send By email", False)
        if generate_clicked:
            from state_of_the_art.deprecated_recommender.generator import Recommender

            with st.spinner("Generating recommendations"):
                Recommender().generate(
                    skip_register=not mine_new_papers,
                    problem_description=topic_description,
                    skip_email=not send_by_email,
                    disable_open_pdf=True,
                    disable_pdf=True,
                    number_lookback_days=lookback_days,
                )

                papers, generated_date = load_papers_from_last_report()


    if selected_ui == DiscoveryPageTypes.all_latest:
        from state_of_the_art.paper.papers_data_loader import PapersLoader


        if "date" in st.query_params:
            default_date_filter = st.query_params["date"]
            default_date_filter = datetime.datetime.strptime(default_date_filter, "%Y-%m-%d").date()
        else:
            default_date_filter=  ArxivMiner().latest_date_with_papers()

        date_filter = st.date_input("Date", value=default_date_filter)
        st.query_params["date"] = date_filter
        papers = PapersLoader().load_papers()
        papers = papers[papers["published"].dt.date == date_filter]
        papers = PapersLoader().to_papers(papers)


st.divider()

# render all papeers
render_papers(papers, generated_date=generated_date)
