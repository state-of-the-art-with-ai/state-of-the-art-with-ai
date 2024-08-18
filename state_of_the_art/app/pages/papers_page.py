from state_of_the_art.app.data import papers, topics
from state_of_the_art.app.pages.papers_page_utils import RecommenationTypes, edit_profile, get_papers_from_summary, load_papers_from_insights
from state_of_the_art.insight_extractor.insights_table import InsightsTable
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.tags_table import TagsTable
from state_of_the_art.preferences.topic_table import Topics
import streamlit as st

num_of_results = 15
lookback_days = None
topic_description = None
num_of_results = 15

st.title("Discover Papers")
papers = None
send_by_email = False


search_types = [item.value for item in RecommenationTypes]
default_search_index = 0
if 'search_type' in st.query_params:
    default_ui = st.query_params['search_type']
    default_search_index = search_types.index(default_ui)


selected_ui = st.selectbox('Search Types', search_types, index=default_search_index)
st.query_params['search_type'] = selected_ui
with st.expander("Search options", expanded=True):
    if selected_ui == RecommenationTypes.recommendation or selected_ui == RecommenationTypes.by_interest:

        if selected_ui == 'By Interest':
            topics = Topics()
            topics_df = topics.read()
            topics_names = [""] + topics_df["name"].tolist()

            default_interest = 0 if 'interest' not in st.query_params else topics_names.index(st.query_params['interest'])

            selected_interest = st.selectbox("Existing Interest", topics_names, index=default_interest)

            if selected_interest:
                st.query_params['interest'] = selected_interest

            interest_name = ""
            topic_description = ""
            if selected_interest:
                interest_name = topics_df[topics_df["name"] == selected_interest].iloc[0]["name"]
                topic_description = topics_df[topics_df["name"] == selected_interest].iloc[0]["description"]

            topic_description = st.text_area("Query / Description", value=topic_description)
            interest_name = st.text_input("Interest name", value=interest_name)


            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save Interest"):
                    topics.add(name=interest_name, description=topic_description)
                    st.query_params['interest'] = interest_name
                    st.success("Interest saved successfully")
                    st.rerun()
            with c2:
                if st.button("Delete Interest"):
                    topics.delete_by(column='name', value=interest_name)
                    st.success("Interest deleted successfully")

        if selected_ui == RecommenationTypes.recommendation:
            lookback_days = st.slider("Days to Look back", 2, 30, 2)

        c1, c2 = st.columns([3, 1])
        with c1:
            current_profile = st.selectbox("Profile", ["jean", "gdp", "mlp", "mlops"])
        with c2:
            if st.button("Manage Profile"):
                edit_profile(current_profile)



        c1, c2, c3 = st.columns([2, 3, 2])

        with c1:
            generate_clicked = st.button("Generate new recommendations")

        with c2:
            mine_new_papers = st.toggle("Mine new papers", False)
            send_by_email = st.toggle("Send By email", False)
        if generate_clicked:
            from state_of_the_art.recommender.generator import Recommender

            Recommender().generate(
                skip_register=not mine_new_papers,
                problem_description=topic_description,
                skip_email=not send_by_email,
                disable_open_pdf=True,
                disable_pdf=True,
                number_lookback_days=lookback_days,
            )

        with c3:
            num_of_results = st.selectbox("Num of results", [15, 50, 100])

    if selected_ui == RecommenationTypes.insights_history:
        load_no = st.selectbox("Number of papers to load", [50, 100, 200])
        papers = load_papers_from_insights(load_no=load_no)

    if selected_ui == RecommenationTypes.by_tags:
        all_tags_df = TagsTable().read()
        all_tags = all_tags_df['tags'].to_list()
        all_tags = [tags.split(',') for tags in all_tags]
        import itertools
        merged = list(itertools.chain(*all_tags))
        unique = list(set(merged))
        
        selected_tags = st.multiselect("Tags", unique)
        all_papers_selected = all_tags_df[all_tags_df['tags'].str.contains('|'.join(selected_tags))]
        all_papers_selected = all_papers_selected['paper_id'].to_list()

        unique_papers = list(set(all_papers_selected))

        papers = PapersDataLoader().load_papers_from_urls(unique_papers)[0:num_of_results]

        

    generated_date = None
    if not papers:
        papers, generated_date = get_papers_from_summary(num_of_results=num_of_results)


st.divider()

if generated_date:
    st.markdown(f"###### Generated at {str(generated_date).split('.')[0]}")
with st.container():

    for k, paper in enumerate(papers):
        st.markdown(
            f"##### {k+1}. [{paper.title}](/paper_details_page?paper_url={paper.abstract_url})"
        )

        st.markdown(f"Published: {paper.published_date_str()}")
        with st.expander("Full abstract"):
            st.markdown(paper.abstract)
