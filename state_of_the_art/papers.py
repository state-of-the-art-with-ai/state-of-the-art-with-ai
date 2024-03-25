
from tiny_data_wharehouse.data_wharehouse import DataWharehouse
import pandas as pd
import datetime

class PapersData():

    def load_papers(self):
        tdw = DataWharehouse()
        df = tdw.event('arxiv_papers')

        return df

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

    def load_from_most_recent(self) -> pd.DataFrame:
        return self.sort_by_recently_published(self.load_papers())
    
    def print_all_papers(self):
        papers = self.load_from_most_recent()

        self.print_papers(papers)


    def print_papers(self, papers_df):
        papers_dict = papers_df.to_dict(orient='records')
        for i in papers_dict:
            print(i['title'], ' ', str(i['published'])[0:10], ' ', i['url'])

    
    def sort_by_recently_published(self, df):
        return df.sort_values(by='published', ascending=False)

    def load_papers_between_published_dates(self, start, end) -> pd.DataFrame:
        df = self.load_papers()
        return self.sort_by_recently_published(df[(df['published'].dt.strftime('%Y-%m-%d') >= start) & (df['published'].dt.strftime('%Y-%m-%d') <= end)])

    def load_latest_n_days(self, look_back_days=10):
        from_date = (datetime.date.today() - datetime.timedelta(days=look_back_days)).isoformat()
        to_date = datetime.date.today().isoformat()

        return self.load_papers_between_published_dates(from_date, to_date)

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
        
        

