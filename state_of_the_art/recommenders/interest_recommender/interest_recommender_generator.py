import datetime
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.recommenders.interest_recommender.embeddings_similarity import EmbeddingsSimilarity
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.search.bm25_search import Bm25Search
from state_of_the_art.tables.interest_table import Interests
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationsHistoryTable,
)
from state_of_the_art.utils.mail import EmailService


class InterestsRecommender:
    PAPER_PER_TOPIC_TO_RENDER = 5

    def __init__(self) -> None:
        self.embedding_similarity = EmbeddingsSimilarity()
        self.bm25_search = Bm25Search()

    def generate(
        self,
        number_of_days_to_look_back=1,
        repeat_check_disable=False,
        skip_register_new_papers=False,
    ):
        """
        Generate a new set of recommendations based on the interests and the number of days to look back
        """
        latest_date_with_papers = ArxivMiner().latest_date_with_papers()
        print(f"Latest date with papers submitted in arxiv: {latest_date_with_papers}")

        last_recommendation = RecommendationsHistoryTable().last().to_dict()
        if (
            not repeat_check_disable and 
            last_recommendation["to_date"] == latest_date_with_papers.isoformat()
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

        self.papers, self.papers_embeddings = self.embedding_similarity.load_papers_and_embeddings(
            self.date_from, self.date_to
        )

        self.bm25_search.set_papers_and_index(self.papers)

        # get all interests
        interests_df = Interests().read()

        result = {}
        result["interest_papers"] = {}
        for interest in interests_df.to_dict(orient="records"):
            # get the top most similar papers indexes positions
            query = interest["name"] + " " + interest["description"]
            result["interest_papers"][interest["name"]] = {}
            result["interest_papers"][interest["name"]]["papers"] = {}

            papers_and_scores = self.bm25_search.search_returning_tuple(query)
            for paper, score in papers_and_scores:
                if paper.abstract_url in result["interest_papers"][interest["name"]]["papers"]:
                    result["interest_papers"][interest["name"]]["papers"][
                        paper.abstract_url
                    ]["bm25_score"] = score
                else:
                    result["interest_papers"][interest["name"]]["papers"][
                        paper.abstract_url
                    ] = {"bm25_score": score, "semantic_score": 0}

            
            top_papers, semantic_scores = self.embedding_similarity.get_papers_for_interest(query)

            for paper_indice, paper in enumerate(top_papers):
                semantic_score = semantic_scores[paper_indice]
                result["interest_papers"][interest["name"]]["papers"][
                    paper.abstract_url
                ] = {"semantic_score": semantic_score, "bm25_score": 0}



        result["interest_papers"] = self._remove_duplicates(result["interest_papers"])
        result["interest_papers"] = self._sort_interests_by_scores(result["interest_papers"])

        RecommendationsHistoryTable().add(
            from_date=self.date_from.isoformat(),
            to_date=self.date_to.isoformat(),
            recommended_papers=str(result),
            papers_analysed="",
            papers_analysed_total=len(self.papers),
        )

        self.format_and_send_email()

        return result

    def format_and_send_email(self):
        content_structured, data = (
            RecommendationsHistoryTable().get_parsed_recommended_papers()
        )
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
                paper_score = interest_data["papers"][paper.abstract_url]["bm25_score"]
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

    def _remove_duplicates(self, recommendation_structure, score_column='semantic_score'):
        papers_scores_by_category = {}
        for interest in recommendation_structure:
            for paper in recommendation_structure[interest]["papers"]:
                if paper not in papers_scores_by_category:
                    papers_scores_by_category[paper] = [
                        (
                            interest,
                            recommendation_structure[interest]["papers"][paper][
                                score_column
                            ],
                        )
                    ]
                else:
                    papers_scores_by_category[paper].append(
                        (
                            interest,
                            recommendation_structure[interest]["papers"][paper][
                                score_column
                            ],
                        )
                    )

        papers_scores_by_category = {
            k: sorted(v, key=lambda item: item[1], reverse=True)
            for k, v in papers_scores_by_category.items()
        }

        result = {}
        for interest in recommendation_structure:
            result[interest] = {}
            result[interest]["papers"] = {}
            for paper in recommendation_structure[interest]["papers"]:
                best_interest_for_paper = papers_scores_by_category[paper][0][0]

                if best_interest_for_paper == interest:
                    result[interest]["papers"][paper] = recommendation_structure[
                        interest
                    ]["papers"][paper]

        return result

    def _sort_interests_by_scores(self, recommendation_structure, score_column='bm25_score'):
        interest_scores_sum = {}
        for interest, papers in recommendation_structure.items():
            interest_scores_sum[interest] = 0
            for _, paper_data in papers["papers"].items():
                interest_scores_sum[interest] += paper_data[score_column]
        sort_interests_scores = sorted(
            interest_scores_sum.items(), key=lambda item: item[1], reverse=True
        )

        # sort given dict with interest scores sum highest first
        # sort with a lambda function
        result_dict = {}

        for interest, score_sum in sort_interests_scores:
            result_dict[interest] = recommendation_structure[interest]

        return result_dict


if __name__ == "__main__":
    import fire

    fire.Fire(InterestsRecommender)