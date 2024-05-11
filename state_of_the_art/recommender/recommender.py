import os
from typing import Optional, List

from datetime import datetime
from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.paper import ArxivPaper
from state_of_the_art.paper.papers_data import PapersInDataWharehouse
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.recommender.ranker.rank_data import RankGeneratedData
from state_of_the_art.register_papers.arxiv_miner import PaperMiner
from state_of_the_art.recommender.ranker.ranker import PaperRanker
from state_of_the_art.recommender.report_parameters import RecommenderParameters
from state_of_the_art.recommender.reports_data import ReportsData
from state_of_the_art.config import config
import sys

from state_of_the_art.recommender.topic_based.topic_search import TopicSearch
from state_of_the_art.utils import pdf
from state_of_the_art.utils.mail import SotaMail


class Recommender:
    """
    Class responsible to the entire generation pipeline
    """

    _input_articles: Optional[List[ArxivPaper]] = None

    def __init__(self):
        self._topic_search = TopicSearch()
        self._input_articles = self._topic_search._papers_list

    def generate(
        self,
        *,
        number_lookback_days=None,
        from_date=None,
        to_date=None,
        skip_register=False,
        dry_run=False,
        batch=1,
        batch_size=None,
        max_papers_per_query=None,
        papers_to_rank=None,
        query: Optional[str] = None,
        by_topic: Optional[str] = None,
        description_from_clipboard=False,
    ):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """

        parameters = RecommenderParameters(
            lookback_days=number_lookback_days,
            from_date=from_date,
            to_date=to_date,
            skip_register=skip_register,
            dry_run=dry_run,
            batch=batch,
            batch_size=batch_size,
            papers_to_rank=papers_to_rank,
            query=query,
            by_topic=by_topic,
            description_from_clipboard=description_from_clipboard,
        )

        if not skip_register:
            PaperMiner().register_new(
                dry_run=dry_run, max_papers_per_query=max_papers_per_query
            )
        else:
            print("Skipping registering papers")

        result = self._rank(parameters)
        formatted_result = self._format_results(result, parameters)
        self._write_event(parameters, formatted_result, result)
        profile_name = config.get_current_audience().name.upper()

        pdf.create_pdf(
            data=formatted_result,
            output_path_description=f"recommender summary {profile_name} {parameters.by_topic if parameters.by_topic else ""} ",
        )

        self._send_email(
            formatted_result,
            f"Sota summary batch {parameters.batch} for profile {profile_name}",
        )

        return result

    def _write_event(self, parameters, formatted_result, result):
        papers_str = PapersInDataWharehouse().papers_to_urls_str(self._input_articles)
        ranking_data = RankGeneratedData(
            from_date=parameters.from_date,
            to_date=parameters.to_date,
            prompt="",
            summary=formatted_result,
            llm_result=result,
            papers_analysed=papers_str,
        )
        config.get_datawarehouse().write_event(
            "state_of_the_art_summary", ranking_data.to_dict()
        )

    def _rank(self, parameters: RecommenderParameters) -> str:

        if parameters.by_topic:
            return self._topic_search.search_by_topic(parameters.by_topic)

        if parameters.query:
            return self._topic_search.extract_query_and_search(parameters.query)

        if parameters.problem_description:
            import subprocess

            output = subprocess.getoutput("clipboard get_content")
            print("Clipboard content: ", output)
            return self.topic_search.extract_query_and_search(output)

        if not sys.stdin.isatty():
            print("Reading from stdin")
            stdindata = sys.stdin.readlines()
            stdindata = "\n".join(stdindata)
            return self._topic_search.extract_query_and_search(stdindata)

        self._input_articles = PapersInDataWharehouse().to_papers(
            PapersInDataWharehouse().get_latest_articles(
                lookback_days=parameters.lookback_days,
                from_date=parameters.from_date,
                batch=parameters.batch,
                batch_size=parameters.batch_size,
            )
        )

        result = PaperRanker().rank(articles=self._input_articles)

        return result

    def _format_results(self, result: str, parameters: RecommenderParameters):
        formatted_result = PapersFormatter().from_str(result)
        profile_name = config.get_current_audience().name

        query_str = f"Query: {parameters.query} \n" if parameters.query else ""
        topic_str = f"Topic: {parameters.by_topic} \n" if parameters.by_topic else ""
        from_date_str = (
            f"From date: {parameters.from_date} \n" if parameters.from_date else ""
        )

        now = datetime.now().isoformat()
        header = f"""Generated at {now} ({len(self._input_articles)}) papers analysed
Profile: "{profile_name}"  
{query_str}{topic_str}{from_date_str} 
"""
        formatted_result = header + formatted_result

        return formatted_result

    def _send_email(self, formatted_result, title):
        print("Sending email")
        if os.environ.get("LLM_MOCK") or os.environ.get("SOTA_TEST"):
            print("Mocking email")
        else:
            SotaMail().send(
                formatted_result,
                title,
            )

    def _load_papers_from_str(self, papers_str: str):
        urls = PapersUrlsExtractor().extract_urls(papers_str)
        return PapersInDataWharehouse().load_from_urls(urls, fail_on_missing_ids=False)

    def latest(self):
        return ReportsData().get_latest_summary()
