from state_of_the_art.tables.base_table import BaseTable


class Interests(BaseTable):
    table_name = "topics"
    schema = {
        "name": {"type": str},
        "description": {"type": str},
    }