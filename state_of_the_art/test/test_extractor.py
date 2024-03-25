from state_of_the_art.papers import PapersComparer


def test_no_url():
    data = """
    not an url
    """

    print(' test')
    assert [] == PapersComparer().extract_papers_urls(data)

def test_a_url():
    data = """
    http://foo.bar
    """

    assert ["http://foo.bar"] == PapersComparer().extract_papers_urls(data)