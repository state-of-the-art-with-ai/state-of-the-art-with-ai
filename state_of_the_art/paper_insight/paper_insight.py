
from state_of_the_art.config import config
from state_of_the_art.llm import LLM
from state_of_the_art.paper.paper import Paper
from state_of_the_art.utils.mail import Mail


class PaperInsightExtractor:
    """
    Looks into a single paper and extracts insights
    """
    def __init__(self):
        self.profile = config.get_current_audience()

    def answer_questions(self, abstract_url: str, question_topic=None):

        abstract_url = Paper.convert_pdf_to_abstract(abstract_url)
        local_location = Paper(arxiv_url=abstract_url).download()

        paper_title = abstract_url
        try :
            paper = Paper.load_paper_from_url(abstract_url)
            paper_title = paper.title
        except Exception as e:
            print(f"Error loading paper from url {abstract_url} {e}")


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
        result = f"Abstract: {abstract_url} + \n\n" + result
        print(result)
        question_topic = question_topic if question_topic else "all"
        config.get_datawarehouse().write_event('sota_paper_insight', {'abstract_url': abstract_url, 'insights': result, 'topic': question_topic})

        Mail().send(result, f'Insight extracted form paper {paper_title}')


    def _get_prompt(self, question_topic=None) -> str:
        QUESTIONS = ""

        counter = 1
        for key, question in self.profile.paper_questions.items():
            QUESTIONS+=f"""===
Question {counter} (Topic: {key})
{question}
==="""
            counter+=1

        if question_topic:
            QUESTIONS = self.profile.paper_questions[question_topic]


        prompt = f"""You are an world class expert in Data Science and computer science.
Your job is answering questions about the paper given to you as they are asked.
Mention the topic and question number in your answers. Make sure to answer all questions you are asked.
Space the questions with 3 new lines
Optimize your suggestions to the following audience: {self.profile.get_preferences()}

Article content starts starts ###start
{{text}}
### end of article content

The tasks now follow
tasks start###
{QUESTIONS}
### task ends

start of answers ###start
Question 1 (institution):
"""


        return prompt


