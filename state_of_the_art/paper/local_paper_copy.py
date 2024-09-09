import os
from tiny_data_warehouse import DataWarehouse

from state_of_the_art.paper.arxiv_paper import ArxivPaper
from state_of_the_art.paper.downloader import PaperDownloader

def open_paper_locally(paper: ArxivPaper):
    downloader = PaperDownloader()
    downloader.download_from_arxiv(paper)
    downloader.open_from_arxiv(paper)

