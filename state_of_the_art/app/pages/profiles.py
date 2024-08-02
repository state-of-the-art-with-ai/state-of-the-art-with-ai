import streamlit as st

st.title("Profile Personalization")

profiles = [
    {
        "name": "Jean",
        "description": """Jean Machado, a Data Science Manager for GetYourGuide.
Jean wants the following out this tool:
2. to understand exciting and important topics with further depth
1. to have actionable insights and learnings he can apply in his teams
3. to stay on the bleeding edge of the field

to see what is going on on important institutions and companies in the field of data science and machine learning and computer science

Jean manages the following teams in GetYourGuide:
Jean is interseted in the following high level topics:

- data science
- ai for social good
- experimentation design, analysis and interpretation
- search engine optimization
- ai ethics
- data science leadership
- truth, and fake news
""",
    },
    {
        "name": "GDP",
        "description": """Growth Data Products is a team in GetYourGuide that is responsible for the data science and machine learning for growing the business
You provide insights to GDP manager to share with the team :)
The mission of the team is to  optimize multi-channel customer acquisition and customer loyalty by building data products.
to see what is going on on important institutions and companies in the field of data science and machine learning
""",
    },
]

st.button("Add profile")

for profile in profiles:
    st.text_input("Profile Name", value=profile["name"])
    st.text_area("Your description", value=profile["description"], height=500)
    st.button("Remove", key=profile["name"])
    st.divider()
