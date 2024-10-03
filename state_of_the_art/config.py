import os
from state_of_the_art.user_preferences.audience import Audience
from state_of_the_art.user_preferences.preferences import SotaPreferences
from tiny_data_warehouse import DataWarehouse
import time


class Tables:
    # for generated summaries
    SUMMARIES = "state_of_the_art_summary"
    INSIGHTS = "sota_paper_insight"


class Config:

    HOME = os.path.expanduser("~")
    NEW_PAPERS_FOLDER = os.path.expanduser("~") + "/.arxiv_papers_new"
    MAX_ABSTRACT_SIZE_RANK = 500
    DEFAUL_MAX_PAPERS_TO_MINE_PER_QUERY = 75
    DEFAULT_LOOK_BACK_DAYS = 1
    MINIMAL_CONFIRMATION_COST = 0.35
    DEFAULT_REPORT_LOOKBACK_DAYS = 2
    region = "eu-central-1"
    aws_account_id = "467863034863"
    streamlit_port = 80
    ecr_image = "sota/monorepo"
    image_local_tag = "sota"
    data_bucket = "sota.data"
    TINY_DATA_WAREHOUSE_EVENTS = f"{HOME}/.tinyws/events"
    MODEL_NAME = f"model.pth"
    MODELS_PATH_LOCALLY = f"{HOME}/.tinyws/models/"
    TEXT_PREDICTOR_PATH_LOCALLY = f"{HOME}/.tinyws/models/" + MODEL_NAME
    MODEL_FOLDER_IN_CLOUD = f"s3://{data_bucket}/models"
    MODEL_IN_CLOUD = f"s3://{data_bucket}/models/" + MODEL_NAME
    PRECOMPUTED_FOLDER = f"{HOME}/.tinyws/precomputed"
    PRECOMPUTED_SEARCH = PRECOMPUTED_FOLDER + "/papers.pkl"
    ONLINE_WEBSITE = 'https://state-of-the-art-with-ai-750989039686.europe-west3.run.app'

    # the maximum number of papers to compute while sorting the batch of papers
    GPT_MODEL = "gpt-4o"
    RANK_MAX_PAPERS_TO_COMPUTE = 2000
    _MAX_ARTICLES_TO_RETURN_RANK = 100
    # the maximum allowed context lenght for the open-ai model
    MAX_CHARS_CONTEXT_LENGHT = 128000 * 4
    OPEN_API_KEY = os.environ["SOTA_OPENAI_KEY"]
    dwh = None

    def __init__(self) -> None:
        pass

    QUERIES_TO_MINE = [
        "data science",
        "mlops",
        "artificial intelligence",
        "cat:cs.AI",
        "cat:cs.CY",
        "cat:stat",
        "machine learning",
        "deep learning",
        "ethics",
        "marketing science",
    ]

    def get_max_articles_to_return_rank(self) -> int:
        if os.environ.get("MAX_ARTICLES_TO_RETURN_RANK"):
            return int(os.environ.get("MAX_ARTICLES_TO_RETURN_RANK"))
        return self._MAX_ARTICLES_TO_RETURN_RANK

    def papers_to_mine_per_query(self) -> int:
        if os.environ.get("PAPERS_TO_MINE_PER_QUERY"):
            return int(os.environ.get("PAPERS_TO_MINE_PER_QUERY"))
        return self.DEFAUL_MAX_PAPERS_TO_MINE_PER_QUERY

    def get_current_audience(self) -> Audience:
        jean = Audience(
            audience_description=f"""Jean Machado, a Data Science Manager for GetYourGuide.
        Jean wants the following out this tool:
        2. to understand exciting and important topics with further depth
        1. to have actionable insights and learnings he can apply in his teams
        3. to stay on the bleeding edge of the field

        to see what is going on on important institutions and companies in the field of data science and machine learning and computer science

        Jean manages the following teams in GetYourGuide:
        Jean is interseted in the following high level topics:

        - data science
        - ai for social good
        - experimentation design, analysis and interpretation
        - search engine optimization
        - ai ethics
        - data science leadership
        - truth, and fake news

            """,
            keywords=[
                "cs.AI",
                "cs.LG",
                "cs.SI",
                "stat.ML",
                "ai",
                "machine learning",
                "data science",
                "large language models",
                "ai for social good",
                "ai ethics"
                "data science management and data science teams  performance",
                "ai regulation",
                "forecasting",
                "bidding",
                "deep learning & neural nets",
                "mlops",
                "ads",
                "computer science",
                "knowledge graphs",
                "graph neural networks",
                "ai productivity",
                "explainable ai",
                "xai",
            ],
        )
        sota_preferences = SotaPreferences(
            audiences={"jean": jean}, default_profile="jean"
        )
        return sota_preferences.get_current_audience()

    @staticmethod
    def load_config():
        return Config()
    
    def is_production(self):
        # in production user variable is not set
        return os.environ.get("USER", '') == ''

    def get_datawarehouse(self, skip_cache=False) -> DataWarehouse:
        if self.dwh and not skip_cache:
            return self.dwh

        events_folder=None
        if os.environ.get("SOTA_TEST"):
            print("Running tests so using a different folder for the datawarehouse")
            events_folder='/tmp/.tinyws' if os.environ.get("SOTA_TEST") else None
        self.dwh = DataWarehouse(
            events_folder=events_folder,
            events_config={"arxiv_papers": {"prevent_duplicates_col": "abstract_url"}}
        )

        return self.dwh

    def get_local_papers_path(self) -> str:
        """return the location where the papers are stored"""

        path = f"{Config.HOME}/.sota/papers"

        if not os.path.exists(path):
            os.system("mkdir -p " + path)

        return path


config = Config.load_config()
