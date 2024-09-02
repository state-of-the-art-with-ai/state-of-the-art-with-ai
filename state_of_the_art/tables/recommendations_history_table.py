from typing import Any
from state_of_the_art.tables.base_table import BaseTable


class RecommendationsHistoryTable(BaseTable):
    table_name = "state_of_the_art_summary"
    schema = {
        "from_date": {"type": Any},
        "to_date": {"type": Any},
        "papers_analysed": {"type": str},
        "papers_analysed_total": {"type": Any},
        "recommended_papers": {"type": str},
    }
