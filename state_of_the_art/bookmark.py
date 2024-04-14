
from typing import Optional
from state_of_the_art.config import config
import datetime

from state_of_the_art.utils.mail import Mail
from state_of_the_art.paper.paper import Paper

class Bookmark():

    EVENT_NAME = 'paper_bookmarks'
    def add(self, paper_url, comment: Optional[str]):
        print(f"Registering paper {paper_url} in bookmarks")
        paper = Paper(arxiv_url=paper_url)

        dwh = config.get_datawharehouse()
        dwh.write_event(self.EVENT_NAME, {'paper_url': paper.arxiv_url, 'comment': comment, 'bookmarked_date': datetime.date.today().isoformat()})

    def list(self, return_result=True):
        dwh = config.get_datawharehouse()
        dict = dwh.event(self.EVENT_NAME).set_index("tdw_timestamp").sort_values(by='bookmarked_date', ascending=False).to_dict(orient='index')

        result  = "Bookmarks: \n\n"
        counter = 1
        for i in dict:
            paper_title = "Title not found"
            paper_url = Paper.convert_pdf_to_abstract(dict[i]['paper_url'])
            try:
                paper = Paper.load_paper_from_url(paper_url)
                paper_title = paper.title
            except Exception as e:
                pass
            result += f"""{counter}. Title: {paper_title} 
{paper_url}
Date bookmark: {str(dict[i]['bookmarked_date']).split(' ')[0]}
Comment: {dict[i]['comment']} 

"""
            counter += 1

        if return_result:
            return result

        print(result)

    def open_latest_paper(self):
        dwh = config.get_datawharehouse()
        dict = dwh.event(self.EVENT_NAME).sort_values(by='bookmarked_date', ascending=False).to_dict(orient='record')
        latest = dict[0]
        Paper(arxiv_url=latest['paper_url']).download_and_open()


    def send_to_email(self):
        Mail().send(self.list(return_result=True), "SOTA Bookmarks as of " + datetime.date.today().isoformat())



    def fzf(self):
        import os
        os.system("sota bookmark list | fzf ")

