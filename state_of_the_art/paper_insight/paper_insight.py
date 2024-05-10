import os
import sys

from state_of_the_art.config import config
from state_of_the_art.utils.llm import LLM
from state_of_the_art.paper.paper import Paper
from state_of_the_art.utils.mail import SotaMail
from state_of_the_art.utils import pdf


class PaperInsightExtractor:
    """
    Looks into a single paper and extracts insights
    """

    def __init__(self):
        self.profile = config.get_current_audience()

    def generate(self, abstract_url: str):
        """
        Generates insights for a given paper
        """
        print("Generating insights for paper: ", abstract_url)
        abstract_url = abstract_url.strip()
        abstract_url = Paper.convert_pdf_to_abstract(abstract_url)

        self.open_if_exists(abstract_url)

        local_location = Paper(arxiv_url=abstract_url).download()

        paper_title = abstract_url
        try:
            paper = Paper.load_paper_from_url(abstract_url)
            paper_title = paper.title
        except Exception as e:
            print(f"Error loading paper from url {abstract_url} {e}")

        paper_content = pdf.read_content(local_location)
        prompt = self._get_prompt()

        result = LLM().call(prompt, paper_content)
        result = f"""Title: {paper_title}
Abstract: {abstract_url}
{result}
        """
        print(result)

        pdf.create_pdf(
            data=result, output_path="/tmp/current_paper.pdf", disable_open=True
        )
        paper_path = pdf.create_pdf_path("p " + paper_title)
        print("Saving paper insights to ", paper_path)
        pdf.merge_pdfs(paper_path, ["/tmp/current_paper.pdf", local_location])

        config.get_datawarehouse().write_event(
            "sota_paper_insight",
            {"abstract_url": abstract_url, "insights": result, "pdf_path": paper_path},
        )

        if os.environ.get("SOTA_TEST"):
            print("Skipping email")
        else:
            SotaMail().send("", f"Insights from {paper_title}", paper_path)

    def open_if_exists(self, abstract_url):
        df = config.get_datawarehouse().event('sota_paper_insight')
        filtered = df[(df['abstract_url'] == 'http://arxiv.org/abs/1904.05526v2') & ~(df['pdf_path'].isnull())]
        if not filtered.empty:
            pdf.open_pdf(filtered['pdf_path'].values[0])

        print("Paper already processed")
        sys.exit(0)


    def _get_prompt(self) -> str:

        counter = 1
        QUESTIONS = ""
        for key, question in self.profile.paper_questions.items():
            QUESTIONS += f"""===
Question {counter} (Topic: {key})
{question}
==="""
            counter += 1

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

    def answer_questions_from_clipboard(self):
        import subprocess

        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        self.generate(url)
