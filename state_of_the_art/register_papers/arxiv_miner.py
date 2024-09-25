from typing import List
from state_of_the_art.config import config
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from tqdm import tqdm
import datetime
import logging

from state_of_the_art.register_papers.arxiv_gateway import ArxivGateway
from state_of_the_art.tables.mine_history import ArxivMiningHistory
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

    def mine_all_keywords(self, dry_run=False, keyword=None):
        """
        Register all papers by looking in arxiv api with the keyworkds of the audience configuration
        :param dry_run:
        :param disable_relevance_miner:
        :return:
        """
        if dry_run:
            print("Dry run, just printing, not registering them")
        keywords_to_mine = self.config.QUERIES_TO_MINE

        print(
            f"Registering papers for the following ({len(keywords_to_mine)}) keywords: ",
            keywords_to_mine,
        )

        total_new_papers_found = []
        for keyword in tqdm(keywords_to_mine):
            print("Mining papers for topic: ", keyword)
            candidate_papers = self.arxiv_gateway.find_by_query(
                query=keyword, sort_by=self.SORT_COLUMN
            )
            real_new_papers = [
                p
                for p in candidate_papers
                if p.abstract_url not in self.existing_papers_urls
            ]
            print(
                "Unique new papers found: ", len(real_new_papers), " for topic: ", keyword
            )
            total_new_papers_found = total_new_papers_found + real_new_papers

        logging.info("Found ", len(total_new_papers_found), " new papers")

        if dry_run:
            return len(total_new_papers_found), 0

        total_registered, total_skipped = self._register_given_papers(
            total_new_papers_found
        )
        ArxivMiningHistory().add(
            keywords=",".join(keywords_to_mine),
            total_new_papers_found=len(total_new_papers_found),
        )

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

        query = "cat:cs.AI"

        result = self.arxiv_gateway.find_by_query(
            query=query, number_of_papers=3, sort_by='submitted'
        )
        if not result:
            raise Exception(f"Did not find any paper with Query {query}")
        date_str = result[0].updated.date().isoformat()
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    
    def debug_latest_date_with_papers(self):
        if not has_internet():
            raise Exception("No internet connection found")

        query = "cat:cs.AI"

        query_result = self.arxiv_gateway.find_by_query(
            query=query, number_of_papers=3, sort_by='submitted'
        )
        dates = [(entry.abstract_url, entry.updated.date().isoformat()) for entry in query_result]
        result = {}
        result['submitted'] = dates
        query_result = self.arxiv_gateway.find_by_query(
            query=query, number_of_papers=3, sort_by='updated'
        )
        dates = [(entry.abstract_url, entry.updated.date().isoformat()) for entry in query_result]
        result['updated'] = dates

        import subprocess
        shell_cmd = """
curl "http://export.arxiv.org/api/query?search_query=all:Artificial+Intelligence&sortBy=submittedDate&sortOrder=descending" | grep -i published
        """
        p = subprocess.Popen(shell_cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, error  = p.communicate()
        print(out)
        print(error)

        return result

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


if __name__ == "__main__":
    import fire

    fire.Fire()
