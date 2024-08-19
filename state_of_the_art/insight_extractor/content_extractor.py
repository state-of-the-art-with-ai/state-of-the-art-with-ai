from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.downloader import Downloader
from state_of_the_art.paper.paper import Paper
from state_of_the_art.register_papers.arxiv_miner import ArxivMiner
from state_of_the_art.utils import pdf
import os


def is_pdf_url(url) -> bool:
    return url.endswith(".pdf") or ArxivPaper.is_arxiv_url(url)


def get_content_from_url(url):
    if os.environ.get("SOTA_TEST"):
        return "Test content", "Test title", "test.pdf"

    if is_pdf_url(url):
        return get_pdf_content(url)

    return get_website_content(url)


def get_pdf_content(url):
    if ArxivPaper.is_arxiv_url(url):
        paper = ArxivPaper(abstract_url=url)
        ArxivMiner().register_paper_if_not_registered(paper)
        paper = ArxivPaper.load_paper_from_url(paper.abstract_url)
        paper_title = paper.title
    else:
        paper = Paper(pdf_url=url)
        paper_title = url.split("/")[-1].replace(".pdf", "")
    print("Paper title: ", paper_title)

    local_location = Downloader().download(paper.pdf_url, title=paper_title)
    paper_content = pdf.read_content(local_location)

    return paper_content, paper_title, local_location


def get_website_content(url: str):
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
