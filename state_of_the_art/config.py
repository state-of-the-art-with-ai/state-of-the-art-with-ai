import os
from state_of_the_art.profile import get_current_profile

class Config():
    HOME = os.path.expanduser("~")
    PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers"
    NEW_PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers_new"
    get_current_profile = get_current_profile

    # the maximum number of papers to compute while sorting the batch of papers
    sort_papers_max_to_compute = 2500
    sort_papers_gpt_model = 'gpt-4-turbo-preview'
    # the maximum allowed context lenght for the open-ai model
    MAX_CHARS_CONTEXT_LENGHT = 128000 * 4 
    open_ai_key = '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'

    
    @staticmethod
    def load_config():
        return Config()




config = Config.load_config()
