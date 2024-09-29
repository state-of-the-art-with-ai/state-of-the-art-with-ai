from typing import Optional
from state_of_the_art.tables.tags_table import TagsTable
import streamlit as st

from state_of_the_art.tables.text_feedback_table import TextFeedbackTable


@st.dialog("More details")
def preview(paper):
    st.markdown("Title: " + paper.title)
    st.markdown("Published at: " + paper.published_date_str())
    st.markdown(paper.abstract)


tags_table = TagsTable()


def render_papers(
    papers,
    papers_metadata: Optional[dict[str, str]] = None,
    generated_date=None,
    metadata: Optional[dict[str, str]] = None,
    max_num_of_renderable_results=None,
):
    """
    metadata is a dictionary with the metadata to be displayed as titles
    """
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
            c1, c2, c3, c4 = st.columns([9, 2, 1, 1])
            with c1:
                st.markdown(
                    f"""##### {k+1}. [{paper.title}](/paper_details_page?paper_url={paper.abstract_url})
                """
                )
                if (
                    papers_metadata
                    and paper.abstract_url in papers_metadata
                    and "labels" in papers_metadata[paper.abstract_url]
                ):
                    for label in papers_metadata[paper.abstract_url]["labels"]:
                        st.markdown(f"###### {label}")
                feedback_score = st.feedback(options="thumbs", key=f"review{k}")
                if feedback_score is not None:
                    TextFeedbackTable().add_feedback(
                        text=paper.title,
                        score=feedback_score,
                        type='paper_title',
                    )
            with c2:
                st.write(f"({paper.published_date_str()})")
            with c3:
                if st.button("More", key=f"feedback{k}"):
                    preview(paper)
            with c4:
                if st.button("Save", key=f"save{k}"):
                    tags_table.add_tag_to_paper(paper.abstract_url, "save For Later")
                    st.success("Saved")
