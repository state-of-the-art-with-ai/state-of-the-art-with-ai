import os

import sys

from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.papers_data import PapersInDataWharehouse


class VectorSearch:

    def __init__(self):
        self.client = self.setup()
    def setup(self):
        import chromadb
        self.chroma_path = os.environ['HOME'] + '/.chroma.db'
        self.client = chromadb.PersistentClient(path=self.chroma_path)

        try:
            self.collection = self.client.get_collection('papers')
        except:
            self.collection = self.setup_papers()



        return self.client
    def setup_papers(self):
        print('Setting up documents')
        papers = PapersInDataWharehouse().get_all_papers()
        documents = []
        ids = []
        for paper in papers:
            documents.append(paper.title + ' ' + paper.abstract)
            ids.append(paper.url)

        collection = self.client.get_or_create_collection('papers')
        print('Adding documents', len(documents))
        collection.add(
            documents=documents,
            ids=ids,
        )
        self.collection = collection
        print('Done setting up documents')

        return collection

    def search(self, query=None, n=20):

        if not query:
            if not sys.stdin.isatty():
                data = sys.stdin.readlines()
                query = "".join(data)

        ids = self.collection.query(query_texts=[query], n_results=n)['ids'][0]
        print(ids)

        papers_data = PapersInDataWharehouse()
        papers = papers_data.to_papers(papers_data.load_from_urls(ids))

        print(PapersFormatter(disable_abstract=True).from_papers(papers))



    def info(self):
        return {
            'docs': self.collection.get()

        }

    def reset(self):
        self.client.reset()





if __name__ == "__main__":
    import fire
    fire.Fire()