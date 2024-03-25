from tiny_data_wharehouse.data_wharehouse import DataWharehouse
from state_of_the_art.papers import PapersComparer, PapersData

class SummariesData():

    def get_summary(self):
        tdw = DataWharehouse()
        return tdw.event('state_of_the_art_summary')
    def get_latest_summary(self, index=-1):
        return self.get_summary()['summary'].to_list()[index]

    def get_latest_date_covered_by_summary(self):
        return self.get_summary().sort_values(by='to_date', ascending=False).head(1).to_dict()['to_date'][0]


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
