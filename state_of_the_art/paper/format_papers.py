from typing import List

from state_of_the_art.paper.papers_data import Papers
from state_of_the_art.paper.text_extractor import PapersUrlsExtractor

class PapersFormatter:
    """ Class optimized to format a list of papers for reading """
    def __init__(self, disable_abstract=False):
        self.disable_abstract = disable_abstract
    def from_str(self, papers_str: str) -> str:
        urls = PapersUrlsExtractor().extract_urls(papers_str)
        papers = Papers().load_papers_from_urls(urls)
        return self.from_papers(papers)

    def from_papers(self, papers: List[Papers]) -> str:
        formatted_result = ""
        counter = 1
        for paper in papers:
            if self.disable_abstract:
                abstract = ""
            else:
                abstract = f"\n{paper.abstract[0:500]}"
            formatted_result += f"""
{counter}. {paper.title}  
{paper.url} {paper.published_date_str()}
{abstract}
            """
            counter = counter + 1
        return formatted_result
