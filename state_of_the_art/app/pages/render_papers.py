from typing import Optional
import streamlit as st


@st.dialog("More details")
def preview(paper):
    st.markdown(paper.abstract)
    st.markdown("Published at: " + paper.date_published_str())


def render_papers(papers, generated_date=None, metadata: Optional[dict] = None, max_num_of_renderable_results=15):
    if generated_date:
        st.markdown(f"###### Generated at {str(generated_date).split('.')[0]}")
        if metadata:
            for k, v in metadata.items():
                st.markdown(f"###### {k}: {v}")
    with st.container():
        for k, paper in enumerate(papers[0:max_num_of_renderable_results]):
            c1, c2, c3 = st.columns([7, 1, 1])
            with c1:
                st.markdown(
                    f"##### {k+1}. [{paper.title}](/paper_details_page?paper_url={paper.abstract_url})"
                )
            with c2:
                st.button(
                    "More", key=f"p{k}", on_click=preview, args=(paper,)
                )
            with c3:
                st.button("Save", key=f"save{k}",)
