
import streamlit as st
from state_of_the_art.tables.text_feedback_table import TextFeedbackTable

def render_feedback(text: str, type='paper_title', context=None):
    id = "".join([i for i in text if i.isalnum()])

    try:
        feedback_score = st.feedback(options="faces", key=f"feedback{id}")
        if feedback_score is not None:
            with st.spinner("Sending feedback..."):
                TextFeedbackTable().add_feedback(
                    text=text,
                    score=feedback_score,
                    type=type,
                    context=context
                )
                st.success(f"Feedback sent for text {text}!")
    except:
        st.error("Failed to render feedback component key = " + f"feedback{id}")