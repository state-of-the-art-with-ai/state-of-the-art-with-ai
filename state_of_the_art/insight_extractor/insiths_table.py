from state_of_the_art.config import config
import pandas as pd


class InsightsTable:
    """
    Score semantics

    5: Very Good insight
    3: Good insight
    1: Okay insight
    0: Not useful insight
    """

    TABLE_NAME = "sota_paper_insights_new"

    def read(self) -> pd.DataFrame:
        return config.get_datawarehouse().read(self.TABLE_NAME)

    def add_insight(self, insight: str, paper_id: str, score: int):
        self.validate_score(score)
        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {"insight": insight, "paper_id": paper_id, "score": score},
        )

    def validate_score(self, score: int):
        assert score in [0, 1, 3, 5], f"Invalid score {score}"
