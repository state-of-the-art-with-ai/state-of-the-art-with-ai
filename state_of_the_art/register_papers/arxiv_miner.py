import arxiv
from typing import Literal, List
from state_of_the_art.config import config
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from tqdm import tqdm
import datetime
import logging

from state_of_the_art.utils.internet import has_internet


class ArxivMiner:
    """
    Looks at arxiv api for papers
    """

    SORT_COLUMN = "submitted"

    def __init__(self):
        self.config = config
        tdw = config.get_datawarehouse()
        arxiv_papers = tdw.event("arxiv_papers")
        self.existing_papers_urls = (
            arxiv_papers["abstract_url"].values if not arxiv_papers.empty else []
        )
        self.tdw = config.get_datawarehouse()
        self.existing_papers_urls = self.load_existing_papers_urls()
        self.arxiv_gateway = ArxivGateway()

    def register_all_new_papers(
        self, dry_run=False, topic=None
    ):
        """
        Register all papers by looking in arxiv api with the keyworkds of the audience configuration
        :param dry_run:
        :param disable_relevance_miner:
        :return:
        """
        if dry_run:
            print("Dry run, just printing, not registering them")
        keywords_to_mine = self.config.KEYWORDS_TO_MINE

        print(
            f"Registering papers for the following ({len(keywords_to_mine)}) keywords: ",
            keywords_to_mine,
        )

        papers = []
        for topic in tqdm(keywords_to_mine):
            print("Mining papers for topic: ", topic)
            candidate_papers = self.arxiv_gateway.find_by_query(query=topic, sort_by=self.SORT_COLUMN)
            real_new_papers = [p for p in candidate_papers if p.abstract_url not in self.existing_papers_urls]
            print("Unique new papers found: ", len(real_new_papers), " for topic: ", topic)
            papers = papers + real_new_papers


        logging.info("Found ", len(papers), " new papers")

        if dry_run:
            return len(papers), 0

        total_registered, total_skipped = self._register_given_papers(papers)
        print("New papers ", total_registered, " papers")
        print("Skipped ", total_skipped, " papers")

    def register_by_id(self, id: str):
        """
        Register new paper by id
        """
        print("Registering paper in db by id: ", id)
        papers = self.arxiv_gateway.find_by_id([id])
        print("Found papers: ", str(papers))
        return self._register_given_papers(papers)

    def latest_date_with_papers(self) -> datetime.date:
        """
        Return the latest date with papers in arxiv with the Query AI
        So i assume it should always return something recent
        """
        if not has_internet():
            raise Exception("No internet connection found")

        query = "cat:Artificial Intelligence"

        result = self.arxiv_gateway.find_by_query(
            query=query, number_of_papers=10, sort_by=self.SORT_COLUMN
        )
        if not result:
            raise Exception(f"Did not find any paper with Query {query}")
        date_str = result[0].updated.date().isoformat()
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    def register_paper_if_not_registered(self, paper: ArxivPaper):
        if not paper.exists_in_db(paper.pdf_url):
            self.register_by_id(ArxivPaper.id_from_url(paper.pdf_url))
        else:
            print("Paper already registered")

    def query_papers(self, query):
        self._find_papers(
            query=query, number_of_papers=15, sort_by="relevance", only_print=True
        )

    def load_existing_papers_urls(self):
        arxiv_papers = self.tdw.event("arxiv_papers")
        if arxiv_papers.empty:
            return []
        return arxiv_papers["abstract_url"].values

    def _register_given_papers(self, papers: List[ArxivPaper]):
        counter = 0
        skipped = 0
        registered = 0
        self.existing_papers_urls = self.load_existing_papers_urls()

        registered_now = []
        for paper in tqdm(papers):
            counter = counter + 1
            if (
                paper.abstract_url in self.existing_papers_urls
                or paper.abstract_url in registered_now
            ):
                skipped += 1
                logging.info("Skipping already registered paper: ", paper.abstract_url)
                continue

            registered += 1
            self.tdw.write_event("arxiv_papers", paper.to_dict())
            registered_now.append(paper.abstract_url)

        print("Registered ", registered, " papers", "Skipped ", skipped, " papers")
        return registered, skipped



class ArxivGateway():
    def find_by_id(self, ids) -> List[ArxivPaper]:
        search = arxiv.Search(
            id_list=ids, max_results=len(ids)
        )

        return self._build_papers_from_results(search.results())

    def find_by_query(
        self,
        query=None,
        number_of_papers=None,
        sort_by: Literal["submitted", "relevance", 'updated'] = "submitted",
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
            query=query, max_results=number_of_papers, sort_by=sort, sort_order=arxiv.SortOrder.Descending
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

if __name__ == "__main__":
    import fire

    fire.Fire()
