
from state_of_the_art.config import config
import sys
from state_of_the_art.llm import calculate_cost, call_chatgpt, LLM
from state_of_the_art.paper import Paper


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """
    def __init__(self):
        self.profile = config.get_current_audience()

    def extract(self, url: str, question_topic=None):

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
        prompt = self._get_prompt(question_topic=question_topic)


        result = LLM().call(prompt, PAPER_CONTENT)

        print(result)

        from tiny_data_wharehouse.data_wharehouse import DataWharehouse
        tdw = DataWharehouse()
        tdw.write_event('sota_paper_insight', {'pdf_url': url, 'insights': result, 'prompt': prompt})
    def _get_prompt(self, question_topic=None) -> str:



        QUESTIONS = ""

        counter = 1
        for key, question in self.profile.paper_tasks.items():
            QUESTIONS+=f"""===
Question {counter}
{question}
==="""
            counter+=1

        if question_topic:
            QUESTIONS = self.profile.paper_tasks[question_topic]


        prompt = f"""You are an world class expert in Data Science and computer science.
Your job is answering questions about the paper given to you as they are asked
You Optimize your suggestions to the following audience: {self.profile.get_preferences()}

Article content starts starts ###start
{{text}}
### end of article content

Tasks now follow
tasks start###
{QUESTIONS}
### task ends

start of answers ###start
"""
        return prompt
