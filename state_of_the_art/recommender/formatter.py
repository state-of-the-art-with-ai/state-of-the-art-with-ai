from state_of_the_art.paper.text_extractor import PapersUrlsExtractor
from state_of_the_art.recommender.reports_data import ReportsData


class SummaryFormatter:

    def format_latest_summary(self):
        return self.format(ReportsData().get_latest_summary())
    def format(self, base_summary):
        urls = PapersUrlsExtractor().extract_urls(base_summary)
        result = ""

        for url in urls:
            result+= f"""
            Url: {url}
            """
        
        return result

if __name__ == "__main__":
    import fire
    fire.Fire()