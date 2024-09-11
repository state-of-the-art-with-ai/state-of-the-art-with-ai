from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.paper_entity import Paper
import os
from state_of_the_art.utils import pdf


class PaperDownloader:
    def download_from_arxiv(self, paper: ArxivPaper, force_download=False) -> str:
        return self.download(
            paper.pdf_url, given_title=paper.title, force_download=force_download
        )

    def open_from_arxiv(self, paper: ArxivPaper):
        self.open(paper.pdf_url, title=paper.title)

    def download(self, pdf_url: str, force_download=False, given_title=None) -> str:
        """
        Downloads a paper from a given url
        :param url:
        :return:
        """
        if not pdf_url.startswith("http"):
            print("Not an http url spkipping download")
            return pdf_url

        paper = Paper(pdf_url=pdf_url)
        print(f"Downloading paper from {paper.pdf_url}")
        destination = self._get_destination(pdf_url, title=given_title)

        if os.path.exists(destination):
            if "FORCE_DOWNLOAD" in os.environ or force_download:
                print("Force download is enabled so will download the file again")
                self.remove(destination)
            else:
                print(f"File {destination} already exists so wont download it again")
                return destination

        print(f"Downloading file {paper.pdf_url} to {destination}")

        import urllib

        opener = urllib.request.build_opener()
        opener.addheaders = [("User-agent", "Mozilla/5.0")]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(paper.pdf_url, destination)
        return destination

    def _get_destination(self, pdf_url, title=None):
        if title is None:
            title = pdf_url.split("/")[-1].replace(".pdf", "")
        return pdf.create_pdf_path("paper" + title, disable_timestamp=True)

    def remove(self, pdf_url):
        path = self._get_destination(pdf_url)
        if os.path.exists(path):
            os.remove(path)
            print(f"Removed file {path}")

    def open(self, pdf_url, title=None):
        path = self._get_destination(pdf_url, title=title)
        pdf.open_pdf(path)
        print(f"Opened file {path}")
