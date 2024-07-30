

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

insights = [
    {'text': "RegionDrag offers an innovative region-based approach for image editing, drastically reducing the editing time to about 1.5 seconds for a 512x512 image compared to up to 3 minutes using point-drag methods." },
    {'text': "This method leverages dense mapping between handle and target regions along with attention-swapping techniques to ensure high fidelity and alignment with user intentions." }
]
import uuid;
for k, insight in enumerate(insights):
    id = str(uuid.uuid4())
    st.markdown(f"{k}. {insight['text']}")
    st.feedback('faces', key=id)
    st.divider()