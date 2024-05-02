
from state_of_the_art.config import config
from state_of_the_art.utils.llm import LLM
from state_of_the_art.paper.paper import Paper
from state_of_the_art.utils.mail import Mail
from state_of_the_art.utils.pdf import create_pdf
from state_of_the_art.utils import pdf
import datetime


class PaperInsightExtractor:
    """
    Looks into a single paper and extracts insights
    """
    def __init__(self):
        self.profile = config.get_current_audience()

    def answer_questions_from_clipboard(self):
        import subprocess
        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        self.answer_questions(url)

    def answer_questions(self, abstract_url: str, question_topic=None):
        print("Generating insights for paper: ", abstract_url)
        abstract_url = abstract_url.strip()

        abstract_url = Paper.convert_pdf_to_abstract(abstract_url)
        local_location = Paper(arxiv_url=abstract_url).download()

        paper_title = abstract_url


        pdf_file_name = f'paper_{datetime.date.today().isoformat()}.pdf'
        try :
            paper = Paper.load_paper_from_url(abstract_url)
            paper_title = paper.title
            pdf_file_name = paper.get_title_filename()
        except Exception as e:
            print(f"Error loading paper from url {abstract_url} {e}")



        paper_content = pdf.read_content(local_location)
        prompt = self._get_prompt(question_topic=question_topic)

        result = LLM().call(prompt, paper_content)
        result = f"""Title: {paper_title}
Abstract: {abstract_url}
{result}
        """
        print(result)

        question_topic = question_topic if question_topic else "all"
        config.get_datawarehouse().write_event('sota_paper_insight', {'abstract_url': abstract_url, 'insights': result, 'topic': question_topic})
        create_pdf(result, f"/tmp/current_paper.pdf", disable_open=True)
        output_paper_name = f"/tmp/" + pdf_file_name
        pdf.merge_pdfs(output_paper_name, ["/tmp/current_paper.pdf", local_location ])

        Mail().send(result, f'Insight extracted form paper {paper_title}', attachment=output_paper_name)


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
make sure to mention all the questions do not stop after answering the first one
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


