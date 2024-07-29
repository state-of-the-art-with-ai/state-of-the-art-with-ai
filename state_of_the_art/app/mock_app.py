import streamlit as st

st.title('Papers')

st.button('Generate Report')

with st.sidebar:
    history_window = st.button("Profile")


st.markdown("#### [Artificial Intuition: Efficient Classification of Scientific Abstract]()")
st.markdown("#### [LLM Internal States Reveal Hallucination Risk Faced With a Query]()")
st.markdown("#### [Evaluating Deep Neural Networks in Deployment: A Comparative Study (Replicability Study)]()")