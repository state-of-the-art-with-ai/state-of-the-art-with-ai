import os

from state_of_the_art.config import config
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
        import subprocess

        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        self.extract_from_url(url)

    def extract_from_url(self, url: str, open_existing=True, email_skip=False):
        """
        Generates insights for a given paper
        """

        url = self._clean_url(url)

        if open_existing and self._open_insight_summary_if_exists(url):
            return

        article_content, title, document_pdf_location = get_content_from_url(url)
        result = InsigthStructured().get_result(article_content)

        result = f"""Title: {title}
Abstract: {url}
{result}
        """

        pdf.create_pdf(
            data=result, output_path="/tmp/current_paper.pdf", disable_open=True
        )
        paper_path = pdf.create_pdf_path("p " + title)
        print("Saving paper insights to ", paper_path)
        pdf.merge_pdfs(paper_path, ["/tmp/current_paper.pdf", document_pdf_location])

        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {"abstract_url": url, "insights": result, "pdf_path": paper_path},
        )

        if os.environ.get("SOTA_TEST") or email_skip:
            print("Skipping email")
        else:
            SotaMail().send("", f"Insights from {title}", paper_path)

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


class BasePrompt:
    def __init__(self):
        self.profile = config.get_current_audience()
        self.QUESTIONS: dict[str, str] = self.profile.paper_questions
        self.profile = config.get_current_audience()


class InsigthStructured(BasePrompt):
    def __init__(self):
        super().__init__()

    def get_result(self, text: str) -> str:
        if os.environ.get("SOTA_TEST"):
            return "Mocked result"

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
                                "description": """returns most valuable insights from the paper max 3 sentences per insight
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
                                Books, articles, papers or people to follow related to the topic that helps to get a deeper understanding of it.
                                """,
                            },
                        },
                    },
                }
            ],
            function_call="auto",
        )
        result = str(result.choices[0].message.function_call.arguments)
        import json

        print("Result", result)
        return json.dumps(json.loads(result), indent=4)
