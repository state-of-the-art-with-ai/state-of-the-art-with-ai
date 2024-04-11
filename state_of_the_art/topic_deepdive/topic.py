from typing import List

class Topic:
    synonyms: List[str]
    subtopics: List[str]

    def __init__(self, synonyms: List[str], subtopics: List[str] = None) -> None:
        self.synonyms = synonyms
        self.subtopics = subtopics
