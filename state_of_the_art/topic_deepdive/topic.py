from typing import List
class Topic:
    synonyms: List[str]
    subtopics: List[str]
    semantic_query: str

    def __init__(self, semantic_query, synonyms: List[str] = None, subtopics: List[str] = None) -> None:
        self.semantic_query = semantic_query
        self.synonyms = synonyms
        self.subtopics = subtopics
