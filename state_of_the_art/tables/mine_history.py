from typing import Any
from state_of_the_art.tables.base_table import BaseTable


class ArxivMiningHistory(BaseTable):
    table_name = "arxiv_mining_history"
    schema = {
        "keywords": {"type": str},
        "total_new_papers_found": {"type": Any},
    }
