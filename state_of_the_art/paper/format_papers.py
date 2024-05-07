from typing import List

from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor


class PapersFormatter:
    """
    from a list of strings or a list of papers return a reading formattted optimzed ouput

    """

    def __init__(self, show_abstract=True, max_abstract_size=500):
        self.show_abstract = show_abstract
        self.max_abstract_size = max_abstract_size

    def from_str(self, papers_str: str) -> str:
        urls = PapersUrlsExtractor().extract_urls(papers_str)
        papers = PapersInDataWharehouse().load_papers_from_urls(urls)
        return self.from_papers(papers)

    def from_papers(self, papers: List[PapersInDataWharehouse]) -> str:
        formatted_result = ""
        counter = 1
        for paper in papers:
            if not self.show_abstract:
                abstract = ""
            else:
                abstract = f"Abstract: {paper.abstract[0:self.max_abstract_size]}"
            formatted_result += f"""
{counter}. {paper.title}  
{paper.url} {paper.published_date_str()}
{abstract}\n\n"""

            counter = counter + 1
        return formatted_result
