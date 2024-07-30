import streamlit as st

st.title('Papers Overview')


with st.popover("Settings"):
    st.number_input("Number of days", 0, 30)
    st.text_input("Query")
    st.text_area("Problem description")
    st.text("Topic name")
    st.button("Save topic")


st.button('Generate Report')
with st.sidebar:
    st.button("Logout")

papers = [
    {'title' :'Artificial Intuition: Efficient Classification of Scientific Abstract' },
    {'title': 'LLM Internal States Reveal Hallucination Risk Faced With a Query'},
    {'title': 'Evaluating Deep Neural Networks in Deployment: A Comparative Study '}

]

for k, paper in enumerate(papers):
    st.markdown(f"##### {k+1} [{paper['title']}](paper_dive) [Paper](pdf)")