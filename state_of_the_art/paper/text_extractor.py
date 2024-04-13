from typing import List


class PapersExtractor():
    def extract_urls(self, data: str) -> List[str]:
        if not type(data)==str:
            raise Exception("Data to extract papers must be a string")

        urls = []
        for row in data.split('\n'):
            for k, _  in enumerate(row):
                if row[k] == 'h' and row[k + 1] == 't' and row[k + 2] == 't' and row[k + 3] == 'p':

                    url_char = row[k]
                    url = ''
                    internal_k = k
                    while url_char != ' ' and url_char != '\n' and internal_k<len(row):
                        url_char = row[internal_k]
                        url += url_char
                        internal_k = internal_k+1

                    urls.append(url)

                    continue
        return urls

    def overlap_size(self, papers_a, papers_b):
        overlap_size = 0
        for paper in papers_a:
            if paper in papers_b:
                overlap_size = overlap_size + 1

        total = len(papers_a) + len(papers_b)

        return (2* overlap_size) / total
