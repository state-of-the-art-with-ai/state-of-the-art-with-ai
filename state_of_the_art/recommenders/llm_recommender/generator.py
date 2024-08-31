import os
import sys
from typing import Optional, List, Tuple

import datetime
from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.papers_data_loader import PapersLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.deprecated_recommender.ranker.rank_data import RankGeneratedData
from state_of_the_art.deprecated_recommender.ranker.structured_ranker import StructuredPaperRanker
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.deprecated_recommender.report_parameters import ReportParameters
from state_of_the_art.config import config

from state_of_the_art.deprecated_recommender.topic_based.topic_search import TopicSearch
from state_of_the_art.utils import pdf
from state_of_the_art.utils.mail import SotaMail


class RecommenderTable:
    TABLE_NAME = "state_of_the_art_summary"

    def read(self):
        return config.get_datawarehouse().event(RecommenderTable.TABLE_NAME)

    def get_latest(self) -> dict:
        df = self.read()
        return df.iloc[-1]


class Recommender:
    """
    Class responsible to the entire generation pipeline
    """

    _input_articles: Optional[List[ArxivPaper]] = None
    _topic_search: Optional[TopicSearch] = None

    def __init__(self):
        self._miner = ArxivMiner()

    def generate(
        self,
        *,
        number_lookback_days: Optional[int] = None,
        from_date: Optional[str] = None,
        skip_register: bool = False,
        batch=1,
        batch_size=None,
        max_papers_per_query=None,
        papers_to_rank=None,
        query: Optional[str] = None,
        by_topic: Optional[str] = None,
        problem_description: Optional[str] = None,
        use_clipboard_for_problem_description: bool = False,
        number_of_recommendations=None,
        skip_email=False,
        disable_open_pdf=False,
        disable_pdf=False,
    ):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """

        context = ReportParameters(
            lookback_days=number_lookback_days,
            from_date=from_date,
            skip_register=skip_register,
            batch=batch,
            batch_size=batch_size,
            papers_to_rank=papers_to_rank,
            query=query,
            by_topic=by_topic,
            problem_description=problem_description,
            use_clipboard_for_problem_description=use_clipboard_for_problem_description,
            number_of_papers_to_recommend=number_of_recommendations,
        )

        if skip_register or context.by_topic:
            print("Skipping global registration")
        else:
            last_date_with_papers = self._miner.latest_date_with_papers()
            if not context.query and last_date_with_papers < context.from_date:
                raise Exception(
                    "No new papers found since ",
                    str(last_date_with_papers),
                    "and you are looking from ",
                    str(context.from_date),
                )

            self._miner.register_all_new_papers(max_papers_per_query=max_papers_per_query)

        result = self._rank(context)
        formatted_result = self._format_results(result, context)
        profile_name = config.get_current_audience().name.upper()

        if not disable_pdf:
            location = pdf.create_pdf(
                data=formatted_result,
                output_path_description=f"recommender summary {profile_name} {context.by_topic if context.by_topic else ""} ",
                disable_open=disable_open_pdf,
            )
        else:
            location = None
        context.generated_pdf_location = location

        self._write_event(context, formatted_result, result)

        if not skip_email:
            self._send_email(
                formatted_result,
                f"Sota summary batch {context.batch} for profile {profile_name}",
            )

        return result

    def _get_topic_search(self) -> TopicSearch:
        if not self._topic_search:
            self._topic_search = TopicSearch()
            self._input_articles = self._topic_search._papers_list

        return self._topic_search

    def _rank(self, context: ReportParameters) -> Tuple[str, dict]:
        if context.by_topic:
            self._miner.register_by_relevance(
                max_papers_per_query=None, topic_name=context.by_topic
            )

            result, automated_query = self._get_topic_search().search_by_topic(
                context.by_topic,
                num_of_results=context.number_of_papers_to_recommend,
            )

            context.machine_generated_query = automated_query

            return result

        if context.query:
            return self._get_topic_search().search_with_query(context.query)

        if context.use_clipboard_for_problem_description:
            import subprocess

            output = subprocess.getoutput("clipboard get_content")
            print("Clipboard content: ", output)
            context.machine_generated_query = self._get_topic_search().extract_query(
                output
            )
            return self._get_topic_search().search_with_query(
                context.machine_generated_query
            )

        if context.problem_description:
            import subprocess

            context.machine_generated_query = self._get_topic_search().extract_query(
                context.problem_description
            )
            return self._get_topic_search().search_with_query(
                context.machine_generated_query
            )

        if not sys.stdin.isatty():
            print("Reading from stdin")
            stdindata = "\n".join(sys.stdin.readlines())
            context.machine_generated_query = self._get_topic_search().extract_query(
                stdindata
            )
            return self._get_topic_search().search_with_query(
                context.machine_generated_query
            )
        # if we arrrive here we want to rank the latest articles
        context.type = "latest"

        self._input_articles = PapersLoader().to_papers(
            PapersLoader().get_latest_articles(
                lookback_days=context.lookback_days,
                from_date=context.from_date,
                batch=context.batch,
                batch_size=context.batch_size,
            )
        )

        result, structured_result = StructuredPaperRanker().rank(articles=self._input_articles)

        return result

    def _format_results(self, result: str, parameters: ReportParameters) -> str:
        formatted_ranked_result = PapersFormatter().from_str(result)
        profile_name = config.get_current_audience().name

        query_str = f"Query: {parameters.query} \n" if parameters.query else ""
        machine_query_str = (
            f"Machine query: {parameters.machine_generated_query} \n"
            if parameters.machine_generated_query
            else ""
        )
        topic_str = f"Topic: {parameters.by_topic} \n" if parameters.by_topic else ""
        number_of_papers = (
            f"Num of results: {parameters.number_of_papers_to_recommend} \n"
            if parameters.number_of_papers_to_recommend
            else ""
        )
        from_date_str = (
            f"From date: {parameters.from_date} \n" if parameters.from_date else ""
        )

        now = datetime.datetime.now().isoformat()
        header = f"""Generated at {now} ({len(self._input_articles)}) papers analysed
Profile: "{profile_name}"  
{query_str}{machine_query_str}{topic_str}{from_date_str}{number_of_papers}
"""
        formatted_ranked_result = header + formatted_ranked_result

        if self._input_articles:
            articles_as_input = PapersFormatter().from_papers(
                self._input_articles[0:200]
            )
            formatted_ranked_result += f""" -----------------------------
Papers analysed: \n{articles_as_input}"""

        return formatted_ranked_result

    def _write_event(self, parameters, formatted_result, result):
        papers_str = PapersLoader().papers_to_urls_str(self._input_articles)
        ranking_data = RankGeneratedData(
            from_date=parameters.from_date.isoformat(),
            to_date=parameters.to_date if parameters.to_date else None,
            prompt="",
            summary=formatted_result,
            llm_result=result,
            papers_analysed=papers_str,
            pdf_location=parameters.generated_pdf_location,
        )
        if os.environ.get("SOTA_TEST"):
            print("Mocking event, not writing to datawarehouse")
            return

        config.get_datawarehouse().write_event(
            RecommenderTable.TABLE_NAME, ranking_data.to_dict()
        )

    def _send_email(self, formatted_result, title):
        print("Sending email")
        if os.environ.get("LLM_MOCK") or os.environ.get("SOTA_TEST"):
            print("Mocking email")
            return

        SotaMail().send(
            formatted_result,
            title,
        )

    def _load_papers_from_str(self, papers_str: str):
        urls = PapersUrlsExtractor().extract_urls(papers_str)
        return PapersLoader().load_from_urls(urls, fail_on_missing_ids=False)
