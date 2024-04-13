from state_of_the_art.paper.paper import Paper

class PaperHumanPresenter:
    def __init__(self, url):
        self.paper = Paper.load_url_from_db(url)

    @staticmethod
    def present_from_url(url):
        return PaperHumanPresenter(url).present()

    def present(self) -> str:
        return f"""Title: {self.paper.title}
Published: {self.paper.published_date_str()}
Abstract: {self.paper.abstract}
URL: {self.paper.arxiv_url}
        """
