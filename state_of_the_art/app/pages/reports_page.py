from state_of_the_art.recommender.past_recommendations_table import (
    PastRecommendationsTable,
)
import streamlit as st

st.title("Past recommendations")

df = PastRecommendationsTable().read().sort_values(by="tdw_timestamp", ascending=False)

st.dataframe(df)
