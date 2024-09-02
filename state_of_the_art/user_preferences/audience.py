from state_of_the_art.user_preferences.default_questions import DEFAULT_PAPER_QUESTIONS


class Audience:
    DEFAULT_KEYWORS_EXCLUDE = [
        "physics",
        "biology",
        "bioinformatics and biomedicine",
        "medicine",
        "astronomy",
        "chemistry",
        "construction engineering",
        "material science",
        "robotics",
        "mobility",
        "geology",
        "electrical engineering",
    ]
    DEAFULT_DESCRIPTION = """Data Science and AI experts and enthusiasts"""

    def __init__(
        self,
        audience_description=None,
        keywords=None,
        keywords_to_exclude=None,
        paper_questions=None,
        topics=None,
        name=None,
    ):
        self.audience_description = (
            audience_description
            if audience_description
            else Audience.DEAFULT_DESCRIPTION
        )
        self.keywords_to_exclude = (
            keywords_to_exclude
            if keywords_to_exclude
            else Audience.DEFAULT_KEYWORS_EXCLUDE
        )
        self.paper_questions = (
            paper_questions if paper_questions else DEFAULT_PAPER_QUESTIONS
        )
        if topics and not isinstance(topics, dict):
            raise ValueError("topics should be a dict, found ", type(topics))

        self.topics = topics
        self.name = name

    def get_topics(self) -> dict:
        return self.topics

    def get_preferences(self, include_keywords_to_exclude=True) -> str:
        """
        Returns all the preferences of the profile encoded in a string
        """

        keywords_to_exclude_str = (
            f"""Non relevant topics (make sure they are not mentioned in the results): \n - {'\n - '.join(self.keywords_to_exclude)}"""
            if include_keywords_to_exclude
            else ""
        )

        return f"""{self.audience_description}
{keywords_to_exclude_str}
        """
