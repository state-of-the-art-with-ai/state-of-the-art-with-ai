import arxiv
from tiny_data_wharehouse.data_wharehouse import DataWharehouse
from typing import Literal
from state_of_the_art.config import config
from state_of_the_art.paper import Paper
class ArxivPaperMiner():
    """
    Looks at arxiv api for papers
    """

    DEFAULT_QUERY = 'cs.AI'

    def register_papers(self, dry_run=False, disable_relevance_miner=False):
        """
        Register papers by looking in arxiv api with the keyworkds of the audience configuration
        :param dry_run:
        :param disable_relevance_miner:
        :return:
        """
        if dry_run:
            print("Dry run, just printing, not registering them")

        topics = config.get_current_audience().keywords
        print("Registering papers for the following keywords: ", topics)
        total_skipped = 0
        total_registered = 0

        for topic in topics:
            if not disable_relevance_miner:
                registered, skipped = self.register_papers_by_topic(query=topic, sort_by='relevance', dry_run=dry_run)
                total_skipped += skipped
                total_registered += registered
            registered, skipped = self.register_papers_by_topic(query=topic, sort_by='submitted', dry_run=dry_run)
            total_skipped += skipped
            total_registered += registered

        print("New papers ", total_registered, " papers")
        print("Skipped ", total_skipped, " papers")


    def register_papers_by_topic(self, *, query=None, number_of_papers=None, sort_by: Literal['submitted', 'relevance' ] = 'submitted', dry_run=False):
        """
        Loads papers from arxiv and store them into the tiny data wharehouse
        """
        print(f"Registering new papers with query '{query}' and sorting by '{sort_by}'")

        papers = self._find_papers(query=query, number_of_papers=number_of_papers, sort_by=sort_by)

        if dry_run:
            return len(papers), 0
        return self._register_given_papers(papers)

    def query_papers(self, query):
        self._find_papers(query, number_of_papers=15, sort_by='relevance', only_print=True)
    def _find_papers(self, query=None, number_of_papers=None, sort_by: Literal['submitted', 'relevance'] = 'submitted', only_print=False):
        if not query:
            print("No query provided, using default query")
            query = self.DEFAULT_QUERY

        if not number_of_papers:
            number_of_papers = self.config.MAX_PAPERS_TO_MINE_PER_QUERY

        sort = arxiv.SortCriterion.SubmittedDate if sort_by == 'submitted' else arxiv.SortCriterion.Relevance

        print({'query': query, 'sort_by': sort_by})
        search = arxiv.Search(
            query=query,
            max_results = number_of_papers,
            sort_by = sort
        )

        result = []
        order_counter = 1
        for r in search.results():
            paper = Paper(title=r.title, abstract=r.summary, arxiv_url=r.entry_id, published=r.published)
            result.append(paper)
            print(order_counter, paper.published, paper.title, paper.url)

            order_counter += 1

        if only_print:
            return
        return result

    def find_latest_papers(self, *, query=None):
        """"
        Check with papers are latest submitted in arxiv, useful to undertand if we need to register more
        """
        self._find_papers(query=query, number_of_papers=30, sort_by='submitted', only_print=True)

    def _register_given_papers(self, papers):
        tdw = DataWharehouse()

        arxiv_papers = tdw.event('arxiv_papers')
        existing_papers_urls = arxiv_papers['url'].values

        counter = 0
        skipped = 0
        registered = 0
        for paper in papers:
            counter = counter+1
            if paper.url in existing_papers_urls:
                skipped += 1
                continue

            registered+=1
            tdw.write_event('arxiv_papers', paper.to_dict())

        return registered, skipped


if __name__ == "__main__":
    import fire
    fire.Fire()

