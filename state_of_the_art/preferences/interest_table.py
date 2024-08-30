from state_of_the_art.utils.base_table import BaseTable


class Interests(BaseTable):
    table_name = "topics"
    schema = {
        "name": {"type": str},
        "description": {"type": str},
    }
