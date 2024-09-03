import datetime
import json
from tqdm import tqdm
from typing import List
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.tables.interest_table import Interests
from sentence_transformers import SentenceTransformer
from state_of_the_art.tables.base_table import BaseTable
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationsHistoryTable,
)
from state_of_the_art.utils.mail import EmailService

class InterestsRecommender:
    def __init__(self) -> None:
        self._sentence_transformer = SentenceTransformer("all-mpnet-base-v2")

    def generate(self, skip_register_new_papers=False, encode=True, ignore_last_recommendation=False):
        latest_date_with_papers = ArxivMiner().latest_date_with_papers()
        print(f"Latest date with papers submitted in arxiv: {latest_date_with_papers}")

        last_recommendation = RecommendationsHistoryTable().last().to_dict()
        if last_recommendation['to_date'] == latest_date_with_papers.isoformat() and not ignore_last_recommendation:
            raise Exception(f"No new papers since last recommendations on {last_recommendation['to_date']}")

        self.date_to = latest_date_with_papers
        self.date_from = (datetime.datetime.fromisoformat(self.date_to.isoformat()) - datetime.timedelta(days=1)).date()

        
        if  latest_date_with_papers < self.date_from:
            print("No new papers since {self.date_from} so skipping mining ")
        elif not skip_register_new_papers:
            print("Will now mine new papers")
            ArxivMiner().register_all_new_papers()

        papers_df = PapersLoader().load_between_dates(self.date_from, self.date_to)
        if papers_df.empty:
            raise Exception(f"No papers found between {self.date_from} and {self.date_to} so cannot generate recommendations")
        
        print(f"Found {len(papers_df.index)} papers between {self.date_from} and {self.date_to}")
        arxiv_papers = PapersLoader().to_papers(papers_df)

        if encode:
            self.encode_papers(arxiv_papers)

        # get all interests
        interests_df = Interests().read()
        interests_to_str = [
            interest["description"]
            for interest in interests_df.to_dict(orient="records")
        ]

        print("Encoding interests")
        interests_embeddings = self._sentence_transformer.encode(interests_to_str, show_progress_bar=True)

        # get top similar papers for each interest
        papers_embeddings_df = self.load_paper_embeddigs_table(paper_ids=papers_df['abstract_url'].to_list()).reset_index()
        papers_embeddings = papers_embeddings_df["embedding"].to_list()


        print("Calculating similarities")
        similarity_matrix = self._sentence_transformer.similarity(
            interests_embeddings, papers_embeddings
        )
        TOP_PAPERS_TO_SELECT = 10

        result = {}
        result['interest_papers'] = {}
        for interest_index, interest in enumerate(interests_df.to_dict(orient="records")):
            # get the top most similar papers indexes positions
            top_papers_indices = similarity_matrix[interest_index].argsort(descending=True)[0:TOP_PAPERS_TO_SELECT]
            # get teh top scores for the papers

            print(f"Top papers for {interest['name']}, indices: {top_papers_indices}")
            result['interest_papers'][interest["name"]] = {}
            result['interest_papers'][interest["name"]]["papers"] = {}
            for index in top_papers_indices:
                score = similarity_matrix[interest_index][index].detach().item()
                paper = arxiv_papers[index]
                result['interest_papers'][interest["name"]]["papers"][paper.abstract_url] = {"score": score}

        RecommendationsHistoryTable().add(
            from_date=self.date_from.isoformat(),
            to_date=self.date_to.isoformat(),
            recommended_papers=str(result),
            papers_analysed="",
            papers_analysed_total=len(papers_df.index),
        )


        self.format_and_send_email()

        return result

    def format_and_send_email(self):
        df = RecommendationsHistoryTable().last()
        data = df.to_dict()
        json_encoded = data['recommended_papers'].replace("'", '"')
        print("Json encoded: ", json_encoded)
        content_structured = json.loads(json_encoded)['interest_papers']

        content_str = f"""
Period from: {data['from_date']}
Period to: {data['to_date']}
Papers analysed: {data['papers_analysed_total']}\n\n"""
        topic_counter = 1
        NUMBER_OF_PAPERS_PER_TOPIC = 3

        # add total score to interest
        content_structured = {k: v for k, v in sorted(content_structured.items(), key=lambda item: sum([paper['score'] for paper in item[1]['papers'].values()]), reverse=True)}
        

        for interest, interest_data in content_structured.items():
            papers = PapersLoader().load_papers_from_urls(interest_data['papers'].keys())
            content_str += f"{topic_counter}. {interest}\n"

            for paper in papers[0:NUMBER_OF_PAPERS_PER_TOPIC]:
                paper_score = interest_data['papers'][paper.abstract_url]['score']
                # add paper and url
                content_str += f"{paper.title}: {paper.abstract_url} ({paper.published_date_str()}) ({round(paper_score, 2)}) \n"

            content_str += "\n"
            content_str += "\n"
            topic_counter += 1

        print("Content str: ", content_str)

        title = "Latest recommendations, generated at " + str(datetime.datetime.now()).split(".")[0]
        EmailService().send(content=content_str, subject=title)

    def encode_papers(self, arxiv_papers: List[ArxivPaper]):
        """
        Encode all papers between the date_from and date_to into embeddings
        """

        print("Encoding papers to embeddings")
        papers = [paper.title + " " + paper.abstract for paper in arxiv_papers]
        result = self._sentence_transformer.encode(papers, show_progress_bar=True)

        table = PaperEmbeddingsTable()

        print("Writing embeddings to table")
        for index, paper in tqdm(enumerate(arxiv_papers)):
            table.update_or_create(
                by_key="paper_id",
                by_value=paper.abstract_url,
                new_values={
                    "paper_id": paper.abstract_url,
                    "content": paper.title + " " + paper.abstract,
                    "embedding": result[index],
                }
            )
        
        df = table.read()

        return df

    def load_paper_embeddigs_table(self, paper_ids: List[str]):
        result = PaperEmbeddingsTable().read()
        result = result[result['paper_id'].isin(paper_ids)]
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

    fire.Fire(InterestsRecommender)
