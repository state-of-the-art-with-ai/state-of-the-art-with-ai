from typing import Any, Optional
from state_of_the_art.tables.base_table import BaseTable


class PaperTable(BaseTable):
    table_name = "arxiv_papers"
    schema = {
        "abstract_url": {"type": str},
        "title": {"type": str},
        "published": {"type": int},
        "institution": {"type": Optional[str]},
    }
