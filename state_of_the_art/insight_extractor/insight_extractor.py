import os
import json
from typing import Tuple

from state_of_the_art.config import config
from state_of_the_art.insight_extractor.insights_table import InsightsTable
from state_of_the_art.utils.clipboard import get_clipboard_content
from state_of_the_art.utils.mail import SotaMail
from state_of_the_art.utils import pdf
from state_of_the_art.insight_extractor.content_extractor import get_content_from_url
from openai import OpenAI


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """

    TABLE_NAME = "sota_paper_insight"

    def extract_from_url_in_clipboard(self):
        """
        loads the url frrom clipboard then calls the extract function
        """
        self.extract_from_url(get_clipboard_content())

    def extract_from_url(
        self, url: str, open_existing: bool = False, email_skip: bool = False
    ):
        """
        Generates insights for a given paper
        """

        url = self._clean_url(url)

        if open_existing and self._open_insight_summary_if_exists(url):
            return

        article_content, title, document_pdf_location = get_content_from_url(url)
        result, structured_result = StructuredPaperInsights().get_result(
            article_content
        )

        result = f"""Title: {title}
Abstract: {url}
{result}
        """

        if os.environ.get("SOTA_TEST"):
            return

        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {"abstract_url": url, "insights": result},
        )

        insights = self._convert_sturctured_output_to_insights(structured_result, url)
        self._write_insights_into_table(insights, url)

        paper_path = self._create_pdf(title, result, document_pdf_location)

        SotaMail().send("", f"Insights from {title}", paper_path)

    def _convert_sturctured_output_to_insights(self, structured_result, url):
        result = []
        for key, value in structured_result.items():
            if key == "top_insights":
                for insight in value:
                    result.append(('top_insights', insight))
                continue

            if key in ["institutions", "published_date", "published_where"]:
                continue

            if isinstance(value, str):
                result.append((key, value))
            else:
                for insight_row in value:
                    result.append((key, insight_row))
        
        return result

    def _write_insights_into_table(self, insights, url):
        insights_table = InsightsTable()
        for (question, insight) in insights:
            insights_table.add_insight(insight, question, url, None)

    def _create_pdf(self, title, result, document_pdf_location):
        pdf.create_pdf(
            data=result, output_path="/tmp/current_paper.pdf", disable_open=True
        )
        paper_path = pdf.create_pdf_path("p " + title)
        print("Saving paper insights to ", paper_path)
        pdf.merge_pdfs(paper_path, ["/tmp/current_paper.pdf", document_pdf_location])
        return paper_path

    def _open_insight_summary_if_exists(self, abstract_url) -> bool:
        df = config.get_datawarehouse().event(self.TABLE_NAME)
        filtered = df[(df["abstract_url"] == abstract_url) & ~(df["pdf_path"].isnull())]
        if filtered.empty:
            return False

        path = filtered["pdf_path"].values[0]
        if not os.path.exists(path):
            print("File not found: ", path)
            return False
        print("Paper insights path: ", path)
        pdf.open_pdf(path)
        print("Paper already processed")
        return True

    def _clean_url(self, url):
        print("Given url: ", url)
        url = url.strip()
        url = url.replace("file://", "")
        return url


class StructuredPaperInsights:
    def __init__(self):
        self.profile = config.get_current_audience()
        self.QUESTIONS: dict[str, str] = self.profile.paper_questions
        self.profile = config.get_current_audience()

    def get_result(self, text: str) -> Tuple[str, dict]:
        if os.environ.get("SOTA_TEST"):
            return "Mocked result", {}

        client = OpenAI(api_key=config.OPEN_API_KEY)
        result = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": text}],
            functions=[
                {
                    "name": "get_insights_from_paper",
                    "description": f"""This function returns expert data science insights that ecompasses the knwoeldge of all world top scientists.
It returns the most insightful and actionable information from the given paper content
The written style is in richard feyman style of explanations
It optimized the answers for the following audience: {self.profile.get_preferences()[0:300]}
""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "institutions": {
                                "type": "string",
                                "description": "the insitutions that published the paper",
                            },
                            "published_date": {
                                "type": "string",
                                "description": "when the paper was published?",
                            },
                            "published_where": {
                                "type": "string",
                                "description": "where paper was published?",
                            },
                            "top_insights": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 3,
                                "maxItems": 5,
                                "description": """returns most valuable insights from the paper 
                                The insights cover well which problem they are trying to solve.
                                """,
                            },
                            "going_deep": {
                                "type": "string",
                                "description": "return a summary on explaining in an clear way the core of the paper",
                            },
                            "core_terms_defintion": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 4,
                                "description": "define core terms in the paper use analogies if needed when they are very complex",
                            },
                            "strenghs_from_paper": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 3,
                                "description": "what are particular strenghts of this paper that make them stand out in relation to others in similar field?",
                            },
                            "weakeness_from_paper": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "description": "what are particular weakenessess of this paper that make it less useful?",
                            },
                            "top_recommended_actions": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 3,
                                "description": "what are actionable recommendations from this paper?",
                            },
                            "external_resoruces_recommendations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 3,
                                "description": """returns further resources recommendations from the board of experts if somebody whants to go deep into it.
                                Books, articles, papers or people to follow related to the topic that helps to get a deeper understanding of it.""",
                            },
                        },
                    },
                }
            ],
            function_call="auto",
        )

        if not hasattr(result.choices[0].message, "function_call"):
            raise Exception(
                f"""Function call extraction operation failed returned {result.choices[0].message.content} instead """
            )

        structured_results = result.choices[0].message.function_call.arguments
        structured_results = json.loads(str(structured_results))
        return json.dumps(structured_results, indent=3), structured_results
