from state_of_the_art.tables.base_table import BaseTable


class QuestionsTable(BaseTable):
    table_name = "questions"
    schema = {
        "short_version": {"type": str},
        "question": {"type": str},
        "order": {"type": int},
        "min_items": {"type": int},
        "max_items": {"type": int},
    }
