from typing import Optional
from state_of_the_art.paper.tags_table import TagsTable
import streamlit as st


@st.dialog("More details")
def preview(paper):
    st.markdown("Published at: " + paper.published_date_str())
    st.markdown(paper.abstract)

tags_table = TagsTable()

def render_papers(papers, generated_date=None, metadata: Optional[dict] = None, max_num_of_renderable_results=None):


    if generated_date:
        st.markdown(f"###### Generated at {str(generated_date).split('.')[0]}")
    if metadata:
        for k, v in metadata.items():
            st.markdown(f"###### {k}: {v}")
    with st.container():
        if not papers:
            st.markdown("No papers found")
            return
        else:
            st.markdown(f"#### {len(papers)} papers found")

        for k, paper in enumerate(papers[0:max_num_of_renderable_results]):
            c1, c2, c3 = st.columns([7, 1, 1])
            with c1:
                st.markdown(
                    f"""##### {k+1}. [{paper.title}](/paper_details_page?paper_url={paper.abstract_url})
###### ({paper.published_date_str()}) """ 
                )
            with c2:
                if st.button(
                    "More", key=f"preview{k}"
                ):
                    preview(paper)
                    
            with c3:
                if st.button("Save", key=f"save{k}"):
                    tags_table.add_tag_to_paper(paper.abstract_url, "save For Later")
                    st.success("Saved")


