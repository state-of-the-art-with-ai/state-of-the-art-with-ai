import streamlit as st
from state_of_the_art.app.data import papers, insights
st.title('Your Evaluations')

st.selectbox("Order", ['Most recent', 'Most liked', 'Least liked'])

st.divider()

for k, insigt in enumerate(insights):
    st.markdown('- ' + insigt['text'])
    st.markdown("Paper: [paper]()")
    st.feedback(key=k)
    st.divider()
