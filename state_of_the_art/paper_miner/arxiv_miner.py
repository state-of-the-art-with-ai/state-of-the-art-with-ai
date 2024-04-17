import arxiv
from typing import Literal, List
from state_of_the_art.config import config
from state_of_the_art.paper.paper import Paper
class PaperMiner():
    """
    Looks at arxiv api for papers
    """

    DEFAULT_QUERY = 'cs.AI'

    def __init__(self):
        self.config = config
        tdw = config.get_datawharehouse()
        arxiv_papers = tdw.event('arxiv_papers')
        self.existing_papers_urls = arxiv_papers['url'].values
        self.tdw = config.get_datawharehouse()
        self.existing_papers_urls = self.load_existing_papers_urls()

    def register_new(self, dry_run=False, disable_relevance_miner=False):
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

        papers = []
        for topic in topics:
            papers = papers + self._find_papers(query=topic, sort_by='relevance')
            papers = papers + self._find_papers(query=topic, sort_by='submitted')

        print("Found ", len(papers), " papers")
        papers = [p for p in papers if p.url not in self.existing_papers_urls]
        print("Found ", len(papers), " new papers")

        if dry_run:
            return len(papers), 0

        total_registered, total_skipped = self._register_given_papers(papers)
        print("New papers ", total_registered, " papers")
        print("Skipped ", total_skipped, " papers")

    def inspect_latest(self, *, query=None, n=10):
        """"
        Check with papers are latest submitted in arxiv, useful to undertand if we need to register more
        """
        self._find_papers(query=query, number_of_papers=n, sort_by='submitted', only_print=True)

    def register_by_id(self, id):
        papers = self._find_papers(id_list=[str(id)], only_print=False)
        return self._register_given_papers(papers)

    def query_papers(self, query):
        self._find_papers(query, number_of_papers=15, sort_by='relevance', only_print=True)
    def _find_papers(self, id_list=None, query=None, number_of_papers=None, sort_by: Literal['submitted', 'relevance'] = 'submitted', only_print=False)->List[Paper]:
        if not query and not id_list:
            print("No query provided, using default query")
            query = self.DEFAULT_QUERY

        if not number_of_papers:
            number_of_papers = self.config.MAX_PAPERS_TO_MINE_PER_QUERY

        sort = arxiv.SortCriterion.SubmittedDate if sort_by == 'submitted' else arxiv.SortCriterion.Relevance

        print({'query': query, 'sort_by': sort_by, 'id_list': id_list, 'number_of_papers': number_of_papers})

        if id_list:
            print("Searching by id list: ", id_list)
            search = arxiv.Search(
                id_list=id_list,
                max_results = number_of_papers,
                sort_by = sort
            )
        else:
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
        print("Found ", len(result), " papers")

        if only_print:
            return
        return result

    def load_existing_papers_urls(self):
        arxiv_papers = self.tdw.event('arxiv_papers')
        return arxiv_papers['url'].values


    def _register_given_papers(self, papers: List[Paper]):
        counter = 0
        skipped = 0
        registered = 0
        self.existing_papers_urls = self.load_existing_papers_urls()
        for paper in papers:
            counter = counter+1
            if paper.url in self.existing_papers_urls:
                skipped += 1
                continue

            registered+=1
            self.tdw.write_event('arxiv_papers', paper.to_dict())

        print("Registered ", registered, " papers", "Skipped ", skipped, " papers")
        return registered, skipped


if __name__ == "__main__":
    import fire
    fire.Fire()

