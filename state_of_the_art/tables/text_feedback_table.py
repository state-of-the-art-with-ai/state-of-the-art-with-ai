import json
from typing import Any, Optional
from state_of_the_art.tables.base_table import BaseTable
from enum import Enum


class TextFeedbackTable(BaseTable):
    table_name = "text_feedback"
    schema = {"text": {"type": str}, "score": {"type": Any}, "type": {"type": str}, "context": {"type": str}}

    def add_feedback(self, text: str, score: int, type: Optional[str] = None, context: Optional[str] = None):

        posible_values = [i.value for i in ScoreMeaning]

        if score not in posible_values:
            raise ValueError(f"Invalid score {score}")
        if not type: 
            type = TextTypes.default.value
        if not context: 
            context = ""
        else:
            context = json.dumps(context)
        
        self.add(text=text, score=score, type=type, context=context)

class TextTypes(Enum):
    default = "default"
    paper_title = "paper_title"
    paper_insight = "paper_insight"

class ScoreMeaning(Enum):
    changed_my_life = 4
    learned_something_new = 3
    cool = 2
    bad = 1
    very_bad = 0

if __name__ == "__main__":
    import fire
    fire.Fire()
