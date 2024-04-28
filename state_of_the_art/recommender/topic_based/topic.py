from typing import List, Optional


class Topic:
    synonyms: List[str]
    subtopics: List[str]
    semantic_query: str
    problem_description: str

    def __init__(self, semantic_query: Optional[str] = None, synonyms: List[str] = None, subtopics: List[str] = None, problem_description: Optional[str] =None) -> None:
        self.semantic_query = semantic_query
        self.synonyms = synonyms
        self.subtopics = subtopics
        self.problem_description = problem_description
