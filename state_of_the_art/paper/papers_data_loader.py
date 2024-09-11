from typing import List, Optional, Union

from state_of_the_art.paper.arxiv_paper import ArxivPaper
import pandas as pd
import datetime
from state_of_the_art.config import config
from state_of_the_art.paper.paper_entity import Paper


class PapersLoader:
    TITLE_MAX_LENGH = 80

    def get_latest_articles(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        lookback_days=None,
        article_slices=None,
        batch=1,
        batch_size=100,
    ) -> pd.DataFrame:
        if not from_date and not lookback_days:
            lookback_days = config.DEFAULT_LOOK_BACK_DAYS

        max_papers = batch_size
        if not article_slices:
            article_slices = (max_papers * (batch - 1), max_papers * batch)
        print("Look back days ", lookback_days)

        from_date = (
            from_date
            if from_date
            else (datetime.date.today() - datetime.timedelta(days=lookback_days))
        ).isoformat()
        to_date = to_date if to_date else datetime.date.today().isoformat()

        articles = self.load_between_dates_str(from_date, to_date)
        amount_of_articles = len(articles)
        print(
            "Found  ",
            amount_of_articles,
            f" articles with date filters but filtering down to {max_papers} ",
        )

        if amount_of_articles < max_papers:
            article_slices = (0, amount_of_articles)
        print("Slicing articles ", article_slices)

        articles = articles[article_slices[0] : article_slices[1]]

        return articles

    def load_papers(self):
        df = config.get_datawarehouse().event("arxiv_papers")
        # @todo Fix duplicates
        df.drop_duplicates(subset=["abstract_url"], keep="first", inplace=True)

        return df

    def get_all_papers(self) -> List[ArxivPaper]:
        df = self.load_papers().sort_values(by="published", ascending=False)
        return self.to_papers(df)

    def to_papers(self, df) -> Union[List[ArxivPaper], dict[str, ArxivPaper]]:
        papers = []
        for i in df.iterrows():
            try:
                papers.append(ArxivPaper.load_from_dict(i[1].to_dict()))
            except Exception:
                pass

        return papers

    def load_between_dates_str(self, start: str, end: str):
        df = self.load_papers()
        print("Date filters of publication (from, to): ", start, end)
        return df[
            (df["published"].dt.strftime("%Y-%m-%d") >= start)
            & (df["published"].dt.strftime("%Y-%m-%d") <= end)
        ].sort_values(by="published", ascending=False)

    def load_between_dates(self, start: datetime.date, end: datetime.date):
        df = self.load_papers()
        return df[
            (df["published"].dt.date >= start) & (df["published"].dt.date <= end)
        ].sort_values(by="published", ascending=False)

    def load_from_url(self, url) -> Optional[pd.DataFrame]:
        papers = self.load_papers()
        result = papers[papers["abstract_url"] == url]
        return result

    def load_from_partial_url(self, url) -> Optional[pd.DataFrame]:
        papers = self.load_papers()
        match = papers[papers["abstract_url"].str.contains(url)]

        print(f"While searching by partial url match found {match}")

        return match

    def load_from_urls(
        self, urls: List[str], as_dict=False, fail_on_missing_ids=True
    ) -> pd.DataFrame:
        urls = list(set(urls))
        papers = self.load_papers()
        if as_dict:
            result = {}
            for url in urls:
                result[url] = papers[papers["abstract_url"] == url]
            result_len = len(result.keys())
        else:
            result = papers[papers["abstract_url"].isin(urls)]
            result_len = len(result)

        if result_len != len(urls):
            message = f"""
                Found {len(result)} papers but expected {len(urls)}
                Missing urls: {[i for i in urls if i not in result['abstract_url'].to_list()]}
"""
            if fail_on_missing_ids:
                raise ValueError(message)
            else:
                print(message)

        return result

    def load_papers_from_urls(self, urls: List[str]) -> List[ArxivPaper]:
        papers = self.load_from_urls(urls, as_dict=True)
        result = []
        for i in urls:
            if not papers[i].to_dict(orient="records"):
                print("No data for ", i)
                continue

            paper_dict = papers[i].to_dict(orient="records")[0]
            if ArxivPaper.is_arxiv_url(paper_dict["abstract_url"]):
                entity = ArxivPaper.load_from_dict(paper_dict)
            else:
                entity = Paper(
                    pdf_url=paper_dict["abstract_url"], title=paper_dict["title"]
                )

            result.append(entity)
        return result

    def is_paper_url_registered(self, url: str) -> bool:
        try:
            self.load_from_partial_url(url)
            return True
        except BaseException as e:
            print("Could not find paper from url ", url, e)
            return False

    def load_paper_from_url(self, url: str) -> ArxivPaper:
        if not url:
            raise Exception("Url not defined to load any paper")

        result = self.load_from_partial_url(url)
        if result.empty:
            raise Exception(f"Could not find paper from url {url}")

        arxiv_data = result.to_dict(orient="records")[0]
        print("Arxiv data ", arxiv_data)
        if not ArxivPaper.is_arxiv_url(url):
            return Paper(pdf_url=arxiv_data["abstract_url"], title=arxiv_data["title"])

        result = ArxivPaper.load_from_dict(arxiv_data)
        if not result:
            raise Exception(f"Could not find paper from url {url}")

        return result

    def df_to_papers(self, papers_df) -> List[ArxivPaper]:
        """
        Converts a dataframe to papers
        """
        papers_dict = papers_df.to_dict(orient="records")
        result = []
        for i in papers_dict:
            try:
                paper = ArxivPaper(
                    title=i["title"],
                    abstract=i["abstract"],
                    abstract_url=i["abstract_url"],
                    published=i["published"],
                )
                result.append(paper)
            except Exception as e:
                print("Error converting to paper ", i, e)

        return result

    def sort_by_recently_published(self, df):
        return df.sort_values(by="published", ascending=False)

    def load_papers_between_published_dates(self, start, end) -> pd.DataFrame:
        df = self.load_papers()
        return self.sort_by_recently_published(
            df[
                (df["published"].dt.strftime("%Y-%m-%d") >= start)
                & (df["published"].dt.strftime("%Y-%m-%d") <= end)
            ]
        )

    def papers_to_urls_str(self, papers: List[ArxivPaper]) -> str:
        urls = ""
        for i in papers:
            urls += i.abstract_url + "\n"
        return urls
