from state_of_the_art.app.data import insights
import uuid;
import streamlit as st

paper =  {
    'title': 'Artificial Intuition: Efficient Classification of Scientific Abstract',
    'url': "https://arxiv.org/abs/2407.18248"
}

st.text_input("Open another paper", value='', key='paper_url', help="Enter the URL of the paper") 
st.button("Open")


st.markdown(f"### Paper: {paper['title']}")
st.link_button("Open this paper", paper['url'])

st.button("Extract insights")

st.markdown("#### Insights")

for k, insight in enumerate(insights):
    id = str(uuid.uuid4())
    st.markdown(f"{k}. {insight['text']}")
    st.feedback('faces', key=id)
    st.divider()