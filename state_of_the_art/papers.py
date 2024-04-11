import os
from typing import List

from state_of_the_art.paper import Paper
from tiny_data_wharehouse.data_wharehouse import DataWharehouse
import pandas as pd
import datetime

class PapersData():
    TITLE_MAX_LENGH = 80
    def display(self):
        """
        Entrypoint to display papers. We add options to this function to change the display logic 
        Rather than introducing more functions.
        """
        self.print_from_most_recent()

    def load_papers(self):
        tdw = DataWharehouse()
        df = tdw.event('arxiv_papers')
        return df

    def load_between_dates(self, start, end):
        df = self.load_papers()
        print("Date filters (from, to): ", start, end)
        return df[(df['published'].dt.strftime('%Y-%m-%d') >= start) & (df['published'].dt.strftime('%Y-%m-%d') <= end)].sort_values(by='published', ascending=False)

    def load_since_last_summary_execution(self):
        from state_of_the_art.summaries import SummariesData
        latest_date = SummariesData().get_latest_date_covered_by_summary()
        print("Latest date covered by summary: ", latest_date)
        today =  datetime.date.today().isoformat()
        papers = self.load_between_dates(latest_date, today)

        self.print_papers(papers)

    def papers_schema(self):
        return list(self.load_papers().columns)
    
    def load_from_url(self, url):
        papers = self.load_papers()
        return papers[papers['url'] == url].to_string()

    def load_from_urls(self, urls):
        papers = self.load_papers()
        result = papers[papers['url'].isin(urls)]

        print("Found ", len(result), " papers")
        return result

    def print_from_most_recent(self, from_date=None, to_date=None) -> pd.DataFrame:

        if from_date and to_date:
            papers = self.load_between_dates(from_date, to_date)
        else:
            papers = self.load_papers()

        self.print_papers(self.sort_by_recently_published(papers))

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
    
    def sort_by_recently_published(self, df):
        return df.sort_values(by='published', ascending=False)

    def load_papers_between_published_dates(self, start, end) -> pd.DataFrame:
        df = self.load_papers()
        return self.sort_by_recently_published(df[(df['published'].dt.strftime('%Y-%m-%d') >= start) & (df['published'].dt.strftime('%Y-%m-%d') <= end)])

    def load_latest_n_days(self, look_back_days=10):
        from_date = (datetime.date.today() - datetime.timedelta(days=look_back_days)).isoformat()
        to_date = datetime.date.today().isoformat()

        return self.load_papers_between_published_dates(from_date, to_date)

class PapersFormatter():
    """
    Used to oncode papers as prompts
    """

    def papers_urls(self, papers: List[Paper]) -> str:
        urls = ""
        for i in papers:
            urls += i.url + '\n'
        return urls

class PapersComparer():
    def extract_papers_urls(self, data) -> str:
        urls = []
        for row in data.split('\n'):
            for k, _  in enumerate(row):
                if row[k] == 'h' and row[k + 1] == 't' and row[k + 2] == 't' and row[k + 3] == 'p':

                    url_char = row[k]
                    url = ''
                    internal_k = k
                    while url_char != ' ' and url_char != '\n' and internal_k<len(row):
                        url_char = row[internal_k]
                        url += url_char
                        internal_k = internal_k+1

                    urls.append(url)
                    
                    continue
        return urls

    def overlap_size(self, papers_a, papers_b):
        overlap_size = 0 
        for paper in papers_a:
            if paper in papers_b:
                overlap_size = overlap_size + 1
            
        total = len(papers_a) + len(papers_b)

        return (2* overlap_size) / total
        
        


class BrowserPapers:
    def fzf(self):
        outoput = os.system('sota papers | /Users/jean.machado/.fzf/bin/fzf --layout=reverse  | sota browser_papers open_from_fzf')
        print(outoput)

    def open_from_fzf(self):
        import sys
        text = sys.stdin.readlines()[0]
        paper_url = text.split(' ')[-2].strip()
        print('"', paper_url,'"')
        print('Opening paper: ', paper_url)
        os.system(f"clipboard set_content {paper_url}")
        Paper(arxiv_url=paper_url).download_and_open()


