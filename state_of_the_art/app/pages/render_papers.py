from typing import Optional
from state_of_the_art.app.utils.paper_details_utils import render_tags_for_paper
from state_of_the_art.tables.tags_table import TagsTable
import streamlit as st

from state_of_the_art.config import config
from state_of_the_art.text_feedback.feedback_elements import render_feedback


@st.dialog("More details")
def preview(paper):
    st.markdown("Title: " + paper.title)
    st.markdown("Published at: " + paper.published_date_str())
    st.markdown(paper.abstract)


tags_table = TagsTable()

def render_papers():
    pass


class PapersRenderer:
    def __init__(self, disable_save_button=False, enable_tags=False):
        self.disable_save_button = disable_save_button
        self.enable_tags = enable_tags
    def render_papers(
        self,
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
                c1, c2= st.columns([7, 3])
                with c1:
                    st.markdown(
                        f"""##### {k+1}. [{paper.title}](./paper_details_page?paper_url={paper.abstract_url})"""
                    )
                    render_feedback(paper.title, type='paper_title')
                    st.write(f"({paper.published_date_str()})")
                    if (
                        papers_metadata
                        and paper.abstract_url in papers_metadata
                        and "labels" in papers_metadata[paper.abstract_url]
                    ):
                        for label in papers_metadata[paper.abstract_url]["labels"]:
                            st.markdown(f"###### {label}")
                    

                with c2:
                    if st.button("More", key=f"feedback{k}"):
                        preview(paper)
                    if not self.disable_save_button:
                        if st.button("Save", key=f"save{k}"):
                            tags_table.add_tag_to_paper(paper.abstract_url, "save for later")
                            st.success("Saved")
                    if self.enable_tags:
                        if st.button("Edit Tags", key=f"etags{k}") or ('tags_table' in st.session_state and paper.abstract_url in st.session_state.tags_table):
                            render_tags_for_paper(paper)
                            if not 'tags_table' in st.session_state:
                                st.session_state.tags_table = [paper.abstract_url]
                            else:
                                st.session_state.tags_table.append(paper.abstract_url)
