from state_of_the_art.paper.papers import PapersData
from state_of_the_art.paper.text_extractor import PapersUrlsExtractor
from state_of_the_art.report.reports_data import ReportsData


class TopReports():
    def get_top_papers_from_summary(self, extractions=3, top_n=60, ):

        papers = []
        for i in range(-1,-(extractions+1),-1):
            try:
                summary = ReportsData().get_latest_summary(i)
                extracted_papers = PapersUrlsExtractor().extract_urls(summary)[0:top_n]
            except:  # catch the exception
                print(" Extraction error ")
                continue


            papers = papers + extracted_papers

        papersData = PapersData()

        return papersData.print_papers(papersData.load_from_urls(papers))
