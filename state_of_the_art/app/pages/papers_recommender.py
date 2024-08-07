from state_of_the_art.app.data import papers, topics
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.recommender.generator import RecommenderTable
import streamlit as st

st.title("Papers Recommender")

with st.expander("Search Details"):
    problem_description = st.text_area("Query / Description", value=None)
    lookback_days = st.slider("Days to Look back", 2, 30, 2)
    st.selectbox("For Profile", ["jean", "gdp", "mlp", "mlops"])
    st.selectbox("Existing Topic", [topic["name"] for topic in topics])
    st.text("Topic name")
    st.selectbox("Search type", ["topic_summary", "literal"])
    c1, c2 = st.columns(2)
    c1.button("Save topic")
    c2.button("Delete topic")


c1, c2 = st.columns([1, 5])

with c1:
    generate_clicked = st.button("Generate")

with c2:
    mine_new_papers = st.checkbox("Mine new papers", False)


if generate_clicked:
    from state_of_the_art.recommender.generator import Recommender

    Recommender().generate(
        skip_register=not mine,
        problem_description=problem_description,
        skip_email=True,
        disable_open_pdf=True,
        number_lookback_days=lookback_days,
    )

latest_summary = RecommenderTable().get_latest().to_dict()
st.divider()
st.markdown(f"###### Generated at {str(latest_summary['tdw_timestamp']).split('.')[0]}")
with st.container():
    latest_urls = PapersUrlsExtractor().extract_urls(latest_summary['summary'])
    papers = PapersDataLoader().load_papers_from_urls(latest_urls)



    for k, paper in enumerate(papers):
        st.markdown(f"##### {k+1}. [{paper.title}](/paper_details?paper_url={paper.abstract_url})")

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.checkbox("Save for later", key=f"s{k}")
        with c2:
            st.checkbox("Mark as read", key=f"r{k}")
        with c3:
            st.feedback(options='faces', key=f"f{k}")
        st.markdown(f"Published: {paper.published_date_str()}")
        st.write('Abstract: ', paper.abstract[0:200] + " ...")
        with st.expander('Full abstract'):
            st.markdown(paper.abstract)

