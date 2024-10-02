from state_of_the_art.app.utils.login_utils import LoggedInUser
from state_of_the_art.tables.base_table import BaseTable


class InterestTable(BaseTable):
    table_name = "topics"
    schema = {
        "name": {"type": str},
        "description": {"type": str},
        "user_uuid": {"type": str},
    }
    def __init__(self, auth_filter=True, auth_callable=None):
        if auth_filter:
            if not auth_callable:
                auth_callable = LoggedInUser.get_instance().get_uuid
            self.auth_context = [auth_callable, "user_uuid"]
        super().__init__()
