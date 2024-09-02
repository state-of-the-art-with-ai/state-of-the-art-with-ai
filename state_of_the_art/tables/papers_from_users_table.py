from state_of_the_art.tables.base_table import BaseTable


class PapersFromUserTable(BaseTable):
    table_name = "personal_papers_from_users"
    schema = {
        "url": {"type": str},
        "title": {"type": str},
        "user_uuid": {"type": "str"},
    }
