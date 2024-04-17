from typing import List

from state_of_the_art.paper.papers_data import Papers
from state_of_the_art.paper.text_extractor import PapersUrlsExtractor

class PapersFormatter:
    """ Class optimized to format a list of papers for reading """
    def from_str(self, papers_str: str) -> str:
        urls = PapersUrlsExtractor().extract_urls(papers_str)
        papers = Papers().load_papers_from_urls(urls)
        return self.from_papers(papers)

    def from_papers(self, papers: List[Papers]) -> str:
        formatted_result = ""
        counter = 1
        for paper in papers:
            formatted_result += f"""
{counter}. {paper.title[0:100]}  
{paper.url} {paper.published_date_str()}
{paper.abstract[0:500]}
            """
            counter = counter + 1
        return formatted_result
