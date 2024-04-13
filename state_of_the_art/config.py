import os
from state_of_the_art.preferences.audience import Audience

class Config():
    HOME = os.path.expanduser("~")
    PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers"
    NEW_PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers_new"
    MAX_ABSTRACT_SIZE_RANK=500
    MAX_PAPERS_TO_MINE_PER_QUERY=50
    DEFAULT_LOOK_BACK_DAYS = 2
    MINIMAL_CONFIRMATION_COST = 0.35

    # the maximum number of papers to compute while sorting the batch of papers
    GPT_MODEL = 'gpt-4-turbo-preview'
    RANK_MAX_PAPERS_TO_COMPUTE = 2000
    # the maximum allowed context lenght for the open-ai model
    MAX_CHARS_CONTEXT_LENGHT = 128000 * 4 
    OPEN_API_KEY = os.environ['SOTA_OPENAI_KEY']

    def get_current_audience(self) -> Audience:
        from state_of_the_art.preferences.audience import get_current_audience
        return get_current_audience()
    @staticmethod
    def load_config():
        return Config()

    def get_datawharehouse(self):
        from tiny_data_wharehouse.data_wharehouse import DataWharehouse
        return DataWharehouse()




config = Config.load_config()
