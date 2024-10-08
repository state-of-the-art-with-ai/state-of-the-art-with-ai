import os
from state_of_the_art.config import config
from state_of_the_art.insight_extractor.structured_insights import StructuredPaperInsights, SupportedModels
from state_of_the_art.tables.insights_table import InsightsTable
from state_of_the_art.utils.clipboard import get_clipboard_content
from state_of_the_art.utils.mail import EmailService
from state_of_the_art.utils import pdf
from state_of_the_art.insight_extractor.content_extractor import get_content_from_url


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """

    INSIGHTS_TABLE_NAME = "sota_paper_insight"

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

        try:
            article_content, title, document_pdf_location = get_content_from_url(url)
        except Exception as e:
            raise e
            #raise Exception(f"Error while downloading paper: {e}")

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
            self.INSIGHTS_TABLE_NAME,
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
            EmailService().send("", f"Insights from {title}", paper_path)

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
        df = config.get_datawarehouse().event(self.INSIGHTS_TABLE_NAME)
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
