from typing import Optional
from state_of_the_art.config import config
import datetime

from state_of_the_art.utils.mail import Mail
from state_of_the_art.paper.paper import Paper
import pandas as pd


class Bookmark:
    """
    Bookmarking papers for future reference
    """

    EVENT_NAME = "paper_bookmarks"

    def add(self, paper_url, comment: Optional[str] = None):
        paper_url = paper_url.strip()

        if comment:
            comment = comment.strip()

        if not comment:
            comment = "registered interest"

        print(f"Registering paper {paper_url} in bookmarks")
        if Paper.is_arxiv_url(paper_url):
            Paper.register_from_url(paper_url)

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

        self.list(n=10)

    def add_interactive(self):
        print("Interactive collecting paper input")
        import subprocess

        url = subprocess.check_output("collect_input -n Url -p", shell=True, text=True)
        comment = subprocess.check_output(
            "collect_input -n Comment", shell=True, text=True
        )

        self.add(url, comment)

    def _base_df(self):
        dwh = config.get_datawarehouse()
        return dwh.event(self.EVENT_NAME)

    def load_df(self, n=None) -> pd.DataFrame:
        df = self._base_df()

        # join duplicates
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

    def list(self, n=5):
        print(self.prepare_list(n=n))

    def prepare_list(self, n=None):
        dict = self.load_df(n=n).to_dict(orient="index")
        result = "Bookmarks: \n\n"
        counter = 1
        for i in dict:
            paper_title = "Title not found"
            published_str = ""
            paper_url = dict[i]["paper_url"]
            comment = dict[i]["comment"]
            comment = comment.strip()
            comment_str = f"\n Comment: {comment}" if comment else ""

            if Paper.is_arxiv_url(paper_url):
                paper_url = Paper.convert_pdf_to_abstract(paper_url)

            abstract_str = ""
            try:
                paper = Paper.load_paper_from_url(paper_url)
                paper_title = paper.title
                published_str = f"Published: {paper.published_date_str()}"
                abstract_str = f"\nAbstract: {paper.abstract}"
            except Exception as e:
                pass
            result += f"""{counter}. Title: {paper_title} 
{paper_url} {comment_str}
Bookmarked: {str(dict[i]['bookmarked_date']).split(' ')[0]}
{published_str} {abstract_str[0:500]}
\n
"""
            counter += 1

        return result

    def send_to_email(self):
        Mail().send(
            self.prepare_list(),
            "Bookmarks as of " + datetime.datetime.now().isoformat().split(".")[0],
        )
