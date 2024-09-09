from state_of_the_art.tables.base_table import BaseTable


class PaperEmbeddingsTable(BaseTable):
    table_name = "paper_embeddings"
    schema = {
        "paper_id": {"type": str},
        "content": {"type": str},
        "embedding": {"type": list},
    }
