import os

from state_of_the_art.paper.paper import Paper

class BrowserPapers:
    def fzf(self):
        outoput = os.system('sota papers | /Users/jean.machado/.fzf/bin/fzf --layout=reverse  | sota browser_papers open_from_fzf')
        print(outoput)

    def open_from_fzf(self):
        import sys
        text = sys.stdin.readlines()[0]
        paper_url = text.split(' ')[-2].strip()
        print('"', paper_url,'"')
        print('Opening paper: ', paper_url)
        os.system(f"clipboard set_content {paper_url}")
        Paper(arxiv_url=paper_url).download_and_open()
