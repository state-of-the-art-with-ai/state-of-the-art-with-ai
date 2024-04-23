from state_of_the_art.papers import PapersExtractor


def test_no_url():
    data = """
    not an url
    """

    print(' test')
    assert [] == PapersExtractor().extract_urls(data)

def test_a_url():
    data = """
    http://foo.bar
    """

    assert ["http://foo.bar"] == PapersExtractor().extract_urls(data)