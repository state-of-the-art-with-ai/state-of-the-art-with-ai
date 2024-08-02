from state_of_the_art.app.data import papers, topics
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.recommender.generator import RecommenderTable
import streamlit as st

st.title("Papers Recommender")


problem_description = st.text_area("Query / Description", value=None)

with st.expander("Search Details"):
    st.selectbox("For Profile", ["jean", "gdp", "mlp", "mlops"])
    st.selectbox("Existing Topic", [topic["name"] for topic in topics])
    st.text("Topic name")
    st.selectbox("Search type", ["topic_summary", "literal"])
    c1, c2 = st.columns(2)
    c1.button("Save topic")
    c2.button("Delete topic")

mine = st.checkbox("Mine new papers", False)

if st.button("Generate"):
    from state_of_the_art.recommender.generator import Recommender

    Recommender().generate(
        skip_register=not mine, problem_description=problem_description, skip_email=True, disable_open_pdf=True
    )

with st.sidebar:
    st.button("Logout")



with st.container():
    st.divider()

    latest_summary = RecommenderTable().get_latest().to_dict()
    latest_urls = PapersUrlsExtractor().extract_urls(latest_summary['summary'])
    papers = PapersDataLoader().load_papers_from_urls(latest_urls)

    for k, paper in enumerate(papers):
        st.markdown(f"##### {k+1}. [{paper.title}](/paper_details?paper_url={paper.abstract_url})")
        st.markdown(f"Published: {paper.published_date_str()}")
        st.markdown(f"Abstract: {paper.abstract}")
        st.feedback(key=f"f{k}")
        st.divider()
