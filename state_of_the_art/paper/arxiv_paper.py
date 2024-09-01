from state_of_the_art.paper.paper_entity import Paper


from typing import List, Optional


class ArxivPaper(Paper):
    """
    Main dto to access papers functionality

    """

    abstract_url: Optional[str] = None
    pdf_url: Optional[str] = None

    def __init__(
        self,
        *,
        abstract_url: Optional[str] = None,
        published=None,
        title: Optional[str] = None,
        abstract: Optional[str] = None,
    ):
        """
        the only acceptable url is the abstract url, the others need to be converted ahead of time
        """
        self.abstract_url = abstract_url.strip()
        self.abstract_url.replace("http://", "https://")
        if not self.is_arxiv_url(self.abstract_url):
            raise Exception(f'"{self.abstract_url}" is not a valid arxiv url')

        self.abstract_url = ArxivPaper._remove_versions_from_url(self.abstract_url)

        self.pdf_url = self.convert_abstract_to_pdf(self.abstract_url)
        self.published = published
        self.title = title if title else ""
        self.abstract = abstract if abstract else ""

    @staticmethod
    def _remove_versions_from_url(url: Optional[str]):
        if not url:
            return url

        if url.endswith("v1"):
            return url[:-2]

        if url.endswith("v2"):
            return url[:-2]

        if url.endswith("v3"):
            return url[:-2]

        return url

    @staticmethod
    def load_from_dict(data):
        return ArxivPaper(
            abstract_url=data["abstract_url"],
            published=data["published"],
            title=data["title"],
            abstract=data["abstract"],
        )

    @staticmethod
    def id_from_url(url) -> str:
        return url.split("/")[-1].replace(".pdf", "")

    @staticmethod
    def load_paper_from_url(url: str) -> "ArxivPaper":
        from state_of_the_art.paper.papers_data_loader import PapersLoader

        result = PapersLoader().load_from_url(url)
        if result.empty:
            raise Exception(f'Paper not found for url "{url}"')

        result = result.iloc[0].to_dict()
        return ArxivPaper(
            abstract_url=result["abstract_url"],
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
            "pdf_url": self.pdf_url,
            "abstract_url": self.abstract_url,
            "published": self.published,
            "title": self.title,
            "abstract": self.abstract,
        }

    def __repr__(self):
        return f"""{self.to_dict()}"""

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
    def is_arxiv_url(url: str):
        return url.startswith("http://arxiv.org") or url.startswith("https://arxiv.org")

    @staticmethod
    def convert_pdf_to_abstract(url):
        url = url.replace(".pdf", "")
        url = url.replace("pdf", "abs")
        url = url.replace("http://", "https://")
        return url
