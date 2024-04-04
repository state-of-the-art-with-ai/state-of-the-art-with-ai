
from typing import Optional
from state_of_the_art.config import config
import datetime
from state_of_the_art.paper import Paper

class Bookmark():

    EVENT_NAME = 'paper_bookmarks'
    def new(self, paper_url, comment: Optional[str]):
        print(f"Registering paper {paper_url} in bookmarks")
        paper = Paper(arxiv_url=paper_url)

        dwh = config.get_datawharehouse()
        dwh.write_event(self.EVENT_NAME, {'paper_url': paper.arxiv_url, 'comment': comment, 'bookmarked_date': datetime.date.today().isoformat()})

    def list(self):
        dwh = config.get_datawharehouse()
        return dwh.event(self.EVENT_NAME).set_index("tdw_timestamp").to_dict(orient='index')

