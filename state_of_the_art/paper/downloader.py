from state_of_the_art.paper.paper import Paper
import os
from state_of_the_art.utils import pdf


class Downloader:

    def download(self, pdf_url:str, force_download=False, title=None):
        """
        Downloads a paper from a given url
        :param url:
        :return:
        """
        paper = Paper(pdf_url=pdf_url)
        destination = self._get_destination(pdf_url, title=title)


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
        os.remove(path)
        print(f"Removed file {path}")

    def open(self, pdf_url):
        path = self._get_destination(pdf_url)
        pdf.open_pdf(path)
        print(f"Opened file {path}")
