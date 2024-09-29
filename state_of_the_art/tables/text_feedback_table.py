from typing import Any
from state_of_the_art.tables.base_table import BaseTable
from enum import Enum


class TextFeedbackTable(BaseTable):
    table_name = "text_feedback"
    schema = {"text": {"type": str}, "score": {"type": Any}, "type": {"type": str}}


class TextTypes(Enum):
    default = "default"
