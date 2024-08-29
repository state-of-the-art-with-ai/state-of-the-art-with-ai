import streamlit as st


@st.dialog("Abstract")
def preview(paper):
    st.markdown(paper.abstract)


def render_papers(papers, generated_date=None, num_of_results=15):
    if generated_date:
        st.markdown(f"###### Generated at {str(generated_date).split('.')[0]}")
    with st.container():
        for k, paper in enumerate(papers[0:num_of_results]):
            st.markdown(
                f"##### {k+1}. [{paper.title}](/paper_details_page?paper_url={paper.abstract_url})"
            )

            c1, c2 = st.columns([3, 1])
            with c1:
                st.button(
                    "Preview Abstract", key=f"p{k}", on_click=preview, args=(paper,)
                )
            with c2:
                st.markdown(f"Published: {paper.published_date_str()}")
