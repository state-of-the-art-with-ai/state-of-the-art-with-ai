from state_of_the_art.app.pages.discover_papers_page import DiscoveryPageTypes
import streamlit as st

pages = {
    "Pages": [
        st.Page("pages/discover_papers_page.py", title="Discover Papers"),
        st.Page("pages/your_papers_page.py", title="Your Papers"),
        st.Page("pages/paper_details_page.py", title="Dive into a Paper"),
        st.Page("pages/papers_report_page.py", title="Past Recomendations"),
    ],
}


pg = st.navigation(pages)
st.set_page_config(layout="wide")


with st.sidebar:
    st.link_button(
        "Find Papers By Interest",
        f"/?search_type={DiscoveryPageTypes.by_interest.value}",
    )


pg.run()
