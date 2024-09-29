from typing import Any, Optional
from state_of_the_art.tables.base_table import BaseTable
from enum import Enum


class TextFeedbackTable(BaseTable):
    table_name = "text_feedback"
    schema = {"text": {"type": str}, "score": {"type": Any}, "type": {"type": str}, "context": {"type": str}}

    def add_feedback(self, text: str, score: int, type: Optional[str] = None, context: Optional[str] = None):
        if score not in [ScoreMeaning.best_of_best.value, ScoreMeaning.positive.value, ScoreMeaning.negative.value]:
            raise ValueError(f"Invalid score {score}")
        if not type: 
            type = TextTypes.default.value
        if not context: 
            context = ""
        self.add(text=text, score=score, type=type, context=context)


class TextTypes(Enum):
    default = "default"
    paper_title = "paper_title"

class ScoreMeaning(Enum):
    best_of_best = 2
    positive = 1
    negative = 0

if __name__ == "__main__":
    import fire
    fire.Fire()
