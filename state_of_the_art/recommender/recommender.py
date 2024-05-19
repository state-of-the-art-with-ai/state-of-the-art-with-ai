import os
import sys
from typing import Optional, List

from datetime import datetime
from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.paper import ArxivPaper
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.paper.url_extractor import PapersUrlsExtractor
from state_of_the_art.recommender.ranker.rank_data import RankGeneratedData
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.recommender.ranker.ranker import PaperRanker
from state_of_the_art.recommender.report_parameters import RecommenderContext
from state_of_the_art.config import config

from state_of_the_art.recommender.topic_based.topic_search import TopicSearch
from state_of_the_art.utils import pdf
from state_of_the_art.utils.mail import SotaMail


class Recommender:
    """
    Class responsible to the entire generation pipeline
    """

    TABLE_NAME = "state_of_the_art_summary"
    _input_articles: Optional[List[ArxivPaper]] = None
    _topic_search: Optional[TopicSearch] = None

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
        number_of_recommendations=None,
    ):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """

        context = RecommenderContext(
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
            number_of_papers_to_recommend=number_of_recommendations,
        )

        if not skip_register:
            ArxivMiner().register_new(
                dry_run=dry_run, max_papers_per_query=max_papers_per_query
            )
        else:
            print("Skipping registering papers")

        result = self._rank(context)
        formatted_result = self._format_results(result, context)
        profile_name = config.get_current_audience().name.upper()

        location = pdf.create_pdf(
            data=formatted_result,
            output_path_description=f"recommender summary {profile_name} {context.by_topic if context.by_topic else ""} ",
        )
        context.generated_pdf_location = location

        self._write_event(context, formatted_result, result)

        self._send_email(
            formatted_result,
            f"Sota summary batch {context.batch} for profile {profile_name}",
        )

        return result

    def open_latest(self):
        """
        Open the latest generated summary
        """
        df = config.get_datawarehouse().event(self.TABLE_NAME)
        dict = df.iloc[-1].to_dict()

        if dict["pdf_location"]:
            pdf.open_pdf(dict["pdf_location"])
        else:
            print("No pdf path found")

    def _get_topic_search(self) -> TopicSearch:
        if not self._topic_search:
            self._topic_search = TopicSearch()
            self._input_articles = self._topic_search._papers_list

        return self._topic_search

    def _rank(self, context: RecommenderContext) -> str:
        if context.by_topic:
            result, automated_query = self._get_topic_search().search_by_topic(
                context.by_topic,
                num_of_results=context.number_of_papers_to_recommend,
            )

            context.machine_generated_query = automated_query

            return result

        if context.query:
            return self._get_topic_search().search_with_query(context.query)

        if context.problem_description:
            import subprocess

            output = subprocess.getoutput("clipboard get_content")
            print("Clipboard content: ", output)
            context.machine_generated_query = self._get_topic_search().extract_query(
                output
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

        self._input_articles = PapersDataLoader().to_papers(
            PapersDataLoader().get_latest_articles(
                lookback_days=context.lookback_days,
                from_date=context.from_date,
                batch=context.batch,
                batch_size=context.batch_size,
            )
        )

        result = PaperRanker().rank(articles=self._input_articles)

        return result

    def _format_results(self, result: str, parameters: RecommenderContext):
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

        now = datetime.now().isoformat()
        header = f"""Generated at {now} ({len(self._input_articles)}) papers analysed
Profile: "{profile_name}"  
{query_str}{machine_query_str}{topic_str}{from_date_str}{number_of_papers}
"""
        formatted_ranked_result = header + formatted_ranked_result

        if self._input_articles:
            articles_as_input = PapersFormatter().from_papers(self._input_articles)
            formatted_ranked_result += f""" -----------------------------
Papers analysed: \n{articles_as_input}"""

        return formatted_ranked_result

    def _write_event(self, parameters, formatted_result, result):
        papers_str = PapersDataLoader().papers_to_urls_str(self._input_articles)
        ranking_data = RankGeneratedData(
            from_date=parameters.from_date,
            to_date=parameters.to_date,
            prompt="",
            summary=formatted_result,
            llm_result=result,
            papers_analysed=papers_str,
            pdf_location=parameters.generated_pdf_location,
        )
        if os.environ.get("SOTA_TEST"):
            print("Mocking event, not writing to datawarehouse")
            return

        config.get_datawarehouse().write_event(self.TABLE_NAME, ranking_data.to_dict())

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
        return PapersDataLoader().load_from_urls(urls, fail_on_missing_ids=False)
