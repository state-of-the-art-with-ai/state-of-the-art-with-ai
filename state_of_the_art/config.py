import os
from state_of_the_art.audience import get_current_profile

class Config():
    HOME = os.path.expanduser("~")
    PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers"
    NEW_PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers_new"
    get_current_profile = get_current_profile
    MAX_ABSTRACT_SIZE_RANK=500
    DEFAULT_LOOK_BACK_DAYS = 14

    # the maximum number of papers to compute while sorting the batch of papers
    sort_papers_gpt_model = 'gpt-4-turbo-preview'
    sort_papers_max_to_compute = 800 
    # the maximum allowed context lenght for the open-ai model
    MAX_CHARS_CONTEXT_LENGHT = 128000 * 4 
    open_ai_key = os.environ['SOTA_OPENAI_KEY']

    @staticmethod
    def load_config():
        return Config()

    def get_datawharehouse(self):
        from tiny_data_wharehouse.data_wharehouse import DataWharehouse
        return DataWharehouse()




config = Config.load_config()
