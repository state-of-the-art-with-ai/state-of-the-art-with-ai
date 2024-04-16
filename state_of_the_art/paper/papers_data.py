from typing import List, Optional

from state_of_the_art.paper.paper import Paper
from tiny_data_wharehouse.data_wharehouse import DataWharehouse
import pandas as pd
import datetime
from state_of_the_art.config import config

class PapersData():
    TITLE_MAX_LENGH = 80
    def display(self, from_date=None, n=None):
        """
        Entrypoint to display papers. We add options to this function to change the display logic 
        Rather than introducing more functions.
        """
        to_date = datetime.date.today().isoformat()

        if from_date and to_date:
            papers = self.load_between_dates(from_date, to_date)
        else:
            papers = self.load_papers()

        papers = self.sort_by_recently_published(papers)
        if n:
            papers = papers.head(n)

        self.print_papers(papers)

    def get_latest_articles(self, from_date: Optional[str]=None, to_date: Optional[str]=None, lookback_days=None, article_slices=None, batch=1):
        if not from_date and not lookback_days:
            lookback_days = config.DEFAULT_LOOK_BACK_DAYS

        max_papers = config.RANK_MAX_PAPERS_TO_COMPUTE
        if not article_slices:
            article_slices = (max_papers * (batch - 1), max_papers * batch)

        print("Look back days ", lookback_days)
        print("Article slices ", article_slices)

        from_date = from_date if from_date else (datetime.date.today() - datetime.timedelta(days=lookback_days)).isoformat()
        to_date = to_date if to_date else datetime.date.today().isoformat()

        articles = self.load_between_dates(from_date, to_date)
        amount_of_articles = len(articles)
        print("Found  ", amount_of_articles, f" articles with date filters but filtering down to {max_papers} ")

        if amount_of_articles < max_papers:
            article_slices = (0, amount_of_articles)
        print("Slicing articles ", article_slices)

        articles = articles[article_slices[0]:article_slices[1]]

        return articles
    def load_papers(self):
        tdw = DataWharehouse()
        df = tdw.event('arxiv_papers')
        return df


    def get_all_papers(self) -> List[Paper]:
        df = self.load_papers()
        return self.to_papers(df)


    def to_papers(self, df) -> List[Paper]:
        papers = []
        for i in df.iterrows():
            paper = Paper(title=i[1]['title'], abstract=i[1]['abstract'], arxiv_url=i[1]['url'], published=i[1]['published'])
            papers.append(paper)
        return papers

    def load_between_dates(self, start, end):
        df = self.load_papers()
        print("Date filters (from, to): ", start, end)
        return df[(df['published'].dt.strftime('%Y-%m-%d') >= start) & (df['published'].dt.strftime('%Y-%m-%d') <= end)].sort_values(by='published', ascending=False)

    def load_since_last_summary_execution(self):
        from state_of_the_art.summaries import SummariesData
        latest_date = SummariesData().get_latest_date_covered_by_summary()
        print("Latest date covered by summary: ", latest_date)
        today = datetime.date.today().isoformat()
        papers = self.load_between_dates(latest_date, today)

        self.print_papers(papers)

    def papers_schema(self):
        return list(self.load_papers().columns)
    
    def load_from_url(self, url) -> Optional[pd.DataFrame]:
        papers = self.load_papers()
        result = papers[papers['url'] == url]

        if result.empty:
            return None

        return result

    def load_from_urls(self, urls):
        urls = list(set(urls))
        papers = self.load_papers()
        result = papers[papers['url'].isin(urls)]

        if len(result) != len(urls):
            raise Exception(f"Found {len(result)} papers but expected {len(urls)}")

        return result


    def df_to_papers(self, papers_df) -> List[Paper]:
        papers_dict = papers_df.to_dict(orient='records')
        result = []
        for i in papers_dict:
            paper = Paper(title=i['title'], abstract=i['abstract'], arxiv_url=i['url'], published=i['published'])
            result.append(paper)
        return result

    def print_papers(self, papers_df,  show_abstract=False):
        papers_dict = papers_df.to_dict(orient='records')
        for i in papers_dict:
            abstract = ''
            if show_abstract:
                abstract = i['abstract']
            print(str(i['published'])[0:10],' ', i['title'][0:self.TITLE_MAX_LENGH], ' ', i['url'], abstract)


        print("Total papers: ", len(papers_dict))
    
    def sort_by_recently_published(self, df):
        return df.sort_values(by='published', ascending=False)

    def load_papers_between_published_dates(self, start, end) -> pd.DataFrame:
        df = self.load_papers()
        return self.sort_by_recently_published(df[(df['published'].dt.strftime('%Y-%m-%d') >= start) & (df['published'].dt.strftime('%Y-%m-%d') <= end)])

    def load_latest_n_days(self, look_back_days=10):
        from_date = (datetime.date.today() - datetime.timedelta(days=look_back_days)).isoformat()
        to_date = datetime.date.today().isoformat()

        return self.load_papers_between_published_dates(from_date, to_date)

    def papers_to_urls_str(self, papers: List[Paper]) -> str:
        urls = ""
        for i in papers:
            urls += i.url + '\n'
        return urls

