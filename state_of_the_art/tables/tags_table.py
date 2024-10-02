from state_of_the_art.app.utils.login_utils import LoggedInUser
from state_of_the_art.tables.base_table import BaseTable


class TagsTable(BaseTable):
    table_name = "tags"
    schema = {
        "tags": {"type": str},
        "paper_id": {"type": str},
    }
    DEFAULT_TAGS = ["To Read", "Save For Later"]

    def __init__(self, auth_filter=True, auth_callable=None):
        if auth_filter:
            if not auth_callable:
                auth_callable = LoggedInUser.get_instance().get_uuid
            self.auth_context = [auth_callable, "user_uuid"]
        super().__init__()

    def add_tag_to_paper(self, paper_id: str, tag: str):
        paper = self.load_with_value("paper_id", paper_id)

        if not paper.empty:
            tags = paper.iloc[0]["tags"]
            tags = tags.split(",")
            tags.append(tag)
            self.update_or_create(
                by_key="paper_id",
                by_value=paper_id,
                new_values={"tags": ",".join(tags)},
            )
        else:
            self.add(tags=tag, paper_id=paper_id)
