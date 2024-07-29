from state_of_the_art.config import config
import pandas as pd


class InsightsTable:
    """
    Score semantics

    5: Very Good insight
    3: Good insight
    1: Neutral (Not Evaluated)
    0: Not useful insight
    """
    SCORE_VALUES = [0, 1, 3, 5]

    TABLE_NAME = "sota_paper_insights_new"

    def read(self) -> pd.DataFrame:
        return config.get_datawarehouse().event(self.TABLE_NAME)

    def add_insight(self, insight: str, paper_id: str, score: int):
        self.validate_score(score)
        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {"insight": insight, "paper_id": paper_id, "score": score},
        )

    def validate_score(self, score: int):
        assert score in self.SCORE_VALUES, f"Invalid score {score}"

    def clipboard_content(self):
        import subprocess

        return subprocess.getoutput("clipboard get_content")
    
    def update_score(self, uuid: str, score: int):
        self.validate_score(score)
        df = self.read()

        df.loc[df["tdw_uuid"] == uuid, "score"] = score

        config.get_datawarehouse().replace_df(self.TABLE_NAME, df, dry_run=False)

