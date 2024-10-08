import json
import os
import datetime
from tqdm import tqdm
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.recommenders.interest_recommender.embeddings_similarity import (
    EmbeddingsSimilarity,
)
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.relevance_model.text_evaluation_inference import TextEvaluationInference
from state_of_the_art.search.bm25_search import Bm25Search
from state_of_the_art.tables.interest_table import InterestTable
from state_of_the_art.tables.recommendations_history_table import (
    RecommendationGenerationStatus,
    RecommendationsRunsTable,
)
from state_of_the_art.tables.user_table import UserTable
from state_of_the_art.utils.mail import EmailService
import scipy.stats as stats


class InterestPaperRecommender:
    MAX_PAPERS_PER_TOPIC = 4

    def __init__(self) -> None:
        self.embedding_similarity = EmbeddingsSimilarity()
        self.bm25_search = Bm25Search()
        self.execution_id = None
        self.recommendations_runs_table = RecommendationsRunsTable(auth_filter=False)
        self.current_user_id = None
        self.current_user = None
        self.text_evaluation_inference = TextEvaluationInference()

    def generate(
        self,
        number_of_days_to_look_back=1,
        skip_register_new_papers=False,
        for_user=None
    ):
        """
        Generate a new set of recommendations based on the interests and the number of days to look back
        """

        print(
            f"Generating recomemndations for the last {number_of_days_to_look_back} days"
        )
        self.date_to = ArxivMiner().latest_date_with_papers()
        print(f"Latest date with papers submitted in arxiv: {self.date_to}")

        self.date_from = (
            datetime.datetime.fromisoformat(self.date_to.isoformat())
            - datetime.timedelta(days=number_of_days_to_look_back)
        ).date()

        self.setup_papers()
        users_df = UserTable().read()
        print(f"Total users found {len(users_df.index)} ")

        for user_dict in users_df.to_dict(orient="records"):
            self.current_user_id = user_dict["tdw_uuid"]
            print("Current user id: ", self.current_user_id)
            self.current_user = UserTable().find_user_by_uuid(self.current_user_id)
            print('Starting recommendations for user:', self.current_user.name)
            interests_df = InterestTable(auth_callable=lambda: self.current_user_id).read()
            print(f"Found {len(interests_df.index)} interests")
            if len(interests_df.index) == 0:
                print(f"No interests found for user {self.current_user.email} skipping ")
                continue
            try: 
                print("Recording execution ...")
                self.record_execution_start()
                # get all interests

                result = {}
                result["interest_papers"] = {}

                for interest in tqdm(interests_df.to_dict(orient="records")):
                    # get the top most similar papers indexes positions
                    query = interest["name"] + " " + interest["description"]
                    result["interest_papers"][interest["name"]] = {}
                    result["interest_papers"][interest["name"]]["papers"] = {}

                    bm25_papers, bm25_scores = self.bm25_search.search_returning_paper_and_score(
                        query
                    )
                    print(f"Search in bm25  for query: {query} returned {len(bm25_papers)} papers")

                    bm25_scores = stats.zscore(bm25_scores)
                    for paper_indice, paper in enumerate(bm25_papers):
                        score = bm25_scores[paper_indice]
                        result["interest_papers"][interest["name"]]["papers"][
                            paper.abstract_url
                        ] = {"bm25_score": score, "semantic_score": 0}

                    top_papers, semantic_scores = (
                        self.embedding_similarity.get_papers_for_interest(query)
                    )
                    semantic_scores = stats.zscore(semantic_scores)

                    for paper_indice, paper in enumerate(top_papers):
                        semantic_score = semantic_scores[paper_indice]
                        existing_bm25_score = result["interest_papers"][interest["name"]]['papers'][paper.abstract_url]['bm25_score'] if paper.abstract_url in result["interest_papers"][interest["name"]]['papers'] else 0
                        result["interest_papers"][interest["name"]]["papers"][
                            paper.abstract_url
                        ] = {"semantic_score": semantic_score, "bm25_score": existing_bm25_score}

                    # add text evaluation score
                for interest_name, interest_data in result["interest_papers"].items():
                    print("Loading papers for ", interest_name)
                    papers_of_interest = PapersLoader().load_papers_from_urls(interest_data['papers'].keys())
                    print("Loaded ", len(papers_of_interest), " papers for ", interest_name)
                    print("Text evaluation inference for ", interest_name)
                    text_evaluation_scores = self.text_evaluation_inference.predict_batch([paper.title for paper in papers_of_interest])
                    text_evaluation_scores = stats.zscore(text_evaluation_scores)

                    for paper_indice, paper_key in enumerate(interest_data['papers']):
                        result["interest_papers"][interest_name]["papers"][paper_key]["text_evaluation_score"] = text_evaluation_scores[paper_indice]

                # sum scores in a final score
                result = self.sum_scores(result)

                result["interest_papers"] = self._remove_duplicates(result["interest_papers"])
                result["interest_papers"] = self._sort_interests_by_scores(
                    result["interest_papers"]
                )

                self.recommendations_runs_table.update(by_key='tdw_uuid', by_value=self.execution_id, new_values={
                        'recommended_papers':json.dumps(result),
                        'papers_analysed_total': len(self.papers_analysed),
                        'status': RecommendationGenerationStatus.SUCCESS,
                        'from_date': self.date_from.isoformat(),
                        'to_date': self.date_to.isoformat(),
                        'end_time': datetime.datetime.now().isoformat(),
                    }
                )
                self.format_and_send_email()
            except Exception as e:
                self.record_error(e)
                result = ''  

        return result
    
    def sum_scores(self, result):
        for interest in result["interest_papers"]:
            for paper in result["interest_papers"][interest]["papers"]:
                bm25_score = result["interest_papers"][interest]["papers"][paper]['bm25_score']
                semantic_score = result["interest_papers"][interest]["papers"][paper]['semantic_score']
                text_evaluation_score = result["interest_papers"][interest]["papers"][paper]['text_evaluation_score']

                result["interest_papers"][interest]["papers"][paper]["final_score"] = bm25_score + semantic_score + text_evaluation_score
        return result

    def setup_papers(self):
        self.papers_analysed, self.papers_embeddings = (
            self.embedding_similarity.load_papers_and_embeddings(
                self.date_from, self.date_to
            )
        )

        print(f"Setting {len(self.papers_analysed)} papers to BM25 search")
        self.bm25_search.set_papers_and_index(self.papers_analysed)


    def record_error(self, e):
        print(f"Error while generating recommendations: {e}")
        import traceback
        print(traceback.format_exc())


        self.recommendations_runs_table.update(by_key='tdw_uuid', by_value=self.execution_id, new_values={
                'status': RecommendationGenerationStatus.ERROR,
                'error_details': str(e),
                'end_time': datetime.datetime.now().isoformat(),
            }
        )


    def record_execution_start(self):
        self.execution_id = self.recommendations_runs_table.add(
            from_date=None,
            to_date=None,
            recommended_papers=None,
            start_time=datetime.datetime.now().isoformat(),
            end_time=None,
            papers_analysed="",
            papers_analysed_total=None,
            status=RecommendationGenerationStatus.STARTED,
            error_details="",
            user_id = self.current_user_id
        )


    def format_and_send_email(self):
        content_structured, data = (
            self.recommendations_runs_table.get_parsed_recommended_papers()
        )

        to_date = datetime.datetime.strptime(data["to_date"], "%Y-%m-%d").date()
        from_date = datetime.datetime.strptime(data["from_date"], "%Y-%m-%d").date()
        days = (to_date - from_date).days

        content_str = f"""Hello, {self.current_user.get_name()},<br><br>

About these recommendations:<br>
Papers from: {data['from_date']} To: {data['to_date']} ({days}) days<br>
Generated at: {data['tdw_timestamp']} By user: {os.environ.get('USER', "None set")}<br>
Papers analysed: {data['papers_analysed_total']}<br><br>

"""

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
            f"Recommendations covering the last {days} days up to "
            + str(datetime.datetime.now()).split(".")[0]
        )
        EmailService().send(content=content_str, subject=title, recepient=self.current_user.email)

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
