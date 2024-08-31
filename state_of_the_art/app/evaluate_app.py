from state_of_the_art.tables.insights_table import InsightsTable
import streamlit as st


st.title("Insights")

df = InsightsTable().read()
df = df.sort_values(by="tdw_timestamp", ascending=False)

ratio_values = InsightsTable.SCORE_VALUES

for index, row in df.iterrows():
    c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
    c1.write(row["insight"])
    new_score = c2.radio(
        "Score",
        ratio_values,
        index=ratio_values.index(row["score"]),
        key=row["tdw_uuid"],
    )

    if new_score != row["score"]:
        InsightsTable().update_score(row["tdw_uuid"], new_score)

    c3.write(row["paper_id"])
    c4.write(row["tdw_timestamp"])
