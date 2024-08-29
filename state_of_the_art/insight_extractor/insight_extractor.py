from enum import Enum
import os
import json
from typing import Optional, Tuple

from state_of_the_art.config import config
from state_of_the_art.insight_extractor.insights_table import InsightsTable
from state_of_the_art.paper.questions_table import QuestionsTable
from state_of_the_art.utils.clipboard import get_clipboard_content
from state_of_the_art.utils.mail import SotaMail
from state_of_the_art.utils import pdf
from state_of_the_art.insight_extractor.content_extractor import get_content_from_url
from openai import OpenAI


class SupportedModels(Enum):
    gpt_4o_mini = "gpt-4o-mini"
    gpt_4o = "gpt-4o"


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """

    TABLE_NAME = "sota_paper_insight"

    def extract_from_url_in_clipboard(self):
        """
        loads the url frrom clipboard then calls the extract function
        """
        self.extract_insights_from_paper_url(get_clipboard_content())

    def extract_insights_from_paper_url(
        self,
        url: str,
        open_existing: bool = False,
        email_skip: bool = False,
        disable_pdf_open=False,
        question=None,
        model_to_use=SupportedModels.gpt_4o.value,
    ):
        """
        Generates insights for a given paper
        """

        url = self._clean_url(url)

        if open_existing and self._open_insight_summary_if_exists(url):
            return

        article_content, title, document_pdf_location = get_content_from_url(url)
        result, structured_result = StructuredPaperInsights(
            model_to_use=model_to_use
        ).get_result(article_content, question=question)

        result = f"""Title: {title}
Abstract: {url}
{result}
        """
        self.post_extraction(
            result,
            structured_result,
            document_pdf_location,
            url,
            title,
            email_skip,
            disable_pdf_open,
        )

    def post_extraction(
        self,
        result,
        structured_result,
        document_pdf_location: str,
        url,
        title,
        email_skip=False,
        disable_pdf_open=False,
    ):
        if os.environ.get("SOTA_TEST"):
            return

        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {
                "abstract_url": url,
                "insights": result,
                "pdf_path": document_pdf_location,
            },
        )

        insights = self._convert_sturctured_output_to_insights(structured_result, url)
        self._write_insights_into_table(insights, url)

        paper_path = self._create_pdf(
            title, result, document_pdf_location, disable_pdf_open=disable_pdf_open
        )
        if not email_skip:
            SotaMail().send("", f"Insights from {title}", paper_path)

    def _convert_sturctured_output_to_insights(self, structured_result, url):
        result = []
        for key, value in structured_result.items():
            if key == "top_insights":
                for insight in value:
                    result.append(("top_insights", insight))
                continue

            if isinstance(value, str):
                result.append((key, value))
            else:
                for insight_row in value:
                    result.append((key, insight_row))

        return result

    def _write_insights_into_table(self, insights, url):
        # reverse order of insights
        insights.reverse()

        insights_table = InsightsTable()
        for question, insight in insights:
            insights_table.add_insight(insight, question, url, None)

    def _create_pdf(self, title, result, document_pdf_location, disable_pdf_open=False):
        pdf.create_pdf(
            data=result, output_path="/tmp/current_paper.pdf", disable_open=True
        )
        paper_path = pdf.create_pdf_path("p " + title)
        print("Saving paper insights to ", paper_path)
        pdf.merge_pdfs(
            paper_path,
            ["/tmp/current_paper.pdf", document_pdf_location],
            disable_open=disable_pdf_open,
        )
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
    def __init__(self, model_to_use: Optional[str] = None):
        self.profile = config.get_current_audience()
        self.QUESTIONS: dict[str, str] = self.profile.paper_questions
        self.profile = config.get_current_audience()
        self.model_to_use = model_to_use

    def get_result(self, text: str, question=None) -> Tuple[str, dict]:
        if os.environ.get("SOTA_TEST"):
            return "Mocked result", {}

        if question:
            print(f"Using question to extract insights ({question})")
            parameters = {question: {"type": "string", "description": question}}
        else:
            questions = QuestionsTable().read()
            parameters = convert_questions_to_openai_call(questions)

        client = OpenAI(api_key=config.OPEN_API_KEY)
        used_model = (
            self.model_to_use if self.model_to_use else SupportedModels.gpt_4o.value
        )
        print("Using model: ", used_model)
        result = client.chat.completions.create(
            model=used_model,
            messages=[{"role": "user", "content": text}],
            functions=[
                {
                    "name": "get_insights_from_paper",
                    "description": f"""This function returns expert data science insights that ecompasses the knwoeldge of all world top scientists.
It returns the most insightful and actionable information from the given paper content
The written style is in richard feyman style of explanations
It optimized the answers for the following audience: {self.profile.get_preferences()[0:300]}
""",
                    "parameters": {"type": "object", "properties": parameters},
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


def convert_questions_to_openai_call(data):
    result = {}
    for i, row in data.iterrows():
        data = {"type": "string", "description": row["question"]}
        if row["min_items"] or row["max_items"]:
            data = {
                "type": "array",
                "items": {"type": "string"},
                "description": row["question"],
            }

            if row["min_items"]:
                data["minItems"] = int(row["min_items"])

            if row["max_items"]:
                data["maxItems"] = int(row["max_items"])

        result[row["short_version"]] = data
    return result
