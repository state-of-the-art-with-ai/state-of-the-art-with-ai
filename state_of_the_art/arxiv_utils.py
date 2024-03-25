import arxiv
import os
from tiny_data_wharehouse.data_wharehouse import DataWharehouse
import pandas as pd
from typing import Literal

def arxiv_search(*, query, max_results=10, short_version=True) -> str:
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


def register_new_papers(*, query='cs', number_of_papers=50, sort_by: Literal['submitted', 'relevance' ] = 'submitted'):
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
    before_amount = len(arxiv_papers.index)
    print("Exising papers: ", before_amount)
    existing_papers_urls = arxiv_papers['url'].values

    counter = 0
    for r in search.results():
        counter = counter+1
        if r.entry_id in existing_papers_urls:
            print(f'Skipping paper {r.title} already registered')
            continue

        print(f'Registering paper {r.title}, {r.published}')
        tdw.write_event('arxiv_papers', {'title': r.title, 'abstract': r.summary, 'url': r.entry_id, 'published': r.published})

    print('Done')

    arxiv_papers = tdw.event('arxiv_papers')
    after_amount = len(arxiv_papers.index)
    print(f"{after_amount - before_amount} new papers registered")

def load_papers_between_published_dates(start, end) -> pd.DataFrame:
    tdw = DataWharehouse()
    df = tdw.event('arxiv_papers')
    return df[(df['published'].dt.strftime('%Y-%m-%d') >= start) & (df['published'].dt.strftime('%Y-%m-%d') <= end)]

def download_papers(num_results=100):
    search = arxiv.Search(
      query='data science',
      max_results = num_results,
      sort_by = arxiv.SortCriterion.SubmittedDate
    )
    for r in search.results():
        print('Downloading: ', r.title, r.pdf_url)
        download_paper(r.title, r.pdf_url)

    open_papers_folder()
    

HOME = os.path.expanduser("~")
PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers"

def convert_title_to_filename(title) -> str:
    for c in title:
        if not c.isalnum():
            title = title.replace(c, '_')
    return title

def download_paper(title, url):
    destination = f'{PAPERS_FOLDER}/{convert_title_to_filename(title)}.pdf'
    import urllib
    urllib.request.urlretrieve(url, destination)

def open_papers_folder():
    os.system(f"open {PAPERS_FOLDER}/")

if __name__ == "__main__":
    import fire
    fire.Fire()
