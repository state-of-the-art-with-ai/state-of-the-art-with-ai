
import datetime
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.user_preferences.interest_table import Interests
from sentence_transformers import SentenceTransformer
from state_of_the_art.tables.base_table import BaseTable

class InterestRecommender:
    def __init__(self) -> None:
        self._sentence_transformer =  SentenceTransformer("all-mpnet-base-v2")
        self.date_from = datetime.date(2024, 8, 1)
        self.date_to =  datetime.date(2024, 8, 30)
    def generate(self):

        # get all interests
        interests_df = Interests().read()
        interests_to_str = [interest["description"] for interest in interests_df.to_dict(orient="records")]
        interests_embeddings = self._sentence_transformer.encode(interests_to_str)

        # get top similar papers for each interest
        papers_embeddings_df = self.load_paper_embeddigs_table().reset_index()
        papers_embeddings  = papers_embeddings_df["embedding"].to_list()

        similarity_matrix = self._sentence_transformer.similarity(interests_embeddings, papers_embeddings)
        for idx, interest in enumerate(interests_df.to_dict(orient="records")):
            # get the top 5 most similar papers indexes positions
            top_papers_indices = similarity_matrix[idx].argsort(descending=True)[0:5]
            print(f"Top papers for {interest['name']}, indices: {top_papers_indices}")
            papers = papers_embeddings_df.loc[top_papers_indices]
            print(papers)


    def encode_papers(self):
        papers_df = PapersLoader().load_between_dates(self.date_from, self.date_to)
        arxiv_papers = PapersLoader().to_papers(papers_df)

        papers = [paper.title + " " + paper.abstract for paper in arxiv_papers]
        result = self._sentence_transformer.encode(papers)

        table = PaperEmbeddingsTable()
        for idx, paper in enumerate(arxiv_papers):
            table.add(paper_id=paper.abstract_url, content=paper.title + " " + paper.abstract, embedding=result[idx])
    
    def load_paper_embeddigs_table(self):
        result = PaperEmbeddingsTable().read()
        return result



class PaperEmbeddingsTable(BaseTable):
    table_name = "paper_embeddings"
    schema = {
        "paper_id": {"type": str},
        "content": {"type": str},
        "embedding": {"type": list},
    }





if __name__ == "__main__":
    import fire
    fire.Fire(InterestRecommender)