import streamlit as st

st.title("Topics")


st.markdown("### Ethics")
st.text_area("Description", value="Ethics is the branch of philosophy that involves systematizing, defending, and recommending concepts of right and wrong conduct. The field of ethics, along with aesthetics, concerns matters of value, and thus comprises the branch of philosophy called axiology. Ethics seeks to resolve questions of human morality by")
st.selectbox("Notified of new", ['Never', 'Weekly'])

st.markdown("### MLops")
st.text_area("Description", key='22', value="MLOPs is a practice for collaboration and communication between data scientists and IT professionals while automating the process of machine learning model deployment and management. It is a combination of 'machine learning' and 'operations'.")
st.selectbox("Notified of new", ['Never', 'Weekly'], key='222')