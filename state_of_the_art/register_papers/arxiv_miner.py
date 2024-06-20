import arxiv
from typing import Literal, List
from state_of_the_art.config import config
from state_of_the_art.paper.paper import ArxivPaper
from tqdm import tqdm
import datetime 
import logging


class ArxivMiner:
    """
    Looks at arxiv api for papers
    """

    DEFAULT_QUERY = "cs.AI"
    max_papers_per_query = None

    def __init__(self):
        self.config = config
        tdw = config.get_datawarehouse()
        arxiv_papers = tdw.event("arxiv_papers")
        self.existing_papers_urls = (
            arxiv_papers["url"].values if not arxiv_papers.empty else []
        )
        self.tdw = config.get_datawarehouse()
        self.existing_papers_urls = self.load_existing_papers_urls()

    def register_latest(self, dry_run=False, max_papers_per_query=None, topic=None):
        """
        Register papers by looking in arxiv api with the keyworkds of the audience configuration
        :param dry_run:
        :param disable_relevance_miner:
        :return:
        """
        self.max_papers_per_query = max_papers_per_query
        if dry_run:
            print("Dry run, just printing, not registering them")

        if topic:
            topics_to_mine = self._get_topic_keywords(topic)
        else:
            topics_to_mine = self._get_topics_to_mine()

        print(
            f"Registering papers for the following ({len(topics_to_mine)}) keywords: ",
            topics_to_mine,
        )

        papers = []

        for topic in tqdm(topics_to_mine):
            papers = papers + self._find_papers(query=topic, sort_by="submitted")

        papers = [p for p in papers if p.abstract_url not in self.existing_papers_urls]
        logging.info("Found ", len(papers), " new papers")

        if dry_run:
            return len(papers), 0

        total_registered, total_skipped = self._register_given_papers(papers)
        print("New papers ", total_registered, " papers")
        print("Skipped ", total_skipped, " papers")

    def register_by_relevance(
        self, dry_run=False, max_papers_per_query=None, topic_name=None
    ):
        """
        Register papers by looking in arxiv api with the keyworkds of the audience configuration
        :param dry_run:
        :param disable_relevance_miner:
        :return:
        """
        self.max_papers_per_query = max_papers_per_query
        if dry_run:
            print("Dry run, just printing, not registering them")

        if topic_name:
            topics_to_mine = self._get_topic_keywords(topic_name)
        else:
            topics_to_mine = self._get_topics_to_mine()

        print(
            f"Registering papers for the following ({len(topics_to_mine)}) keywords: ",
            topics_to_mine,
        )

        papers = []
        for topic_name in topics_to_mine:
            papers = papers + self._find_papers(query=topic_name, sort_by="relevance")

        papers = [p for p in papers if p.abstract_url not in self.existing_papers_urls]
        print("Found ", len(papers), " new papers")

        if dry_run:
            return len(papers), 0

        total_registered, total_skipped = self._register_given_papers(papers)
        print("New papers ", total_registered, " papers")
        print("Skipped ", total_skipped, " papers")

    def register_latest_by_query(self, query):
        papers = self._find_papers(query=query, number_of_papers=10)
        print("Found ", len(papers), " new papers")

        total_registered, total_skipped = self._register_given_papers(papers)
        print("New papers ", total_registered, " papers")
        print("Skipped ", total_skipped, " papers")

    def _get_topic_keywords(self, filter_topic_name: str) -> List[str]:
        audience_topics = config.get_current_audience().get_topics()
        if filter_topic_name in audience_topics:
            return audience_topics[filter_topic_name].get_arxiv_search_keywords()
        return []

    def _get_topics_to_mine(self) -> List[str]:
        audience_keywords = config.get_current_audience().keywords
        topics_to_mine = audience_keywords
        audience_topics = config.get_current_audience().get_topics().values()
        for topic in audience_topics:
            topics_to_mine = topics_to_mine + topic.get_arxiv_search_keywords()

        return topics_to_mine

    def find_latest_published_date(self):
        result = self.find_latest_by_query("AI")
        date_str = result[0].published_date_str()
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

    def find_latest_by_query(self, query=None, n=10):
        """ "
        Check with papers are latest submitted in arxiv, useful to undertand if we need to register more
        """
        return self._find_papers(query=query, number_of_papers=n, sort_by="submitted")

    def register_paper_if_not_registered(self, paper: ArxivPaper):
        if not paper.exists_in_db(paper.pdf_url):
            self.register_by_id(ArxivPaper.id_from_url(paper.pdf_url))
        else:
            print("Paper already registered")

    def register_by_id(self, id: str):
        print("Registering paper in db by id: ", id)
        papers = self._find_papers(id_list=[str(id)], only_print=False)
        print("Found papers: ", str(papers))
        return self._register_given_papers(papers)

    def query_papers(self, query):
        self._find_papers(
            query, number_of_papers=15, sort_by="relevance", only_print=True
        )

    def _find_papers(
        self,
        id_list=None,
        query=None,
        number_of_papers=None,
        sort_by: Literal["submitted", "relevance"] = "submitted",
        only_print=False,
    ) -> List[ArxivPaper]:
        if not query and not id_list:
            print("No query provided, using default query")
            query = self.DEFAULT_QUERY

        if not number_of_papers:
            number_of_papers = (
                self.max_papers_per_query
                if self.max_papers_per_query
                else self.config.papers_to_mine_per_query()
            )

        sort = (
            arxiv.SortCriterion.SubmittedDate
            if sort_by == "submitted"
            else arxiv.SortCriterion.Relevance
        )

        logging.info(
            "Arxiv query parameters:",
            "".join(
                {
                    "query": query,
                    "sort_by": sort_by,
                    "id_list": id_list,
                    "number_of_papers": number_of_papers,
                }
            ),
        )

        if id_list:
            print("Searching by id list: ", id_list)
            search = arxiv.Search(
                id_list=id_list, max_results=number_of_papers, sort_by=sort
            )
        else:
            search = arxiv.Search(
                query=query, max_results=number_of_papers, sort_by=sort
            )

        result = []
        order_counter = 1
        for r in search.results():
            paper = ArxivPaper(
                title=r.title,
                abstract=r.summary,
                pdf_url=r.entry_id,
                published=r.published,
            )
            result.append(paper)
            logging.info(
                order_counter, paper.published, paper.title, paper.abstract_url
            )
            order_counter += 1
        logging.info("Found ", len(result), " papers")

        if only_print:
            return
        return result

    def load_existing_papers_urls(self):
        arxiv_papers = self.tdw.event("arxiv_papers")
        if arxiv_papers.empty:
            return []
        return arxiv_papers["url"].values

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


if __name__ == "__main__":
    import fire

    fire.Fire()
