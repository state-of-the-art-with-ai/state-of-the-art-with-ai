import time
from state_of_the_art.app.data import papers, topics
from state_of_the_art.app.utils.render_papers import PapersRenderer
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.search.bm25_search import Bm25Search, PrecomputedSearch
from state_of_the_art.tables.interest_table import InterestTable
import streamlit as st

@st.cache_data
def load_bm25_papers():
    return PrecomputedSearch().load_papers_from_pickle()

generated_date = None
lookback_days = None
topic_description = None

st.title("Your Interests")
papers = None
send_by_email = False

topics = InterestTable()
topics_df = topics.read(recent_first=True)
topics_names = topics_df["name"].tolist()

c1, c2 = st.columns([2, 1])
with c2:
    with st.expander("Interests", expanded=True):
        if len(topics_names) > 0:
            st.write(f"{len(topics_names)} Interests registered")

        for topic in topics_names:
            try:
                if st.button(topic, key=f"t{topic}"):
                    st.query_params["interest"] = topic
            except:
                pass
with c1:
    if "interest" in st.query_params:
        selected_interest = st.query_params["interest"]
    else:
        selected_interest = topics_names[-1] if topics_names else ""

    if selected_interest:
        interest_name = topics_df[topics_df["name"] == selected_interest].iloc[0]["name"] 
        topic_description = topics_df[topics_df["name"] == selected_interest].iloc[0][
            "description"
        ]
    else: 
        interest_name = ""
        topic_description = ""


    interest_name = st.text_input("Interest name", value=interest_name)
    topic_description = st.text_area("Query / Description", value=topic_description)

    c1, c2 = st.columns([1, 7])
    with c1:
        if st.button("Save"):
            topics.add(name=interest_name, description=topic_description)
            st.query_params["interest"] = interest_name
            st.success("Interest saved successfully")
            time.sleep(0.1)
            st.rerun()
    with c2:
        if st.button("Delete"):
            topics.delete_by(column="name", value=interest_name)
            del st.query_params["interest"]
            st.rerun()
            st.success("Interest deleted successfully")


    if not interest_name:
        st.error("You need to create an interest to get started")
        st.stop()

    st.write(f"Selected interest: {interest_name}")
st.divider()
papers = load_bm25_papers().search_returning_papers(
    interest_name + " " + topic_description
)

# render all papeers
PapersRenderer().render_papers(papers, generated_date=generated_date)
