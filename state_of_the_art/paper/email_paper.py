
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.downloader import PaperDownloader
from state_of_the_art.utils.mail import EmailService


class EmailAPaper:
    destination_emails = [
        'j34nc4rl0@gmail.com', 'machado.jean.kindle_new@kindle.com'
    ]
    def send(self, paper: ArxivPaper) -> bool:
        destination = PaperDownloader().download_from_arxiv(paper)

        for email in self.destination_emails:
            EmailService().send(content=None, subject=paper.title, attachment=destination, recepient=email)

        return True