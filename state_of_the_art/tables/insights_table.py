from typing import List, Union
from state_of_the_art.config import config
import pandas as pd


class InsightsTable:
    """
    Representt a single insigth for row.

    4: Very Good insight
    3: Good insight
    2: Neutral (Not Evaluated)
    1: Bad insight
    0: Very Bad insight
    """

    SCORE_VALUES = [None, 0, 1, 2, 3, 5]

    TABLE_NAME = "sota_paper_insights_new"

    def read(self) -> pd.DataFrame:
        return config.get_datawarehouse().event(self.TABLE_NAME)

    def add_insight(self, insight: str, question: str, paper_id: str, score: int):
        if not isinstance(insight, str):
            raise ValueError(f"Insight should be a string found {type(insight)}")

        if not isinstance(question, str):
            raise ValueError(f"Question should be a string: found {type(question)}")
        self.validate_score(score)

        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {
                "insight": insight,
                "question": question,
                "paper_id": paper_id,
                "score": score,
            },
        )

    def validate_score(self, score: int):
        assert score in self.SCORE_VALUES, f"Invalid score {score}"

    def update_score(self, uuid: str, score: Union[int, str]):
        if isinstance(score, str):
            score = int(score)
        self.validate_score(score)
        df = self.read()

        df.loc[df["tdw_uuid"] == uuid, "score"] = score
        config.get_datawarehouse().replace_df(self.TABLE_NAME, df, dry_run=False)

    def get_lastest_answer(self, question: str, paper)->str:
        df = self.read().sort_values(by='tdw_timestamp', ascending=False)
        result = df[(df["question"] == question) & (df["paper_id"] == paper)]

        if result.empty:
            return ""
        
        return result['insight'].iloc[0]

    def get_all_answers(self, question: str, paper)->List[str]:
        df = self.read().sort_values(by='tdw_timestamp', ascending=False)
        return df[(df["question"] == question) & (df["paper_id"] == paper)]['insight'].to_list()