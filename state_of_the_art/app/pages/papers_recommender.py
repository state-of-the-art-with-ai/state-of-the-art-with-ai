from state_of_the_art.app.data import papers, topics
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

mine = st.checkbox('Mine new papers', True)

if st.button("Generate"):
    from state_of_the_art.recommender.generator import Recommender
    Recommender().generate(skip_register=not mine, problem_description=problem_description)

with st.sidebar:
    st.button("Logout")

with st.container():
    st.divider()
    for k, paper in enumerate(papers):
        st.markdown(f"##### {k+1}. [{paper['title']}](paper_dive)")
        st.markdown(f"Paper url: [Url]({paper['arxiv_url']})")
        st.markdown(f"Abstract: {paper['abstract']}")
        st.feedback(key=f"f{k}")
        st.divider()
