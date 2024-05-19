from typing import List, Optional
from state_of_the_art.config import config


class Paper:
    def __init__(self, *, pdf_url: str):
        self.pdf_url = pdf_url
        if not self.pdf_url.endswith(".pdf"):
            self.pdf_url += ".pdf"

    def exists_in_db(self, url):
        print(f"Checking if paper {url} exists in db")
        from state_of_the_art.paper.papers_data import PapersDataLoader

        result = PapersDataLoader().load_from_url(url)
        if result.empty:
            return False
        return True

    def get_destination(self):
        file_name = self.get_filename()
        return f"{config.NEW_PAPERS_FOLDER}/{file_name}"

    def get_filename(self):
        return self.pdf_url.split("/")[-1]


class ArxivPaper(Paper):
    """
    Main dto to access papers functionality

    """

    def __init__(
        self,
        *,
        url: Optional[str] = None,
        pdf_url: Optional[str] = None,
        published=None,
        title: Optional[str] = None,
        abstract: Optional[str] = None,
    ):
        if url and not self.is_arxiv_url(url):
            raise Exception(f'"{url}" is not a valid arxiv url')
        if pdf_url and not self.is_arxiv_url(pdf_url):
            raise Exception(f'"{url}" is not a valid arxiv url')

        if pdf_url and not url:
            self.abstract_url = self.convert_pdf_to_abstract(pdf_url)
            self.pdf_url = pdf_url.replace("http://", "https://")

        if url and not pdf_url:
            self.pdf_url = self.convert_abstract_to_pdf(url)
            self.abstract_url = self.convert_pdf_to_abstract(url)

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
        result = result.iloc[0].to_dict()
        return ArxivPaper(
            url=result["url"],
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
            "url": self.pdf_url,
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
        result = result.replace("http://", "https://")
        result += ".pdf"
        return result

    @staticmethod
    def is_arxiv_url(url):
        return url.startswith("http://arxiv.org") or url.startswith("https://arxiv.org")

    @staticmethod
    def convert_pdf_to_abstract(url):
        url = url.replace(".pdf", "")
        url = url.replace("pdf", "abs")
        url = url.replace("http://", "https://")
        return url
