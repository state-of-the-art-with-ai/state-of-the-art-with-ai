


from state_of_the_art.utils.base_table import BaseTable

class QuestionsTable(BaseTable):
    table_name = 'questions'
    schema = {
        'question': {'type': str},
    }