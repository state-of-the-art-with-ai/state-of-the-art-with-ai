import os
from state_of_the_art.preferences.audience import Audience
from tiny_data_warehouse import DataWarehouse


class Config():
    HOME = os.path.expanduser("~")
    NEW_PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers_new"
    MAX_ABSTRACT_SIZE_RANK=500
    _MAX_PAPERS_TO_MINE_PER_QUERY = 50
    DEFAULT_LOOK_BACK_DAYS = 1
    MINIMAL_CONFIRMATION_COST = 0.35

    # the maximum number of papers to compute while sorting the batch of papers
    GPT_MODEL = 'gpt-4-turbo-preview'
    RANK_MAX_PAPERS_TO_COMPUTE = 2000
    # the maximum allowed context lenght for the open-ai model
    MAX_CHARS_CONTEXT_LENGHT = 128000 * 4 
    OPEN_API_KEY = os.environ['SOTA_OPENAI_KEY']
    dwh = None


    def papers_to_mine_per_query(self) -> int:
        if os.environ.get('PAPERS_TO_MINE_PER_QUERY'):
            return int(os.environ.get('PAPERS_TO_MINE_PER_QUERY'))
        return self._MAX_PAPERS_TO_MINE_PER_QUERY

    def get_current_audience(self) -> Audience:
        # @todo implement this dynamically
        from examples.gyg_teams import sota_preferences
        return sota_preferences.get_current_audience()
    @staticmethod
    def load_config():
        return Config()

    def get_datawarehouse(self) -> DataWarehouse:
        if self.dwh:
            return self.dwh

        self.dwh = DataWarehouse(events_config={'arxiv_papers': {'prevent_duplicates_col': 'url'}})

        return self.dwh




config = Config.load_config()
