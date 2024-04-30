from typing import List, Optional


class Topic:
    synonyms: List[str]
    subtopics: List[str]
    semantic_query: str
    problem_description: str
    arxiv_search_keywords: List[str]

    def __init__(self, semantic_query: Optional[str] = None, synonyms: List[str] = None, subtopics: List[str] = None, problem_description: Optional[str] =None, arxiv_search_keywords = None) -> None:
        self.semantic_query = semantic_query
        self.synonyms = synonyms
        self.subtopics = subtopics
        self.problem_description = problem_description
        self.arxiv_search_keywords = arxiv_search_keywords

    def get_arxiv_search_keywords(self) -> List[str]:
        if not self.arxiv_search_keywords:
            return []
        return self.arxiv_search_keywords
