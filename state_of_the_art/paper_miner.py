import arxiv
import os
from tiny_data_wharehouse.data_wharehouse import DataWharehouse
from typing import Literal, Optional
from state_of_the_art.config import config
from state_of_the_art.paper import Paper
class ArxivMiner():
    """
    Looks at arxiv api for papers
    """

    DEFAULT_MAX_PAPERS_TO_LOAD=10

    def register_papers(self, dry_run=False):
        from state_of_the_art.config import Config
        topics = Config.load_config().get_current_profile().keyworkds
        loader = ArxivMiner()
        print("Registering papers for topics: ", topics)
        total_skipped = 0
        total_registered = 0
        for topic in topics:
            registered, skipped = loader.register_papers_by_topic(query=topic, sort_by='relevance', dry_run=dry_run)
            total_skipped += skipped
            total_registered += registered
            registered, skipped = loader.register_papers_by_topic(query=topic, sort_by='submitted', dry_run=dry_run)
            total_skipped += skipped
            total_registered += registered

        print("Registered ", total_registered, " papers")
        print("Skipped ", total_skipped, " papers")

    def load_papers(self, *, query='cs', number_of_papers=None, sort_by: Literal['submitted', 'relevance' ] = 'submitted'):

        sort = arxiv.SortCriterion.SubmittedDate if sort_by == 'submitted' else arxiv.SortCriterion.Relevance

        search = arxiv.Search(
            query=query,
            max_results = number_of_papers,
            sort_by = sort
        )

        result = []
        for r in search.results():
            paper = Paper(title=r.title, abstract=r.summary, arxiv_url=r.entry_id, published=r.published)
            result.append(paper)
        return result

    def register_papers_by_topic(self, *, query='cs', number_of_papers=None, sort_by: Literal['submitted', 'relevance' ] = 'submitted', dry_run=False):
        """
        Loads papers from arxiv and store them into the tiny data wharehouse
        """
        print(f"Registering new papers with query '{query}' and sorting by '{sort_by}'")

        if not number_of_papers:
            number_of_papers = self.DEFAULT_MAX_PAPERS_TO_LOAD

        papers = self.load_papers(query=query, number_of_papers=number_of_papers, sort_by=sort_by)
        if dry_run:
            print("Dry run, just printing the papers")
            print(" =========== For query ", query, " and sorting by ", sort_by, " found ", len(papers), " papers =========== ")
            for i in papers:
                print(i.published, i.title, i.url)

            return len(papers), 0


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

    def convert_title_to_filename(self, title) -> str:
        for c in title:
            if not c.isalnum():
                title = title.replace(c, '_')
        return title

    def download_named_paper(self, url: str, title: Optional[str] = None):
        destination = f'{config.PAPERS_FOLDER}/{self.convert_title_to_filename(title)}.pdf'
        import urllib
        urllib.request.urlretrieve(url, destination)

    def download_paper(self, url: str) -> str:
        """
        Downloads a paper from a given url
        :param url:
        :return:
        """
        if not url.endswith('.pdf'):
            pdf_url = Paper.convert_abstract_to_pdf(url)

        if not pdf_url.endswith('.pdf'):
            raise Exception("Invalid file format. Only PDF files are supported")

        destination = self.get_destination(pdf_url)

        if os.path.exists(destination):
            print(f"File {destination} already exists")
            return destination

        print(f"Downloading file {pdf_url} to {destination}")

        import urllib
        urllib.request.urlretrieve(pdf_url, destination)
        return destination
        
    def get_destination(self, url):
        if not url.endswith('.pdf'):
                url = Paper.convert_abstract_to_pdf(url)

        file_name= url.split('/')[-1]
        return f'{config.NEW_PAPERS_FOLDER}/{file_name}'


    def download_and_open(self, url):
        destination = self.download_paper(url)
        self.open_paper(url)

    def open_paper(self, url):
        os.system(f"open {self.get_destination(url)}")

if __name__ == "__main__":
    import fire
    fire.Fire()

