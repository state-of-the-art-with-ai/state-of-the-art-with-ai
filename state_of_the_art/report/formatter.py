from state_of_the_art.paper.text_extractor import PapersUrlsExtractor
from state_of_the_art.report.reports_data import ReportsData


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

class LLMSummaryFormatter:
    def format(self, source: str):
        """
        return keywords from project descriptions

        :return:
        """

        prompt = f"""Your task is to properly format a blog post to be pbulished form a unformatted source
return the articles as markdown links, find the best spacing arrangement psosssible between the articles. Mkae it very readable

blog post content starts###{{text}}
###content ends

formatted blogpost content starts###{{text}}
        """
        from state_of_the_art.llm import LLM
        result = LLM().call(prompt, source)
        return result

if __name__ == "__main__":
    import fire
    fire.Fire()