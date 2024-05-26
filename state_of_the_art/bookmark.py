from typing import Optional
from state_of_the_art.config import config
import datetime

from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.utils.mail import SotaMail
from state_of_the_art.paper.paper import ArxivPaper
from state_of_the_art.utils import pdf
import pandas as pd


class Bookmark:
    """
    Bookmarking papers for future reference
    """

    EVENT_NAME = "paper_bookmarks"

    def list(
        self, n=None, from_published_date: Optional[str] = None, abstract_included=False
    ):
        # convert str to date
        from_published_date = (
            datetime.datetime.strptime(from_published_date, "%Y-%m-%d").date()
            if from_published_date
            else None
        )

        dict = self.load_df(n=n).to_dict(orient="index")
        result = (
            "From published date: " + str(from_published_date) + "\n"
            if from_published_date
            else ""
        )
        result += "Bookmarks:\n\n"

        counter = 1
        for i in dict:
            paper_title = "Title not registered"
            published_str = ""
            paper_url = (
                ArxivPaper(url=dict[i]["paper_url"]).abstract_url
                if ArxivPaper.is_arxiv_url(dict[i]["paper_url"])
                else dict[i]["paper_url"]
            )
            comment = dict[i]["comment"]
            comment = comment.strip()
            comment_str = f"Comment: {comment}" if comment else ""

            abstract_str = ""
            try:
                paper = ArxivPaper.load_paper_from_url(
                    ArxivPaper._remove_versions_from_url(paper_url)
                )

                paper_title = paper.title
                published_str = f"Published: {paper.published_date_str()}"
                abstract_str = (
                    f"\nAbstract: {paper.abstract}" if abstract_included else ""
                )
                if from_published_date:
                    if paper.published.date() < from_published_date:
                        continue
            except Exception as e:
                print(f"Error: {e}")
            result += f"""{counter}. Title: {paper_title} 
{paper_url}
{comment_str}
Bookmarked: {str(dict[i]['bookmarked_date']).split(' ')[0]}
{published_str} {abstract_str[0:500]}

"""
            counter += 1

        pdf_location = pdf.create_pdf(data=result, output_path_description="Bookmarks")
        print(result)
        return pdf_location

    def add(self, paper_url, comment: Optional[str] = None):
        paper_url = paper_url.strip()

        if comment:
            comment = comment.strip()

        if not comment:
            comment = "registered interest"

        dwh = config.get_datawarehouse()
        dwh.write_event(
            self.EVENT_NAME,
            {
                "paper_url": paper_url,
                "comment": comment,
                "bookmarked_date": datetime.date.today().isoformat(),
            },
        )
        self.send_to_email()

    def register_url_from_clipboard(self):
        import subprocess

        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        self.add(url, "resigered interest")

    def add_interactive(self):
        print("Interactive collecting paper input")
        import subprocess

        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        url = url.strip()
        print("Url content: ", url)

        if not url.startswith("https://") and not url.startswith("http://"):
            raise Exception(f"Given clipboard content '{url}' is not a url!")

        comment = subprocess.check_output(
            "collect_input -n Comment", shell=True, text=True
        )

        self.add(url, comment)

    def _base_df(self):
        dwh = config.get_datawarehouse()
        return dwh.event(self.EVENT_NAME)

    def load_df(self, n=None) -> pd.DataFrame:
        df = self._base_df()

        df = (
            df.groupby("paper_url")
            .agg(
                {
                    "comment": " ".join,
                    "tdw_timestamp": "last",
                    "bookmarked_date": "last",
                }
            )
            .reset_index()
            .sort_values(by="tdw_timestamp", ascending=False)
        )

        if n:
            return df.head(n)

        return df

    def send_to_email(self):
        SotaMail().send(
            content="",
            subject="Bookmarks as of "
            + datetime.datetime.now().isoformat().split(".")[0],
            attachment=self.list(),
        )

    def register_bookmarks_papers(self):
        df = self.load_df()

        arxiv_miner = ArxivMiner()

        for i in df.index:
            paper_url = df.loc[i, "paper_url"]
            if ArxivPaper.is_arxiv_url(paper_url):
                paper = ArxivPaper(url=paper_url)
                arxiv_miner.register_paper_if_not_registered(paper)
