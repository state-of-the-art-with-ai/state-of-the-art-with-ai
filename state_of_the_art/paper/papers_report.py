from datetime import datetime

from state_of_the_art.paper.format_papers import PapersFormatter
from state_of_the_art.paper.papers_data import PapersDataLoader
from state_of_the_art.utils import pdf


class PapersReport:
    def generate(self, from_date):
        papers = PapersDataLoader().load_papers_between_published_dates(
            from_date, datetime.now().strftime("%Y-%m-%d")
        )
        urls = papers["url"].tolist()
        urls = " ".join(urls)
        formatted_result = PapersFormatter().from_str(urls)
        formatted_result = (
            "Total papers: "
            + str(len(papers))
            + "\nFrom Date: "
            + from_date
            + "\ "
            + formatted_result
        )

        pdf.create_pdf(
            data=formatted_result,
            output_path_description=f"all papers in period from {from_date}",
        )
