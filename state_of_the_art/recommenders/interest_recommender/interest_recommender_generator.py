import os
import datetime
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.recommenders.interest_recommender.embeddings_similarity import (
    EmbeddingsSimilarity,
)
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.search.bm25_search import Bm25Search
from state_of_the_art.tables.interest_table import InterestTable
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationsHistoryTable,
)
from state_of_the_art.utils.mail import EmailService
import scipy.stats as stats


class InterestPaperRecommender:
    MAX_PAPERS_PER_TOPIC = 4

    def __init__(self) -> None:
        self.embedding_similarity = EmbeddingsSimilarity()
        self.bm25_search = Bm25Search()

    def generate(
        self,
        number_of_days_to_look_back=1,
        skip_register_new_papers=False,
    ):
        """
        Generate a new set of recommendations based on the interests and the number of days to look back
        """
        print(
            f"Generating recomemndations for the last {number_of_days_to_look_back} days"
        )
        latest_date_with_papers = ArxivMiner().latest_date_with_papers()
        print(f"Latest date with papers submitted in arxiv: {latest_date_with_papers}")

        last_recommendation = RecommendationsHistoryTable().last().to_dict()
        print(f"No new papers since last recommendations on {last_recommendation['to_date']}")

        self.date_to = latest_date_with_papers
        self.date_from = (
            datetime.datetime.fromisoformat(self.date_to.isoformat())
            - datetime.timedelta(days=number_of_days_to_look_back)
        ).date()

        if latest_date_with_papers < self.date_from:
            print("No new papers since {self.date_from} so skipping mining ")
        elif not skip_register_new_papers:
            print("Will now mine new papers")
            ArxivMiner().mine_all_keywords()

        self.papers, self.papers_embeddings = (
            self.embedding_similarity.load_papers_and_embeddings(
                self.date_from, self.date_to
            )
        )

        self.bm25_search.set_papers_and_index(self.papers)

        # get all interests
        interests_df = InterestTable().read()

        result = {}
        result["interest_papers"] = {}
        for interest in interests_df.to_dict(orient="records"):
            # get the top most similar papers indexes positions
            query = interest["name"] + " " + interest["description"]
            result["interest_papers"][interest["name"]] = {}
            result["interest_papers"][interest["name"]]["papers"] = {}

            papers, bm25_scores = self.bm25_search.search_returning_paper_and_score(
                query
            )
            bm25_scores = stats.zscore(bm25_scores)
            for paper_indice, paper in enumerate(papers):
                score = bm25_scores[paper_indice]
                if (
                    paper.abstract_url
                    in result["interest_papers"][interest["name"]]["papers"]
                ):
                    result["interest_papers"][interest["name"]]["papers"][
                        paper.abstract_url
                    ]["bm25_score"] = score
                else:
                    result["interest_papers"][interest["name"]]["papers"][
                        paper.abstract_url
                    ] = {"bm25_score": score, "semantic_score": 0}

            top_papers, semantic_scores = (
                self.embedding_similarity.get_papers_for_interest(query)
            )
            semantic_scores = stats.zscore(semantic_scores)

            for paper_indice, paper in enumerate(top_papers):
                semantic_score = semantic_scores[paper_indice]
                result["interest_papers"][interest["name"]]["papers"][
                    paper.abstract_url
                ] = {"semantic_score": semantic_score, "bm25_score": 0}

        # sum scores in a final score
        for interest in result["interest_papers"]:
            for paper in result["interest_papers"][interest]["papers"]:
                result["interest_papers"][interest]["papers"][paper]["final_score"] = (
                    result["interest_papers"][interest]["papers"][paper]["bm25_score"]
                    + result["interest_papers"][interest]["papers"][paper][
                        "semantic_score"
                    ]
                )

        result["interest_papers"] = self._remove_duplicates(result["interest_papers"])
        result["interest_papers"] = self._sort_interests_by_scores(
            result["interest_papers"]
        )

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
        import datetime

        to_date = datetime.datetime.strptime(data["to_date"], "%Y-%m-%d").date()
        from_date = datetime.datetime.strptime(data["from_date"], "%Y-%m-%d").date()
        days = (to_date - from_date).days

        content_str = f"""
Period from: {data['from_date']}<br>
Period to: {data['to_date']}<br>
Days = {days}<br>
Generated at: {data['tdw_timestamp']}<br>
By user: {os.environ.get('USER', "None set")}<br>
Papers analysed: {data['papers_analysed_total']}<br><br>"""

        print(content_str)
        topic_counter = 1

        for interest, interest_data in content_structured.items():
            papers = PapersLoader().load_papers_from_urls(
                interest_data["papers"].keys()
            )
            content_str += f"{topic_counter}. {interest}<br>"

            for paper in papers[0 : self.MAX_PAPERS_PER_TOPIC]:
                paper_score = interest_data["papers"][paper.abstract_url]["bm25_score"]
                # add paper and url
                content_str += f'<a href="https://state-of-the-art-with-ai-750989039686.europe-west3.run.app/paper_details_page?paper_url={paper.abstract_url}"> {paper.title} {paper.published_date_str()} ({round(paper_score, 2)})</a> <br>'

            content_str += "<br><br>"
            topic_counter += 1

        print("Content str: ", content_str)

        title = (
            f"Papers covering {days} days up to "
            + str(datetime.datetime.now()).split(".")[0]
        )
        EmailService().send(content=content_str, subject=title)

    def _remove_duplicates(self, recommendation_structure, score_column="final_score"):
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

    def _sort_interests_by_scores(
        self, recommendation_structure, score_column="final_score"
    ):
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

    fire.Fire(InterestPaperRecommender)
