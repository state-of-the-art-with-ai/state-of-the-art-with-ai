from state_of_the_art.paper.paper import Paper

class PaperHumanPresenter:
    def __init__(self, url):
        self.paper = Paper.load_paper_from_url(url)

    @staticmethod
    def present_from_url(url):
        return PaperHumanPresenter(url).present()

    def present(self) -> str:
        return f"""\n{self.paper.title}
{self.paper.arxiv_url}
Published: {self.paper.published_date_str()}\n
Abstract: {self.paper.safe_abstract()}
        """
