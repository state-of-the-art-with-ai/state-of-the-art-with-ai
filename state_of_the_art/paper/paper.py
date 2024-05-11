import os
from typing import List
from state_of_the_art.config import config


class PaperDTO:

    def __init__(self, *, pdf_url: str):
        self.pdf_url = pdf_url
        if not self.pdf_url.endswith(".pdf"):
            self.pdf_url += ".pdf"

    def download(self) -> str:
        """
        Downloads a paper from a given url
        :param url:
        :return:
        """

        if not self.pdf_url.endswith(".pdf"):
            raise Exception("Invalid file format. Only PDF files are supported")

        destination = self.get_destination()

        if os.path.exists(destination):
            print(f"File {destination} already exists so wont download it again")
            return destination

        print(f"Downloading file {self.pdf_url} to {destination}")

        import urllib

        opener = urllib.request.build_opener()
        opener.addheaders = [("User-agent", "Mozilla/5.0")]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(self.pdf_url, destination)
        return destination

    def exists_in_db(self, url):
        print(f"Checking if paper {url} exists in db")
        from state_of_the_art.paper.papers_data import PapersDataLoader

        result = PapersDataLoader().load_from_url(url)
        if not result:
            return False
        return True

    def get_destination(self):
        file_name = self.get_filename()
        return f"{config.NEW_PAPERS_FOLDER}/{file_name}"

    def get_filename(self):
        return self.pdf_url.split("/")[-1]


class ArxivPaper(PaperDTO):
    """
    Main dto to access papers functionality

    """

    def __init__(self, *, pdf_url: str, published=None, title=None, abstract=None):
        self.validate_abstract_url(pdf_url)

        self.arxiv_url = pdf_url

        self.url = pdf_url
        self.pdf_url = None
        self.published = published
        self.title = title
        self.abstract = abstract

    @staticmethod
    def load_from_dict(data):
        return ArxivPaper(
            pdf_url=data["url"],
            published=data["published"],
            title=data["title"],
            abstract=data["abstract"],
        )

    @staticmethod
    def id_from_url(url):
        return url.split("/")[-1].replace(".pdf", "")

    @staticmethod
    def load_paper_from_url(url) -> "ArxivPaper":

        from state_of_the_art.paper.papers_data import PapersDataLoader

        result = PapersDataLoader().load_from_url(url)

        if result.empty:
            raise Exception(f"Paper not found for url {url}")

        result = PapersDataLoader().load_from_url(url)
        result = result.iloc[0].to_dict()
        return ArxivPaper(
            pdf_url=result["url"],
            published=result["published"],
            title=result["title"],
            abstract=result["abstract"],
        )

    def load_papers_from_urls(urls) -> List["ArxivPaper"]:
        result = []
        for url in urls:
            result.append(ArxivPaper.load_paper_from_url(url))
        return result

    def to_dict(self):
        return {
            "url": self.arxiv_url,
            "published": self.published,
            "title": self.title,
            "abstract": self.abstract,
        }

    def __str__(self):
        return f"""Title: {self.title}\n
Published: {self.published_date_str()}
Url: {self.url}\n"""

    def safe_abstract(self):
        return "".join(
            c for c in self.abstract if c.isalnum() or c in [" ", "\n", ".", ","]
        )

    def published_date_str(self) -> str:
        return str(self.published)[0:10]

    @staticmethod
    def validate_abstract_url(url):
        if url.endswith(".pdf"):
            raise Exception(
                f'This url is meant to be the abstract url, not the pdf url: "{url}"'
            )
        if not url.startswith("http://arxiv.org"):
            raise Exception(f'"{url}" not a valid arxiv url example')

    @staticmethod
    def is_valid_abstract_url(url) -> bool:
        try:
            ArxivPaper.validate_abstract_url(url)
            return True
        except Exception as e:
            print(f"Error validating url {url}: {e}")
            return False

    @staticmethod
    def is_abstract_url(url):
        if (
            url.startswith("https://arxiv.org") or url.startswith("http://arxiv.org")
        ) and "abs" in url:
            return True
        return False

    @staticmethod
    def convert_abstract_to_pdf(url):
        result = url.replace("abs", "pdf")

        result += ".pdf"
        return result

    @staticmethod
    def is_arxiv_url(url):
        return url.startswith("http://arxiv.org") or url.startswith("https://arxiv.org")

    @staticmethod
    def convert_pdf_to_abstract(url):
        url = url.replace(".pdf", "")
        url = url.replace("pdf", "abs")
        url = url.replace("https://", "http://")
        return url

    def get_title_filename(self):
        # remove non alphanumeric characters
        file_name = "".join(e for e in self.title if e.isalnum() or e in [" ", "_"])
        file_name = file_name.replace(" ", "_")
        return file_name + ".pdf"

    def download_and_open(self):
        self.download()
        self.open()

    def open(self):
        """
        Opens the paper in the default pdf reader of the desktop

        :return:
        """
        os.system(f"open {self.get_destination(self.url)}")
