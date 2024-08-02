from state_of_the_art.insight_extractor.insights_table import InsightsTable
from state_of_the_art.paper.papers_data import PapersDataLoader
import streamlit as st
from state_of_the_art.app.data import papers

st.title("Papers History")

st.selectbox("Order", ["Most recent", "Most liked", "Least liked"])
st.divider()

it = InsightsTable()
from tiny_data_warehouse import DataWarehouse
tdw = DataWarehouse()
df = tdw.event('sota_paper_insight').sort_values(by='tdw_timestamp', ascending=False)

df = df[['abstract_url', 'tdw_timestamp']]
df = df.drop_duplicates(subset=['abstract_url'])
papers = df.to_dict(orient="records")[0:50]


for paper_dict in papers:
        try:
            paper = PapersDataLoader().load_paper_from_url(paper_dict["abstract_url"])
        except Exception:
            continue

        st.markdown(f"Paper: [{paper.title}](/paper_details?paper_url={paper.abstract_url})")
        st.markdown(f"Url: {paper.abstract_url}")
        st.markdown("Extracted: " + str(paper_dict['tdw_timestamp']).split(' ')[0])
        st.markdown("Published: " + paper.published_date_str())
        st.divider()

