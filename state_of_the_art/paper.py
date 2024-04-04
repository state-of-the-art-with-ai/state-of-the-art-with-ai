

class Paper():
    def __init__(self,*, arxiv_url, published=None, title=None, abstract=None):
        self._validate_arxiv_url(arxiv_url)
        self.arxiv_url = arxiv_url

        self.published = published
        self.title = title
        self.abstract = abstract

    def _validate_arxiv_url(self, url):
        if not url.startswith("https://arxiv.org") and not url.startswith("http://arxiv.org") :
            raise Exception(f'"{url}" not a valid arxiv url example')

    @staticmethod
    def is_abstract_url(url):
        if (url.startswith("https://arxiv.org") or url.startswith("http://arxiv.org")) and 'abs' in url:
            return True
        return False

    @staticmethod
    def convert_abstract_to_pdf(url):
        result = url.replace('abs', 'pdf')

        result += '.pdf'
        return result

