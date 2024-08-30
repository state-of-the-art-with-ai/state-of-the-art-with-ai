import os
import sys

import tqdm

from state_of_the_art.paper.papers_data_loader import PapersDataLoader


class SemanticSearch:
    def __init__(self):
        self.client = self.setup()

    def _get_chroma_instance(self):
        import chromadb

        self.chroma_path = os.environ["HOME"] + "/.chroma.db"
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        return self.client

    def setup(self):
        self._get_chroma_instance()
        try:
            self.collection = self.client.get_collection("papers")
        except Exception:
            print("Collection not found")
            self.collection = self.setup_papers()

        return self.client

    def setup_papers(self):
        print("Setting up documents")

        existing_ids = self.client.get_or_create_collection("papers").get()["ids"]
        papers = PapersDataLoader().get_all_papers()
        missing_papers = [
            paper for paper in papers if paper.abstract_url not in existing_ids
        ]
        print("Found ", len(missing_papers), " missing papers")

        collection = self.client.get_or_create_collection("papers")
        for paper in tqdm.tqdm(missing_papers):
            collection.add(
                documents=[paper.title + " " + paper.abstract],
                ids=[paper.abstract_url],
            )

        self.collection = collection
        print("Done setting up documents")

        return collection

    def search(self, query=None, n=20):
        if not query:
            if not sys.stdin.isatty():
                data = sys.stdin.readlines()
                query = "".join(data)

        ids = self.collection.query(query_texts=[query], n_results=n)["ids"][0]
        return ids

    def info(self):
        return {"docs_count": self.collection.count()}

    def reset(self):
        self.client.reset()
