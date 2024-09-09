import json
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

    def get_parsed_recommended_papers(self):
        df = self.last()
        data = df.to_dict()
        json_encoded = data["recommended_papers"].replace("'", '"')
        content_structured = json.loads(json_encoded)["interest_papers"]

        return content_structured, data
