from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationsHistoryTable,
)
import streamlit as st

st.title("Past recommendations")
st.divider()

df = (
    RecommendationsHistoryTable()
    .read()
    .sort_values(by="tdw_timestamp", ascending=False)
)


@st.dialog("More info")
def preview(row):
    with st.expander("Prompt"):
        st.write(row["prompt"])

    st.write("Papers recommended")
    urls = PapersUrlsExtractor().extract_urls(row["summary"])
    st.write(len(urls))
    st.write(row["summary"])


for index, row in enumerate(df.to_dict(orient="records")):
    papers_analysed = len(row["papers_analysed"].split("\n"))

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown(f"""
            ##### Generated at: {str(row["tdw_timestamp"]).split('.')[0]}
            ###### Number of Papers Analysed: {papers_analysed}
        """)
    with c2:
        st.markdown(f"""
            ###### From Date: {row["from_date"]}
            ###### To Date {row["to_date"]}
        """)
    with c3:
        st.link_button(
            "Open report",
            "/?search_type=Recommendations+from+Latest+Papers&report_uuid="
            + row["tdw_uuid"],
        )
        if st.button("Preview", key=f"preview_{index}"):
            preview(row)

    st.divider()
