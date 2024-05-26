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
    DEFAULT_KEYWORDS_OF_INTEREST = None
    DEAFULT_DESCRIPTION = """Data Science and AI experts and enthusiasts"""

    DEFAULT_PAPER_QUESTIONS = {
        "institution": "Which institution published this paper?",
        "explain": "Guide me through understanding the main points of the article. Explain if i had to explain it to a 10 year old",
        "top_insights": """What are the most relevant learnings of the paper? Highlight key insights. The insights can come form the results of the paper and form literature review Highlight 3-6 insights. Avoid trivial or salesly insights that are common knowledge for your audience or not backed by data. Highlight also insights from the literature review in the paper. Make sure to mention a literal quote from the paper that supports your insight""",
        "recommended_actions": """What are top actions recommended as learnings from this paper? """,
        "future": """What are the implications of this work for the future? How the future can look like if the claims and direction here fully develop in the next 1, 3 and 10 years? """,
        "time_to_understanding": """how long do you think it would take for a person to understand the paper in minutes?""",
        "literature_review": "What is the most interesting learning from this paper literature review? Quote the interesting part literally and explain why its interesting",
        "hardest_part": """What is the more complex part of the paper?
        First identify what it is and define it well. Explain terms that are not necessarily explained in the paper but are crucial to understand the hardest part.
        Then break down the topic on its parts as they are explained in the paper. Quote literally a phrase form the paper where it talks about it.
        First explain it normally and then explain it in analogies.
        """,
        "methodology": """Is the methodoloy and claims of the  paper sound? What are the weaknessess? Be skeptical, act like a scientific reviewer and provide a critique of the methodology of the paper""",
    }

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
        self.keywords = keywords if keywords else Audience.DEFAULT_KEYWORDS_OF_INTEREST
        self.keywords_to_exclude = (
            keywords_to_exclude
            if keywords_to_exclude
            else Audience.DEFAULT_KEYWORS_EXCLUDE
        )
        self.paper_questions = (
            paper_questions if paper_questions else Audience.DEFAULT_PAPER_QUESTIONS
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

        if self.keywords:
            keywords_str = f"""Important relevant topics: \n - {'\n - '.join(self.keywords)}
           """
        else:
            keywords_str = ""

        keywords_to_exclude_str = (
            f"""Non relevant topics (make sure they are not mentioned in the results): \n - {'\n - '.join(self.keywords_to_exclude)}"""
            if include_keywords_to_exclude
            else ""
        )

        return f"""{self.audience_description}
{keywords_str}
{keywords_to_exclude_str}
        """
