from state_of_the_art.app.data import papers, topics
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.preferences.topic_table import Topics
from state_of_the_art.recommender.generator import RecommenderTable
import streamlit as st

st.title("Papers Recommender")
topics = Topics()
topics_df = topics.read()
topics_names = topics_df["name"].tolist()

with st.expander("Search Details"):
    selected_topic_name = st.selectbox("Existing Topic", topics_names)

    topic_name = ""
    topic_description = ""
    if selected_topic_name:
        topic_name = topics_df[topics_df["name"] == selected_topic_name].iloc[0]["name"]
        topic_description = topics_df[topics_df["name"] == selected_topic_name].iloc[0]["description"]

    topic_description = st.text_area("Query / Description", value=topic_description)
    topic_name = st.text_input("Topic name", value=topic_name)
    if st.button("Save topic"):
        topics.add(name=topic_name, description=topic_description)
        st.success("Topic saved successfully")

    if st.button("Delete topic"):
        topics.delete_by(column='name', value=topic_name)
        st.success("Topic deleted successfully")

    lookback_days = st.slider("Days to Look back", 2, 30, 2)
    st.selectbox("For Profile", ["jean", "gdp", "mlp", "mlops"])


c1, c2 = st.columns([1, 5])

with c1:
    generate_clicked = st.button("Generate")

with c2:
    mine_new_papers = st.checkbox("Mine new papers", False)


if generate_clicked:
    from state_of_the_art.recommender.generator import Recommender

    Recommender().generate(
        skip_register=not mine_new_papers,
        problem_description=topic_description,
        skip_email=True,
        disable_open_pdf=True,
        number_lookback_days=lookback_days,
    )

latest_summary = RecommenderTable().get_latest().to_dict()
st.divider()
st.markdown(f"###### Generated at {str(latest_summary['tdw_timestamp']).split('.')[0]}")
with st.container():
    latest_urls = PapersUrlsExtractor().extract_urls(latest_summary["summary"])
    papers = PapersDataLoader().load_papers_from_urls(latest_urls)

    for k, paper in enumerate(papers):
        st.markdown(
            f"##### {k+1}. [{paper.title}](/paper_details?paper_url={paper.abstract_url})"
        )

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.checkbox("Save for later", key=f"s{k}")
        with c2:
            st.checkbox("Mark as read", key=f"r{k}")
        with c3:
            st.feedback(options="faces", key=f"f{k}")
        st.markdown(f"Published: {paper.published_date_str()}")
        st.write("Abstract: ", paper.abstract[0:200] + " ...")
        with st.expander("Full abstract"):
            st.markdown(paper.abstract)
