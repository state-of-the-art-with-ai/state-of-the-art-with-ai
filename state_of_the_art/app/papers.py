import streamlit as st

st.title('Papers Overview')


st.button('Generate Report')

col1, col2 = st.columns([1, 1])

with col1:
    st.number_input("Number of days", 0, 30)
with col2:
    st.text_input("Query")


with st.sidebar:
    st.button("Logout")

papers = [
    {'title' :'Artificial Intuition: Efficient Classification of Scientific Abstract' },
    {'title': 'LLM Internal States Reveal Hallucination Risk Faced With a Query'},
    {'title': 'Evaluating Deep Neural Networks in Deployment: A Comparative Study '}

]

for paper in papers:
    st.markdown(f"##### [{paper['title']}](paper_dive) [Paper](pdf)")