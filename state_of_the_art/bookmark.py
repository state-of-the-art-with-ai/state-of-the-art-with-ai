
from typing import Optional
from state_of_the_art.config import config
import datetime
from state_of_the_art.paper import Paper


class Bookmark():

    EVENT_NAME = 'paper_bookmarks'
    def add(self, paper_url, comment: Optional[str]):
        print(f"Registering paper {paper_url} in bookmarks")
        paper = Paper(arxiv_url=paper_url)

        dwh = config.get_datawharehouse()
        dwh.write_event(self.EVENT_NAME, {'paper_url': paper.arxiv_url, 'comment': comment, 'bookmarked_date': datetime.date.today().isoformat()})

    def list(self):
        dwh = config.get_datawharehouse()
        dict = dwh.event(self.EVENT_NAME).set_index("tdw_timestamp").sort_values(by='bookmarked_date', ascending=False).to_dict(orient='index')

        for i in dict:
            print(f"{str(dict[i]['bookmarked_date']).split(' ')[0]} {dict[i]['paper_url']} {dict[i]['comment']} ")

    def open_latest_paper(self):
        dwh = config.get_datawharehouse()
        dict = dwh.event(self.EVENT_NAME).sort_values(by='bookmarked_date', ascending=False).to_dict(orient='record')
        latest = dict[0]
        Paper(arxiv_url=latest['paper_url']).download_and_open()



    def fzf(self):
        import os
        os.system("sota bookmark list | fzf ")

