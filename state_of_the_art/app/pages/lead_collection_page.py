

import streamlit as st

st.markdown("""
## Welcome to our platform
If you are interested in our idea please register your email here. 
I will eventually get back to you.
""")

email = st.text_input("Type your email here")

if st.button("Submit"):
    st.success("Thank you for your interest. I will get back to you soon.")