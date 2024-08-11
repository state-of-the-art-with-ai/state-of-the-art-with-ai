

from state_of_the_art.utils.base_table import BaseTable

class TagsTable(BaseTable):
    table_name = 'tags'
    schema = {
        'tags': {'type': str},
        'paper_id': {'type': str},
    }
    DEFAULT_TAGS = ['To Read', 'Save For Later']