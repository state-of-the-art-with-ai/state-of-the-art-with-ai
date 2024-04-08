
import os
from state_of_the_art.config import config
class Paper():
    def __init__(self,*, arxiv_url, published=None, title=None, abstract=None):
        self._validate_arxiv_url(arxiv_url)
        self.arxiv_url = arxiv_url

        self.url = arxiv_url
        self.published = published
        self.title = title
        self.abstract = abstract


    def to_dict(self):
        return {
            'url': self.arxiv_url,
            'published': self.published,
            'title': self.title,
            'abstract': self.abstract
        }


    def _validate_arxiv_url(self, url):
        if not url.startswith("https://arxiv.org") and not url.startswith("http://arxiv.org") :
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
        if not self.url.endswith('.pdf'):
            pdf_url = Paper.convert_abstract_to_pdf(self.url)

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

        file_name = url.split('/')[-1]
        return f'{config.NEW_PAPERS_FOLDER}/{file_name}'

    def download_and_open(self):
        self.download_paper()
        self.open_paper()

    def open(self):
        """
        Opens the paper in the default pdf reader of the desktop

        :return:
        """
        os.system(f"open {self.get_destination(self.url)}")
