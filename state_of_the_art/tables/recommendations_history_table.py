import json
from typing import Any
from state_of_the_art.app.utils.login_utils import LoggedInUser
from state_of_the_art.tables.base_table import BaseTable

from enum import Enum

class RecommendationGenerationStatus(str, Enum):
    STARTED = "started"
    ERROR = "error"
    SUCCESS = "success"

class RecommendationsRunsTable(BaseTable):
    table_name = "state_of_the_art_summary"
    schema = {
        "recommended_papers": {"type": str},
        "from_date": {"type": Any},
        "to_date": {"type": Any},
        "start_time": {"type": Any},
        "end_time": {"type": Any},
        "papers_analysed": {"type": str},
        "papers_analysed_total": {"type": Any},
        "status": {"type": str},
        "error_details": {"type": str},
        "user_id": {"type": str},
    }
    def __init__(self, auth_filter=True, auth_callable=None):
        if auth_filter:
            if not auth_callable:
                auth_callable = LoggedInUser.get_instance().get_uuid
            self.auth_context = [auth_callable, "user_id"]
        super().__init__()


    def get_parsed_recommended_papers(self):
        df = self.last()
        data = df.to_dict()
        json_encoded = data["recommended_papers"].replace("'", '"')
        content_structured = json.loads(json_encoded)["interest_papers"]

        return content_structured, data
