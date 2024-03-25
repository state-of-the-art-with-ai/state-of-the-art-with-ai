from tiny_data_wharehouse.data_wharehouse import DataWharehouse
from state_of_the_art.papers import PapersComparer, PapersData

class SummariesData():
    def get_latest_summary(self, index=-1):
        tdw = DataWharehouse()
        df = tdw.event('state_of_the_art_summary')
        return df['summary'].to_list()[index]


class TopSummaries():
    def get_top_papers_from_summary(self, extractions= 5, top_n=50, ):

        papers = []
        for i in range(-1,-(extractions+1),-1):
            try:
                extracted_papers = PapersComparer().extract_papers_urls(SummariesData().get_latest_summary(i))[0:top_n]
            except:  # catch the exception
                print(" Extraction error ")
                continue

            
            papers = papers + extracted_papers
        
        papersData = PapersData()

        return papersData.print_papers(papersData.load_from_urls(papers))
