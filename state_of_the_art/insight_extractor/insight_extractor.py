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

    def generate(self, url: str, open_existing=True):
        """
        Generates insights for a given paper
        """

        url = self._clean_url(url)

        if open_existing and self.open_if_exists(url):
            return

        if self.is_pdf_url(url):
            document_content, title, document_pdf_location = self.get_pdf_content(url)
        else:
            document_content, title, document_pdf_location = self._get_website_content(url)


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


    def is_pdf_url(self, url):
        return url.endswith(".pdf") or ArxivPaper.is_arxiv_url(url)

    def get_pdf_content(self, url):
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


    def _get_website_content(self, url):
        from urllib.request import urlopen, Request
        from bs4 import BeautifulSoup

        req = Request(
            url=url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
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
        text = '\n'.join(chunk for chunk in chunks if chunk)

        # get teh page title
        title = soup.title.string

        location = pdf.create_pdf(data=text,output_path_description='webpage ' + title, disable_open=True)

        return text, title, location


    def open_if_exists(self, abstract_url):
        df = config.get_datawarehouse().event(self.TABLE_NAME)
        filtered = df[(df["abstract_url"] == abstract_url) & ~(df["pdf_path"].isnull())]
        if filtered.empty:
            return False

        path = filtered["pdf_path"].values[0]
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
