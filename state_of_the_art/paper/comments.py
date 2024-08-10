
from typing import Any
from state_of_the_art.utils.base_table import BaseTable

class Comments(BaseTable):
    table_name = 'comments'
    schema = {
        'message': {'type': str},
        'paper_url': {'type': str}
    }
