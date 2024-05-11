from state_of_the_art.paper.paper import Paper
import os

class Downloader:

    def download(self, pdf_url):
        """
        Downloads a paper from a given url
        :param url:
        :return:
        """
        paper = Paper(pdf_url=pdf_url)

        if not paper.pdf_url.endswith(".pdf"):
            raise Exception("Invalid file format. Only PDF files are supported")

        destination = paper.get_destination()



        if os.path.exists(destination):
            if 'FORCE_DOWNLOAD' in os.environ:
                print('Force download is enabled so will download the file again')
                os.remove(destination)
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
