from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.tables.papers_embeddings_table import PaperEmbeddingsTable


from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from typing import List, Tuple

class EmbeddingsSimilarity:
    TOP_PAPERS_TO_SELECT = 10
    def __init__(self, reencode_all_embeddings: bool = False) -> None:
        self._sentence_transformer = SentenceTransformer("all-mpnet-base-v2")
        self.rencode_all_embeddings = reencode_all_embeddings
    def load_papers_and_embeddings(self, date_from, date_to):
        papers_df = PapersLoader().load_between_dates(date_from, date_to)
        if papers_df.empty:
            raise Exception(
                f"No papers found between {date_from} and {date_to} so cannot generate recommendations"
            )

        print(f"Found {len(papers_df.index)} papers between {date_from} and {date_to}")
        self.papers = arxiv_papers = PapersLoader().to_papers(papers_df)

        self._encode_missing_papers(arxiv_papers)

        papers_embeddings_df = self.load_papers_embeddings(
            paper_ids=papers_df["abstract_url"].to_list()
        ).reset_index()
        self.papers_embeddings = papers_embeddings_df["embedding"].to_list()

        return self.papers, self.papers_embeddings

    def load_papers_embeddings(self, paper_ids: List[str]):
        result = PaperEmbeddingsTable().read()
        result = result[result["paper_id"].isin(paper_ids)]
        return result

    def get_papers_for_interest(
        self, interest_str: str
    ) -> Tuple[List[ArxivPaper], List[float]]:
        interests_embedding = self._sentence_transformer.encode(
            interest_str, show_progress_bar=True
        )

        print("Calculating similarities")
        similarity_matrix = self._sentence_transformer.similarity(
            [interests_embedding], self.papers_embeddings
        )
        # return the closest match papapers
        top_indices = similarity_matrix[0].argsort(descending=True)[
            0 : self.TOP_PAPERS_TO_SELECT
        ]
        scores = [similarity_matrix[0][index].detach().item() for index in top_indices]
        papers = [self.papers[index] for index in top_indices]
        # get teh top scores for the papers
        print(
            "Top papers for interest: ",
            interest_str,
            " are: ",
            [paper.title for paper in papers],
        )

        # print top papers matching
        return papers, scores

    def _encode_missing_papers(self, arxiv_papers: List[ArxivPaper]):
        """
        Encode all papers between the date_from and date_to into embeddings
        """

        print("Encoding papers to embeddings")
        papers_candidates_ids = [paper.abstract_url for paper in arxiv_papers]
        papers_dict = {paper.abstract_url: paper for paper in arxiv_papers}

        table = PaperEmbeddingsTable()
        if self.rencode_all_embeddings:
            table.reset(dry_run=False)

        existing_embedding_ds = table.read()
        existing_papers_df = (
            existing_embedding_ds["paper_id"].to_list()
            if not existing_embedding_ds.empty
            else []
        )
        papers_to_add = list(set(papers_candidates_ids) - set(existing_papers_df))

        if not papers_to_add:
            print("No new papers to add to table skipping encoding")
            return

        papers_str_list = [
            # papers_dict[paper_id].title + " " + papers_dict[paper_id].abstract
            papers_dict[paper_id].title
            for paper_id in papers_to_add
        ]
        result = self._sentence_transformer.encode(
            papers_str_list, show_progress_bar=True
        )

        print("Writing embeddings to table in progress bellow...")
        for index, paper_id in tqdm(enumerate(papers_to_add), total=len(papers_to_add)):
            if self.rencode_all_embeddings:
                table.add(
                    paper_id=paper_id,
                    content=papers_dict[paper_id].title,
                    embedding=result[index],
                )
            else:
                table.update_or_create(
                    by_key="paper_id",
                    by_value=paper_id,
                    new_values={
                        "paper_id": paper_id,
                        "content": papers_dict[paper_id].title,
                        "embedding": result[index],
                    },
                )

        df = table.read()

        return df