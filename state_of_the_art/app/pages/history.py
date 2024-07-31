import streamlit as st
from state_of_the_art.app.data import papers, insights
st.title('Your Insights')

st.selectbox("Order", ['Most recent', 'Most liked', 'Least liked'])

st.divider()

from tiny_data_warehouse import DataWarehouse
tdw = DataWarehouse()
df = tdw.event('sota_paper_insight').sort_values(by='tdw_timestamp', ascending=False)

for insight in df.to_dict(orient="records")[0:50]:
    st.markdown('- ' + insight['insights'])
    st.markdown(f"Paper: [paper]({insight['abstract_url']})")
    st.divider()
