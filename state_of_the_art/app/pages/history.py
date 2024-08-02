from state_of_the_art.insight_extractor.insiths_table import InsightsTable
from state_of_the_art.paper.papers_data import PapersDataLoader
import streamlit as st
from state_of_the_art.app.data import papers, insights
st.title('Your Insights History')

st.selectbox("Order", ['Most recent', 'Most liked', 'Least liked'])
st.divider()

it = InsightsTable()
df = it.read().sort_values(by='tdw_timestamp', ascending=False)

papers = df.to_dict(orient="records")[0:50]

printed_title=False
last_paper_id = papers[0]['paper_id']
for insight in papers:
    if not printed_title:
        paper = PapersDataLoader().load_paper_from_url(insight['paper_id'])
        st.markdown(f"Paper: [{paper.title}]({insight['paper_id']})")
        st.markdown(f"Url: {insight['paper_id']}")
        st.markdown('Published: ' + paper.published_date_str())
        st.markdown(f"Date: {insight['tdw_timestamp']}")
        printed_title=True

    st.markdown('- ' + insight['insight'])
    feedback_received = st.feedback(options="faces", key=insight['tdw_uuid'])
    st.write('Current Score: ', insight['score'])
    if feedback_received:
        it.update_score(insight['tdw_uuid'], feedback_received)
    if insight['paper_id'] != last_paper_id:
        st.divider()
        printed_title=False

    last_paper_id = insight['paper_id']