import os

from state_of_the_art.config import config
from state_of_the_art.utils.llm.llm import LLM
from state_of_the_art.utils.mail import SotaMail
from state_of_the_art.utils import pdf
from state_of_the_art.insight_extractor.content_extractor import get_content_from_url


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """

    TABLE_NAME = "sota_paper_insight"

    def extract_from_url_in_clipboard(self):
        """
        loads the url frrom clipboard then calls the extract function
        """
        import subprocess

        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        self.extract_from_url(url)

    def extract_from_url(self, url: str, open_existing=True):
        """
        Generates insights for a given paper
        """

        url = self._clean_url(url)

        if open_existing and self._open_insight_summary_if_exists(url):
            return

        article_content, title, document_pdf_location = get_content_from_url(url)
        result = InsigthPrompt().get_result(article_content)

        result = f"""Title: {title}
Abstract: {url}
{result}
        """

        pdf.create_pdf(
            data=result, output_path="/tmp/current_paper.pdf", disable_open=True
        )
        paper_path = pdf.create_pdf_path("p " + title)
        print("Saving paper insights to ", paper_path)
        pdf.merge_pdfs(paper_path, ["/tmp/current_paper.pdf", document_pdf_location])

        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {"abstract_url": url, "insights": result, "pdf_path": paper_path},
        )

        if os.environ.get("SOTA_TEST"):
            print("Skipping email")
        else:
            SotaMail().send("", f"Insights from {title}", paper_path)


    def _open_insight_summary_if_exists(self, abstract_url) -> bool:
        df = config.get_datawarehouse().event(self.TABLE_NAME)
        filtered = df[(df["abstract_url"] == abstract_url) & ~(df["pdf_path"].isnull())]
        if filtered.empty:
            return False

        path = filtered["pdf_path"].values[0]
        if not os.path.exists(path):
            print("File not found: ", path)
            return False
        print("Paper insights path: ", path)
        pdf.open_pdf(path)
        print("Paper already processed")
        return True

    def _clean_url(self, url):
        print("Given url: ", url)
        url = url.strip()
        url = url.replace("file://", "")
        return url


class BasePrompt():
    def __init__(self):
        self.profile = config.get_current_audience()
        self.QUESTIONS: dict[str, str] = self.profile.paper_questions
        self.profile = config.get_current_audience()

class InsigthPrompt(BasePrompt):
    def __init__(self):
        super().__init__()

    def get_result(self, text: str) -> str:
        return LLM().call(self.get_prompt(), text)

    def get_prompt(self) -> str:
        counter = 1
        QUESTIONS = ""
        for key, question in self.QUESTIONS.items():
            QUESTIONS += f"""===
Topic ({key}): {question}
==="""
            counter += 1

        self.PROMPT = (
            lambda QUESTIONS_STR: f"""Your job is to answer Data Science and AI questions in an understandable way.
You inpersonates a board of scientists and field experts that togeter answer all the questions based on their individual opinions and way of writing. 

Person 1. Richard Feynman, has concise and simple answers using simple language and helps you to build an intuition about the topic, uses analogies often.
Person 2. Andrej Karpathy, very technical and precise, uses a lot of technical terms and is very detailed.

We value diversity in the answers. Make sure that the same question get answered by more then 1 person when its complex or nunanced.
Especially for questions that are open ended, harder, or require many examples please answer with multiple people.
Make sure to mention the new person that is answering the question at the moment and mark when a transition happens. Ex: Question 1. Person 1 (Name): ..., Person 2 (Name): Additionally to what Person 1 said, I think... Question 2. Person 1 (Name): ... Person 3 (Name): I disagree with Person 1, because ... 
We should start with simple answers first from teh most qualified person to answer the question and then go to more complex answers.
Make sure that in the answers they dont repeat each other, just add new information.
Mention the topic and question number in your answers. Do not worry about the lenght of the answers, if you need to write a lot to break down the concept do it.
Make sure to cover all the questions do not stop after answering the first one.
Make the content very clean and minimalistic, use 3 new lines to space the questions
Optimize your answers to the following audience: {self.profile.get_preferences()}

Article content starts ###start
{{text}}
### end of article content

The tasks now follow
tasks start###
{QUESTIONS_STR}
### task ends

start of answers ###start
0. Question (topic_example)
Person 1: 
This is the answer based on person 1 opinion
Person 2: 
Here goes the addition to answer on from person 2 perspective

1. Question ("""
        )

        prompt = self.PROMPT(QUESTIONS)
        return prompt