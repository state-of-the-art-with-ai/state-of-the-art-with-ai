from typing import List, Optional, Union

from state_of_the_art.paper.paper import ArxivPaper
import pandas as pd
import datetime
from state_of_the_art.config import config


class PapersDataLoader:
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

        articles = self.load_between_dates(from_date, to_date)
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
        df.drop_duplicates(subset=["url"], keep="first", inplace=True)

        return df

    def get_all_papers(self) -> List[ArxivPaper]:
        df = self.load_papers()
        return self.to_papers(df)

    def to_papers(self, df) -> Union[List[ArxivPaper], dict[str, ArxivPaper]]:
        papers = []
        for i in df.iterrows():
            papers.append(ArxivPaper.load_from_dict(i[1].to_dict()))
        return papers

    def load_between_dates(self, start: str, end: str):
        df = self.load_papers()
        print("Date filters of publication (from, to): ", start, end)
        return df[
            (df["published"].dt.strftime("%Y-%m-%d") >= start)
            & (df["published"].dt.strftime("%Y-%m-%d") <= end)
        ].sort_values(by="published", ascending=False)

    def papers_schema(self):
        return list(self.load_papers().columns)

    def load_from_url(self, url) -> Optional[pd.DataFrame]:
        papers = self.load_papers()
        result = papers[papers["url"] == url]
        return result

    def load_from_urls(
        self, urls: List[str], as_dict=False, fail_on_missing_ids=True
    ) -> pd.DataFrame:
        urls = list(set(urls))
        papers = self.load_papers()
        if as_dict:
            result = {}
            for url in urls:
                result[url] = papers[papers["url"] == url]
            result_len = len(result.keys())
        else:
            result = papers[papers["url"].isin(urls)]
            result_len = len(result)

        if result_len != len(urls):
            message = f"""
                Found {len(result)} papers but expected {len(urls)}
                Missing urls: {[i for i in urls if i not in result['url'].to_list()]}
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
            result.append(ArxivPaper.load_from_dict(paper_dict))
        return result

    def load_paper_from_url(self, url: str) -> ArxivPaper:
        if not url:
            raise Exception("Url not defined to load any paper")

        result = self.load_papers_from_urls([url])
        if not result or len(result) == 0:
            raise Exception(f'Could not find paper from url {url}')

        return result[0]

    def df_to_papers(self, papers_df) -> List[ArxivPaper]:
        papers_dict = papers_df.to_dict(orient="records")
        result = []
        for i in papers_dict:
            paper = ArxivPaper(
                title=i["title"],
                abstract=i["abstract"],
                pdf_url=i["url"],
                published=i["published"],
            )
            result.append(paper)
        return result

    def print_papers(self, papers_df, show_abstract=False):
        papers_dict = papers_df.to_dict(orient="records")
        for i in papers_dict:
            abstract = ""
            if show_abstract:
                abstract = i["abstract"]
            print(
                str(i["published"])[0:10],
                " ",
                i["title"][0 : self.TITLE_MAX_LENGH],
                " ",
                i["url"],
                abstract,
            )

        print("Total papers: ", len(papers_dict))

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

    def load_latest_n_days(self, look_back_days=10):
        from_date = (
            datetime.date.today() - datetime.timedelta(days=look_back_days)
        ).isoformat()
        to_date = datetime.date.today().isoformat()

        return self.load_papers_between_published_dates(from_date, to_date)

    def papers_to_urls_str(self, papers: List[ArxivPaper]) -> str:
        urls = ""
        for i in papers:
            urls += i.abstract_url + "\n"
        return urls
