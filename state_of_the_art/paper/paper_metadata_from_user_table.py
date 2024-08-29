from state_of_the_art.utils.base_table import BaseTable


class PaperMetadataFromUser(BaseTable):
    table_name = "paper_metadata_from_user"
    schema = {
        "abstract_url": {"type": str},
        "progress": {"type": str},
    }
