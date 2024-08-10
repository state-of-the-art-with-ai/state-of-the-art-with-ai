from state_of_the_art.app.data import papers, topics
from state_of_the_art.insight_extractor.insights_table import InsightsTable
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.preferences.topic_table import Topics
from state_of_the_art.recommender.generator import RecommenderTable
import streamlit as st

def load_papers():
    from tiny_data_warehouse import DataWarehouse

    tdw = DataWarehouse()
    df = tdw.event("sota_paper_insight").sort_values(by="tdw_timestamp", ascending=False)

    df = df[["abstract_url", "tdw_timestamp"]]
    df = df.drop_duplicates(subset=["abstract_url"])
    papers = df.to_dict(orient="records")[0:50]
    papers_urls = [paper['abstract_url'] for paper in  papers]
    papers = PapersDataLoader().load_papers_from_urls(papers_urls)

    return papers


def get_papers_from_summary():
    latest_summary = RecommenderTable().get_latest().to_dict()
    latest_urls = PapersUrlsExtractor().extract_urls(latest_summary["summary"])
    papers = PapersDataLoader().load_papers_from_urls(latest_urls)[0:15]

    return papers, latest_summary['tdw_timestamp']


st.title("Papers")
papers = None

tab1, tab2 = st.tabs(['Search', 'Insights history'])

with tab1:
    topics = Topics()
    topics_df = topics.read()
    topics_names = [""] + topics_df["name"].tolist()

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


    c1, c2 = st.columns([2, 4])

    with c1:
        generate_clicked = st.button("Generate new recommendations")

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


with tab2:
    if st.button("Load"):
        papers = load_papers()

generated_date = None
if not papers:
    papers, generated_date = get_papers_from_summary()


st.divider()
if generated_date:
    st.markdown(f"###### Generated at {str(generated_date).split('.')[0]}")
with st.container():

    for k, paper in enumerate(papers):
        st.markdown(
            f"##### {k+1}. [{paper.title}](/paper_details_page?paper_url={paper.abstract_url})"
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
