from state_of_the_art.app.data import topics
import streamlit as st

st.title("Topics")

with st.expander("Email-me novel papers"):
    st.toggle("Enable")
    st.selectbox("Email frequency", ['Never', 'Weekly', 'Monthly'])
    

st.button("Add new topic")

for k, topic in enumerate(topics):
    st.markdown(f"### {topic['name']}")
    st.text_area("Description", key=k, value="Ethics is the branch of philosophy that involves systematizing, defending, and recommending concepts of right and wrong conduct. The field of ethics, along with aesthetics, concerns matters of value, and thus comprises the branch of philosophy called axiology. Ethics seeks to resolve questions of human morality by")
    st.button('Delete', key=f'd{k}')
    st.toggle("Include in email", key=f"e{k}")
    st.divider()
