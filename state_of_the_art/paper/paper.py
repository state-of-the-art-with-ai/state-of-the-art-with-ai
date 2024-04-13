
import os
from typing import List
from state_of_the_art.config import config


class Paper():
    """
    Main dto to acceess papers functionality

    """
    def __init__(self,*, arxiv_url, published=None, title=None, abstract=None):
        self.validate_abstract_url(arxiv_url)
        self.arxiv_url = arxiv_url

        self.url = arxiv_url
        self.published = published
        self.title = title
        self.abstract = abstract


    @staticmethod
    def load_paper_from_url(url) -> 'Paper':
        from state_of_the_art.paper.papers_data import PapersData
        result = PapersData().load_from_url(url)
        if result is None:
            raise Exception(f"Paper with url {url} not found")
        result = result.iloc[0].to_dict()
        return Paper(arxiv_url=result['url'], published=result['published'], title=result['title'], abstract=result['abstract'])

    def load_papers_from_urls(urls) -> List['Paper']:
        result = []
        for url in urls:
            result.append(Paper.load_paper_from_url(url))
        return result

    def to_dict(self):
        return {
            'url': self.arxiv_url,
            'published': self.published,
            'title': self.title,
            'abstract': self.abstract
        }


    def safe_abstract(self):
         return ''.join(c for c in self.abstract if c.isalnum() or c in [' ', '\n', '.', ','])

    def published_date_str(self) -> str:
        return str(self.published)[0:10]

    @staticmethod
    def validate_abstract_url(url):
        if url.startswith("https://arxiv.org"):
            raise Exception(f'The url via arxiv api is usually http we got: "{url}"')
        if url.endswith(".pdf"):
            raise Exception(f'This url is meant to be the abstract url, not the pdf url: "{url}"')
        if not url.startswith("http://arxiv.org"):
            raise Exception(f'"{url}" not a valid arxiv url example')

    @staticmethod
    def is_abstract_url(url):
        if (url.startswith("https://arxiv.org") or url.startswith("http://arxiv.org")) and 'abs' in url:
            return True
        return False

    @staticmethod
    def convert_abstract_to_pdf(url):
        result = url.replace('abs', 'pdf')

        result += '.pdf'
        return result

    def download(self) -> str:
        """
        Downloads a paper from a given url
        :param url:
        :return:
        """
        pdf_url = self.url
        if not self.url.endswith('.pdf'):
            pdf_url = Paper.convert_abstract_to_pdf(self.url)

        if not pdf_url.endswith('.pdf'):
            raise Exception("Invalid file format. Only PDF files are supported")

        destination = self.get_destination(pdf_url)

        if os.path.exists(destination):
            print(f"File {destination} already exists so wont download it again")
            return destination

        print(f"Downloading file {pdf_url} to {destination}")

        import urllib
        urllib.request.urlretrieve(pdf_url, destination)
        return destination

    def get_destination(self, url):
        if not url.endswith('.pdf'):
            url = Paper.convert_abstract_to_pdf(url)

        file_name = url.split('/')[-1]
        return f'{config.NEW_PAPERS_FOLDER}/{file_name}'

    def download_and_open(self):
        self.download()
        self.open()

    def open(self):
        """
        Opens the paper in the default pdf reader of the desktop

        :return:
        """
        os.system(f"open {self.get_destination(self.url)}")


