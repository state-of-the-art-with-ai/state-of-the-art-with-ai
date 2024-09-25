from state_of_the_art.config import config
from state_of_the_art.paper.arxiv_paper import ArxivPaper
import arxiv

from typing import List, Literal


class ArxivGateway:
    def find_by_id(self, ids) -> List[ArxivPaper]:
        search = arxiv.Search(id_list=ids, max_results=len(ids))

        return self._build_papers_from_results(search.results())

    def find_by_query(
        self,
        query=None,
        number_of_papers=None,
        sort_by: Literal["submitted", "relevance", "updated"] = "submitted",
    ) -> List[ArxivPaper]:
        if not number_of_papers:
            number_of_papers = config.papers_to_mine_per_query()

        if sort_by == "submitted":
            sort = arxiv.SortCriterion.SubmittedDate
        elif sort_by == "relevance":
            sort = arxiv.SortCriterion.Relevance
        elif sort_by == "updated":
            sort = arxiv.SortCriterion.LastUpdatedDate

        print("Searching by query: ", query)
        print("Sorting by: ", sort_by)

        search = arxiv.Search(
            query=query,
            max_results=number_of_papers,
            sort_by=sort,
            sort_order=arxiv.SortOrder.Descending,
        )
        return self._build_papers_from_results(search.results())

    def _build_papers_from_results(self, results):
        papers = []
        for r in results:
            paper = ArxivPaper(
                abstract_url=r.entry_id,
                title=r.title,
                abstract=r.summary,
                published=r.published,
                updated=r.updated,
            )
            papers.append(paper)
        return papers