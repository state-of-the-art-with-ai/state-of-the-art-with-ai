from typing import Callable, List, Optional
from state_of_the_art.app.utils.paper_details_utils import render_tags_for_paper
from state_of_the_art.insight_extractor.insight_extractor import AIInsightsExtractor
from state_of_the_art.paper.paper_entity import Paper
from state_of_the_art.tables.insights_table import InsightsTable
from state_of_the_art.tables.tags_table import TagsTable
import streamlit as st

from state_of_the_art.config import config
from state_of_the_art.text_feedback.feedback_elements import render_feedback


@st.dialog("More details")
def preview(paper):
    st.markdown("Title: " + paper.title)
    st.markdown(paper.abstract)


tags_table = TagsTable()

def render_papers():
    pass


class PapersRenderer:

    def __init__(self, disable_save_button=False, enable_tags=False, enable_pagination=False):
        self.disable_save_button = disable_save_button
        self.enable_tags = enable_tags
        self.enable_pagination = enable_pagination
        self.current_page = int(st.query_params.get("page", 1))
        self.enable_pagination = enable_pagination  
        self.total_papers_passed = None

    def paginate_paper_list(self, paper_list: List[Paper]):
        PAGE_SIZE = 30
        FROM_INDEX = (self.current_page - 1) * PAGE_SIZE
        TO_INDEX = FROM_INDEX + PAGE_SIZE
        return paper_list[FROM_INDEX:TO_INDEX]
    
    def _render_pagination_ui(self):
        c1, c2 = st.columns([1,5])
        with c1:
            if st.button("Previous page"):
                self.current_page = self.current_page - 1 if self.current_page > 1 else 1
                st.query_params['page'] = self.current_page
                st.rerun()
        with c2:
            if st.button("Next page"):
                self.current_page += 1
                st.query_params['page'] = self.current_page
                st.rerun()


    def render_papers(
        self,
        papers: Optional[List[Paper]] = None,
        papers_metadata: Optional[dict[str, str]] = None,
        generated_date=None,
        metadata: Optional[dict[str, str]] = None,
        max_num_of_renderable_results=None,
        collapse_metadata=False,
    ):
        """
        metadata is a dictionary with the metadata to be displayed as titles
        """

        
        self.total_papers_passed = len(papers)
        with st.spinner("Paginating papers ..."):
            papers = self.paginate_paper_list(papers)

        with st.spinner("Rendering metadata ..."):
            with st.expander("Metadata", expanded=not collapse_metadata):
                if generated_date:
                    st.markdown(f"###### Generated at {str(generated_date).split('.')[0]}")

                if self.enable_pagination:
                    st.markdown(f"###### Page {self.current_page}")
                if metadata:
                    for k, v in metadata.items():
                        st.markdown(f"###### {k}: {v}")


        if self.enable_pagination:
            self._render_pagination_ui()

        if not papers:
            st.markdown("No papers found")
            return
        else:
            st.markdown(f"#### {len(papers)} papers rendered out of {self.total_papers_passed}")
        insights_table = InsightsTable()
        with st.spinner("Rendering papers ..."):
            for k, paper in enumerate(papers[0:max_num_of_renderable_results]):
                ca, cb = st.columns([3, 1])
                with ca:
                    st.markdown(
                        f"""##### {k+1}. [{paper.title}](./paper_details_page?paper_url={paper.abstract_url})"""
                )
                with cb:
                    render_feedback(paper.title, type='paper_title')


                cd, ce = st.columns([1,1])
                with cd:
                    st.write(f"Published: {paper.published_date_str()}")
                with ce:
                    if (
                    papers_metadata
                    and paper.abstract_url in papers_metadata
                        and "labels" in papers_metadata[paper.abstract_url]
                    ):
                        for label in papers_metadata[paper.abstract_url]["labels"]:
                            st.markdown(f"###### {label}")

                c1, c2 = st.columns([5,1])
                with c1:
                    with st.expander("Top Insights", expanded=True):
                        defintions = insights_table.get_all_answers_cached("TopInsights", paper.abstract_url)
                        for definition in defintions[0:3]:
                            ca, cb = st.columns([3, 1])
                            with ca:    
                                st.markdown(" - " + definition)
                            with cb:
                                render_feedback(definition, type="paper_insight", context={'paper_id': paper.abstract_url})
                
                
                c1, c2, c3 = st.columns([1,1,1])
                with c1:
                    if st.button("Abstract", key=f"abstract{k}"):
                        preview(paper)
                with c2:
                    if st.button("Gen AI Insights", key=f"ai_insights{k}"):
                        with st.spinner("Generating..."):
                            AIInsightsExtractor().extract_insights_from_paper_url(paper.abstract_url)
                        st.rerun()
                with c3:
                    if not self.disable_save_button:
                        if st.button("Save into Your Papers", key=f"save{k}"):
                            tags_table.add_tag_to_paper(paper.abstract_url, "save for later")
                            st.success("Saved")
                    if self.enable_tags:
                        if st.button("Edit Tags", key=f"etags{k}") or ('tags_table' in st.session_state and paper.abstract_url in st.session_state.tags_table):
                            render_tags_for_paper(paper)
                        if not 'tags_table' in st.session_state:
                            st.session_state.tags_table = [paper.abstract_url]
                        else:
                            st.session_state.tags_table.append(paper.abstract_url)
