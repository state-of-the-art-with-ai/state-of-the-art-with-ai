from tiny_data_wharehouse.data_wharehouse import DataWharehouse

from state_of_the_art.utils.mail import Mail
from state_of_the_art.paper_miner.arxiv import ArxivPaperMiner
from state_of_the_art.papers import PapersExtractor, PapersData
from state_of_the_art.ranker.paper_ranker import PaperRanker


class Report():
    def __init__(self):
        pass
    def generate(self, *, lookback_days=None, topic=None, from_date=None, skip_register=False, dry_run=False, batch=1):
        """
        The main entrypoint of the application does the entire cycle from registering papers to ranking them
        """
        if not skip_register:
            ArxivPaperMiner().register_papers(dry_run=dry_run)
        else:
            print("Skipping registering papers")

        result = PaperRanker().rank(lookback_days=lookback_days, from_date=from_date, batch=batch)


        Mail().send(result, f'Sota summary batch {batch}')
        return result

    def latest(self):
        return ReportsData().get_latest_summary()

class ReportsData():
    def get_summary(self):
        tdw = DataWharehouse()
        return tdw.event('state_of_the_art_summary')
    def schema(self):
        return self.get_summary().dtypes
    def get_latest_summary(self, as_json=False, as_dict=False):
        result = self.get_summary().iloc[-1]
        if as_json:
            return result.to_json()
        if as_dict:
            return result.to_dict()

        return result['summary']


    def get_latest_date_covered_by_summary(self):
        return self.get_summary().sort_values(by='to_date', ascending=False).head(1).to_dict()['to_date'][0]



class TopReports():
    def get_top_papers_from_summary(self, extractions=3, top_n=60, ):

        papers = []
        for i in range(-1,-(extractions+1),-1):
            try:
                summary = ReportsData().get_latest_summary(i)
                extracted_papers = PapersExtractor().extract_urls(summary)[0:top_n]
            except:  # catch the exception
                print(" Extraction error ")
                continue

            
            papers = papers + extracted_papers
        
        papersData = PapersData()

        return papersData.print_papers(papersData.load_from_urls(papers))
