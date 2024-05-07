from state_of_the_art.paper.url_extractor import PapersUrlsExtractor


def test_no_url():
    data = """
    not an url
    """

    print(" test")
    assert [] == PapersUrlsExtractor().extract_urls(data)


def test_a_url():
    data = """
    http://foo.bar
    """

    assert ["http://foo.bar"] == PapersUrlsExtractor().extract_urls(data)
