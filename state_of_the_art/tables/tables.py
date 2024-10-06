import os

class Table:
    def __init__(self):
        # set environment variable to skip auth filter
        os.environ["SKIP_AUTH_FILTER"] = "True"

        from state_of_the_art.tables.tags_table import TagsTable
        from state_of_the_art.tables.user_table import UserTable
        self.user = UserTable()
        self.tag = TagsTable()
        
