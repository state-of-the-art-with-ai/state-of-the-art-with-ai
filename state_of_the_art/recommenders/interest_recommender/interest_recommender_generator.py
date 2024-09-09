import datetime
import json
from tqdm import tqdm
from typing import List, Tuple
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.tables.interest_table import Interests
from sentence_transformers import SentenceTransformer
from state_of_the_art.tables.papers_embeddings_table import PaperEmbeddingsTable
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationsHistoryTable,
)
from state_of_the_art.utils.mail import EmailService


class InterestsRecommender:
    PAPER_PER_TOPIC_TO_RENDER = 5
    TOP_PAPERS_TO_SELECT = 10

    def __init__(self, reencode_all_embeddings=False) -> None:
        self._sentence_transformer = SentenceTransformer("all-mpnet-base-v2")
        self.rencode_all_embeddings = reencode_all_embeddings

    def generate(
        self,
        number_of_days_to_look_back=1,
        repeat_check_disable=False,
        skip_register_new_papers=False,
    ):
        """
        to disable encode set encode=False
        """
        latest_date_with_papers = ArxivMiner().latest_date_with_papers()
        print(f"Latest date with papers submitted in arxiv: {latest_date_with_papers}")

        last_recommendation = RecommendationsHistoryTable().last().to_dict()
        if (
            last_recommendation["to_date"] == latest_date_with_papers.isoformat()
            and not repeat_check_disable
        ):
            raise Exception(
                f"No new papers since last recommendations on {last_recommendation['to_date']}"
            )

        self.date_to = latest_date_with_papers
        self.date_from = (
            datetime.datetime.fromisoformat(self.date_to.isoformat())
            - datetime.timedelta(days=number_of_days_to_look_back)
        ).date()

        if latest_date_with_papers < self.date_from and not repeat_check_disable:
            print("No new papers since {self.date_from} so skipping mining ")
        elif not skip_register_new_papers:
            print("Will now mine new papers")
            ArxivMiner().mine_all_keywords()

        self.load_papers_and_embeddings(self.date_from, self.date_to)

        # get all interests
        interests_df = Interests().read()

        result = {}
        result["interest_papers"] = {}
        for interest in interests_df.to_dict(orient="records"):
            # get the top most similar papers indexes positions
            top_papers, scores = self.get_papers_for_interest(
                interest["name"] + " " + interest["description"]
            )
            # get teh top scores for the papers

            result["interest_papers"][interest["name"]] = {}
            result["interest_papers"][interest["name"]]["papers"] = {}
            for paper_indice, paper in enumerate(top_papers):
                score = scores[paper_indice]
                result["interest_papers"][interest["name"]]["papers"][
                    paper.abstract_url
                ] = {"score": score}

        RecommendationsHistoryTable().add(
            from_date=self.date_from.isoformat(),
            to_date=self.date_to.isoformat(),
            recommended_papers=str(result),
            papers_analysed="",
            papers_analysed_total=len(self.papers),
        )

        self.format_and_send_email()

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

    def format_and_send_email(self):
        content_structured, data = RecommendationsHistoryTable().get_parsed_recommended_papers()
        content_structured = self.remove_duplicates(content_structured)
        content_str = f"""
Period from: {data['from_date']}
Period to: {data['to_date']}
Generated at: {data['tdw_timestamp']}
Papers analysed: {data['papers_analysed_total']}\n\n"""

        print(content_str)
        topic_counter = 1

        for interest, interest_data in content_structured.items():
            papers = PapersLoader().load_papers_from_urls(
                interest_data["papers"].keys()
            )
            content_str += f"{topic_counter}. {interest}\n"

            for paper in papers[0 : self.PAPER_PER_TOPIC_TO_RENDER]:
                paper_score = interest_data["papers"][paper.abstract_url]["score"]
                # add paper and url
                content_str += f"{paper.title}: {paper.abstract_url} ({paper.published_date_str()}) ({round(paper_score, 2)}) \n"

            content_str += "\n"
            content_str += "\n"
            topic_counter += 1

        print("Content str: ", content_str)

        title = (
            "Latest recommendations, generated at "
            + str(datetime.datetime.now()).split(".")[0]
        )
        EmailService().send(content=content_str, subject=title)

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
        existing_papers_df = existing_embedding_ds["paper_id"].to_list() if not existing_embedding_ds.empty else []
        papers_to_add = list(set(papers_candidates_ids) - set(existing_papers_df))

        if not papers_to_add:
            print("No new papers to add to table skipping encoding")
            return

        papers_str_list = [
            #papers_dict[paper_id].title + " " + papers_dict[paper_id].abstract
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
                    content= papers_dict[paper_id].title,
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

    def load_papers_embeddings(self, paper_ids: List[str]):
        result = PaperEmbeddingsTable().read()
        result = result[result["paper_id"].isin(paper_ids)]
        return result

    def remove_duplicates(self, recommendation_structure):
        papers_scores_by_category = {}
        for interest in recommendation_structure:
            for paper in recommendation_structure[interest]['papers']:
                if not paper in papers_scores_by_category:
                    papers_scores_by_category[paper] = [(interest, recommendation_structure[interest]['papers'][paper]['score'])]
                else:
                    papers_scores_by_category[paper].append((interest, recommendation_structure[interest]['papers'][paper]['score']))


        papers_scores_by_category = {k: sorted(v, key=lambda item: item[1], reverse=True) for k, v in  papers_scores_by_category.items()}

        result = {}
        for interest in recommendation_structure:
            result[interest] = {}
            result[interest]['papers'] = {}
            for paper in recommendation_structure[interest]['papers']:

                best_interest_for_paper = papers_scores_by_category[paper][0][0]

                if best_interest_for_paper == interest:
                    result[interest]['papers'][paper] = recommendation_structure[interest]['papers'][paper]



        return result
                                                                            



if __name__ == "__main__":
    import fire

    fire.Fire(InterestsRecommender)

