
import streamlit as st

st.markdown("### Topics")

st.button("Add topic")

topics = [
    {'topic': 'ethics'}
]

for k, topic in enumerate(topics):
    st.markdown(f"{k}. {topic['topic']}")
    st.button('Delete')
    st.button('Edit')
    st.divider()