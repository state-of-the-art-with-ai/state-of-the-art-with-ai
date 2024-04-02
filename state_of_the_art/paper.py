

class Paper():
    def __init__(self,*, arxiv_url):
        self._validate_arxiv_url(arxiv_url)
        self.arxiv_url = arxiv_url

    def _validate_arxiv_url(self, url):
        if not url.startswith("https://arxiv.org"):
            raise Exception(f'{url} not a valid arxiv url example')
        
        if url.endswith('.pdf'):
            raise Exception(f'paper url {url} should not end in .pdf')

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

