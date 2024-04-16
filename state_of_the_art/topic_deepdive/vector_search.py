import os

from state_of_the_art.paper.papers_data import PapersData


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
        papers = PapersData().get_all_papers()
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

    def search(self, query, n=20):
        ids = self.collection.query(query_texts=[query], n_results=n)['ids'][0]
        print(ids)

        papers_data = PapersData()
        papers = papers_data.to_papers(papers_data.load_from_urls(ids))

        counter = 1
        for paper in papers:
            print(f"{counter}. ", paper)
            counter+=1



    def info(self):
        return {
            'docs': self.collection.get()

        }

    def reset(self):
        self.client.reset()





if __name__ == "__main__":
    import fire
    fire.Fire()