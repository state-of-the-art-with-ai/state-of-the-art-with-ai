from typing import Optional
from state_of_the_art.config import config


class Paper:
    """
    Base paper abstration
    """

    def __init__(self, *, pdf_url: str, title: Optional[str] = None):
        self.pdf_url = pdf_url
        self.abstract_url = pdf_url
        self.title = title
        self.abstract = ""
        if not self.pdf_url.endswith(".pdf"):
            self.pdf_url += ".pdf"

    def exists_in_db(self, url):
        print(f"Checking if paper {url} exists in db")
        from state_of_the_art.paper.papers_data_loader import PapersLoader

        result = PapersLoader().load_from_url(url)
        if result.empty:
            return False
        return True

    def get_destination(self):
        file_name = self.get_filename()
        return f"{config.NEW_PAPERS_FOLDER}/{file_name}"

    def get_filename(self):
        return self.pdf_url.split("/")[-1]

    def published_date_str(self):
        return ""
