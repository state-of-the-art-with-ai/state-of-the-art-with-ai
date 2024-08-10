

from state_of_the_art.utils.base_table import BaseTable

class Topics(BaseTable):
    table_name = 'topics'
    schema = {
        'name': {'type': str},
        'description': {'type': str},
    }