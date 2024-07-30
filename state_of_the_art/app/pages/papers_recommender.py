from state_of_the_art.app.data import papers
import streamlit as st

st.title('Papers Recommender')


st.selectbox("For Profile", ['jean', 'gdp', 'mlp', 'mlops'])

st.text_area("Query / Problem description")

with st.expander("Topics Details"):
    st.selectbox("Existing Topic", ['Select', 'ethics', 'mlops'])
    st.text("Topic name")
    st.selectbox("Search type", ['topic_summary', 'literal'])
    c1, c2  = st.columns(2)
    c1.button("Save topic")
    c2.button('Delete topic')

st.button('Generate')
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
