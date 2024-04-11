
from state_of_the_art.config import config
import sys
from state_of_the_art.llm import calculate_cost, call_chatgpt
from state_of_the_art.paper import Paper


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """
    def extract(self, url: str, question_topic):

        local_location = Paper(arxiv_url=url).download()

        from pypdf import PdfReader

        reader = PdfReader(local_location)
        number_of_pages = len(reader.pages)
        PAPER_CONTENT = ""
        for page in reader.pages:
            PAPER_CONTENT += page.extract_text()

        print(PAPER_CONTENT)

        print("Number of pages: ", number_of_pages)
        print("Number of characters: ", len(PAPER_CONTENT))
        print("Number of tokens: ", len(PAPER_CONTENT)/4)
        cost = calculate_cost(chars_input=len(PAPER_CONTENT), chars_output=4000)

        user_input = input(f"Do you want ton continue to generate insights at a cost of $ {cost}? Type c to continue \n")
        profile = config.get_current_audience()
        if user_input != 'c':
            print("Aborting")
            sys.exit(1)

        prompt = f"""You are an world class expert in Data Science and computer science.
Your task is answering questions about a paper as they are asked to you.
You Optimize your suggestions to the following audience: {profile.get_preferences()}

Article now starts: ##start
{{text}}
## end of article to extract insights

{profile.paper_tasks[question_topic]}
start of answer ##start
"""


        result = call_chatgpt(prompt, PAPER_CONTENT)

        print(result)

        from tiny_data_wharehouse.data_wharehouse import DataWharehouse
        tdw = DataWharehouse()
        tdw.write_event('sota_paper_insight', {'pdf_url': url, 'insights': result, 'prompt': prompt})
