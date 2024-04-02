import arxiv
import os
from state_of_the_art.papers import PapersData
from tiny_data_wharehouse.data_wharehouse import DataWharehouse
from typing import Literal, Optional
from state_of_the_art.config import config


class ArxivLoader():
    def arxiv_search(self, *, query, max_results=10, short_version=True) -> str:
        summary = ''
        search = arxiv.Search(
        query=query,
        max_results = max_results,
        sort_by = arxiv.SortCriterion.SubmittedDate
        )

        summary = ""
        counter = 0
        for result in search.results():
            if short_version:
                summary += f"{counter} ({result.published}) {result.title} {result.entry_id}\n"
            else:
                summary += f"Title: {result.title}, Abstract: {result.summary}, URL: {result.entry_id}\n"
            counter += 1
        print("Found  ", counter, " articles")

        return summary


    def register_papers_by_topic(self, *, query='cs', number_of_papers=50, sort_by: Literal['submitted', 'relevance' ] = 'submitted'):
        """
        Loads papers from arxiv and store them into the tiny data wharehouse
        """
        print(f"Registering new papers with query '{query}' and sorting by '{sort_by}'")

        sort=  arxiv.SortCriterion.SubmittedDate if sort_by == 'submitted' else arxiv.SortCriterion.Relevance

        search = arxiv.Search(
        query=query,
        max_results = number_of_papers,
        sort_by = sort
        )

        tdw = DataWharehouse()

        arxiv_papers = tdw.event('arxiv_papers')
        existing_papers_urls = arxiv_papers['url'].values

        counter = 0
        skipped = 0
        registered = 0
        for r in search.results():
            counter = counter+1
            if r.entry_id in existing_papers_urls:
                skipped += 1
                continue

            registered+=1
            tdw.write_event('arxiv_papers', {'title': r.title, 'abstract': r.summary, 'url': r.entry_id, 'published': r.published})

        arxiv_papers = tdw.event('arxiv_papers')
        after_amount = len(arxiv_papers.index)
        return registered, skipped


    def download_papers(num_results=100):
        search = arxiv.Search(
        query='data science',
        max_results = num_results,
        sort_by = arxiv.SortCriterion.SubmittedDate
        )
        for r in search.results():
            print('Downloading: ', r.title, r.pdf_url)
            download_named_paper(r.pdf_url,r.title)

        open_papers_folder()
        

    def convert_title_to_filename(self, title) -> str:
        for c in title:
            if not c.isalnum():
                title = title.replace(c, '_')
        return title

    def download_named_paper(self, url: str, title: Optional[str] = None):
        destination = f'{config.PAPERS_FOLDER}/{convert_title_to_filename(title)}.pdf'
        import urllib
        urllib.request.urlretrieve(url, destination)

    def download_paper(self, url: str) -> str:
        file_name= url.split('/')[-1]
        destination = f'{config.NEW_PAPERS_FOLDER}/{file_name}'

        if os.path.exists(destination):
            print(f"File {destination} already exists")
            return destination


        print(f"Downloading file {url} to {destination}")

        import urllib
        urllib.request.urlretrieve(url, destination)
        return destination

    def open_papers_folder(self):
        os.system(f"open {config.PAPERS_FOLDER}/")

if __name__ == "__main__":
    import fire
    fire.Fire()


def register_papers():
    from state_of_the_art.config import Config
    topics = Config.load_config().get_current_profile().arxiv_topics
    loader = ArxivLoader()
    print("Registering papers for topics: ", topics)
    total_skipped = 0
    total_registered = 0
    for topic in topics:
        registered, skipped = loader.register_papers_by_topic(query=topic, sort_by='relevance')
        total_skipped += skipped
        total_registered += registered
        registered, skipped = loader.register_papers_by_topic(query=topic, sort_by='submitted')
        total_skipped += skipped
        total_registered += registered

    print("Registered ", total_registered, " papers")
    print("Skipped ", total_skipped, " papers")
