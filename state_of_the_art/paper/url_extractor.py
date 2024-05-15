from typing import List
from urlextract import URLExtract

class PapersUrlsExtractor:
    def extract_urls(self, data: str) -> List[str]:

        if not type(data) == str:
            raise Exception("Data to extract papers must be a string")

        extractor = URLExtract()
        return extractor.find_urls(data)

    def overlap_size(self, papers_a, papers_b):
        overlap_size = 0
        for paper in papers_a:
            if paper in papers_b:
                overlap_size = overlap_size + 1

        total = len(papers_a) + len(papers_b)

        return (2 * overlap_size) / total
