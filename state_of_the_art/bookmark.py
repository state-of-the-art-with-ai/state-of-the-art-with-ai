
from typing import Optional
from state_of_the_art.config import config
import datetime

from state_of_the_art.utils.mail import Mail
from state_of_the_art.paper.paper import Paper

class Bookmark():
    """
    Bookmarking papers for future reference
    """
    EVENT_NAME = 'paper_bookmarks'
    def add(self, paper_url, comment: Optional[str]):

        if not comment:
            comment = 'registered interest'

        paper_url = paper_url.strip()
        print(f"Registering paper {paper_url} in bookmarks")
        try: 
            paper = Paper(arxiv_url=Paper.convert_pdf_to_abstract(paper_url))
        except Exception as e:
            print("Given url is not from Arxiv")

        dwh = config.get_datawarehouse()
        dwh.write_event(self.EVENT_NAME, {'paper_url': paper_url, 'comment': comment, 'bookmarked_date': datetime.date.today().isoformat()})
        self.send_to_email()

    def add_interactive(self):
        print("Interactive collecting paper input")
        import subprocess
        url = subprocess.check_output("collect_input -n Url -p", shell=True, text=True)
        comment = subprocess.check_output("collect_input -n Comment -p", shell=True, text=True)

        self.add(url, comment)


    def register_interest(self):
        import subprocess
        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        url = url.strip()
        self.add(url, 'regisered interest')

    def list(self, return_result=True, top_n=None):
        dwh = config.get_datawarehouse()
        dict = dwh.event(self.EVENT_NAME).set_index("tdw_timestamp").sort_values(by='bookmarked_date', ascending=False).to_dict(orient='index')

        result  = "Bookmarks: \n\n"
        counter = 1
        for i in dict:
            paper_title = "Title not found"
            paper_url = dict[i]['paper_url']

            if Paper.is_arxiv_url(paper_url):
                paper_url = Paper.convert_pdf_to_abstract(paper_url)

            try:
                paper = Paper.load_paper_from_url(paper_url)
                paper_title = paper.title
            except Exception as e:
                pass
            result += f"""{counter}. Title: {paper_title} 
{paper_url}
Comment: {dict[i]['comment']} 
Published: {paper.published_date_str()}
Bookmarked: {str(dict[i]['bookmarked_date']).split(' ')[0]}
\n
"""
            counter += 1
            if top_n and counter > top_n:
                break

        if return_result:
            return result

        print(result)

    def open_latest_paper(self):
        dwh = config.get_datawarehouse()
        dict = dwh.event(self.EVENT_NAME).sort_values(by='bookmarked_date', ascending=False).to_dict(orient='record')
        latest = dict[0]
        Paper(arxiv_url=latest['paper_url']).download_and_open()


    def send_to_email(self):
        Mail().send(self.list(return_result=True), "SOTA Bookmarks as of " + datetime.date.today().isoformat())

    def fzf(self):
        import os
        os.system("sota bookmark list | fzf ")

