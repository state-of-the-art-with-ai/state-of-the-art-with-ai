from state_of_the_art.paper.arxiv_paper import ArxivPaper


def test_paper_url():
    given_abstract = "https://arxiv.org/abs/2202.13868"
    paper = ArxivPaper(abstract_url=given_abstract)

    assert paper.abstract_url == given_abstract
    assert paper.pdf_url == "https://arxiv.org/pdf/2202.13868.pdf"
