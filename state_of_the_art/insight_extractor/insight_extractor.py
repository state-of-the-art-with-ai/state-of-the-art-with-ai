import os

from state_of_the_art.config import config
from state_of_the_art.paper.downloader import Downloader
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.utils.llm.llm import LLM
from state_of_the_art.paper.paper import ArxivPaper, Paper
from state_of_the_art.utils.mail import SotaMail
from state_of_the_art.utils import pdf


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """

    TABLE_NAME = "sota_paper_insight"

    def __init__(self):
        self.profile = config.get_current_audience()
        self.QUESTIONS: dict[str, str] = self.profile.paper_questions
        self.PROMPT = (
            lambda QUESTIONS_STR: f"""Your job is to answer Data Science and AI questions in an understandable way.
You inpersonates a board of scientists that togeter answer all the questions based on their individual opinions and way of writing. 

Person 1. Richard Feynman, has concise and simple answers using simple language and helps you to build an intuition about the topic, uses analogies often.
Person 2. A person like Edu Lira, extremly energized and fixated about improving the world and making it a better place, making sure in his explanations nobody is left behind.
Person 3. Andrej Karpathy, very technical and precise, uses a lot of technical terms and is very detailed.

We value diversity in the answers. Make sure that the same question get answered by more then 1 person when its complex or nunanced.
Especially for questions that are open ended, harder, or require many examples please answer with multiple people.
Make sure to mention the new person that is answering the question at the moment and mark when a transition happens. Ex: Question 1. Person 1 (Name): ..., Person 2 (Name): Additionally to what Person 1 said, I think... Question 2. Person 1 (Name): ... Person 3 (Name): I disagree with Person 1, because ... 
We should start with simple answers first from teh most qualified person to answer the question and then go to more complex answers.
Make sure that in teh answers they dont repeat each other, just add new information.

Mention the topic and question number in your answers. Do not worry about the lenght of the answers, if you need to write a lot to break down the concept do it.
Make sure to cover all the questions do not stop after answering the first one
Make the content very readable, use 3 new lines to space the questions
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

    def extract_from_url(self, url: str, open_existing=True):
        """
        Generates insights for a given paper
        """

        url = self._clean_url(url)

        if open_existing and self._open_if_exists(url):
            return

        if self._is_pdf_url(url):
            document_content, title, document_pdf_location = self._get_pdf_content(url)
        else:
            document_content, title, document_pdf_location = self._get_website_content(
                url
            )

        prompt = self._get_prompt()

        result = LLM().call(prompt, document_content)
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

    def _is_pdf_url(self, url):
        return url.endswith(".pdf") or ArxivPaper.is_arxiv_url(url)

    def _get_pdf_content(self, url):
        if ArxivPaper.is_arxiv_url(url):
            paper = ArxivPaper(url=url)
            ArxivMiner().register_paper_if_not_registered(paper)
            paper = ArxivPaper.load_paper_from_url(url=paper.abstract_url)
            paper_title = paper.title
        else:
            paper = Paper(pdf_url=url)
            paper_title = url.split("/")[-1].replace(".pdf", "")
        print("Paper title: ", paper_title)

        local_location = Downloader().download(paper.pdf_url, title=paper_title)
        paper_content = pdf.read_content(local_location)

        return paper_content, paper_title, local_location

    def _get_website_content(self, url: str):
        from urllib.request import urlopen, Request
        from bs4 import BeautifulSoup

        req = Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req).read()

        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()  # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)

        # get teh page title
        title = soup.title.string

        location = pdf.create_pdf(
            data=text, output_path_description="webpage " + title, disable_open=True
        )

        return text, title, location

    def _open_if_exists(self, abstract_url):
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

    def _get_prompt(self) -> str:
        counter = 1
        QUESTIONS = ""
        for key, question in self.QUESTIONS.items():
            QUESTIONS += f"""===
Topic ({key}): {question}
==="""
            counter += 1

        prompt = self.PROMPT(QUESTIONS)
        return prompt

    def answer_questions_from_clipboard(self):
        import subprocess

        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        self.extract_from_url(url)
