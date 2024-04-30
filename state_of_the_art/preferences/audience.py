class Audience():
    DEFAULT_KEYWORS_EXCLUDE = ['physics', 'biology', 'bioinformatics and biomedicine', 'medicine', 'astronomy',
                               'chemistry',
                               'construction engineering', 'material science', 'robotics', 'mobility', 'geology',
                               'electrical engineering']

    DEFAULT_KEYWORDS_OF_INTEREST = None

    DEAFULT_DESCRIPTION = """Data Science and AI experts and enthusiasts"""

    DEFAULT_PAPER_QUESTIONS = {
        'institution': 'Which institution published this paper?',
        'explain_me': 'Guide me through understanding the main point of the paper even if you are not 100% in the topic',
        'top_insights': """What are the key insights of the paper?
    Highlight only key insights, ideally actionable ones.
    The insights can come form the results of the paper or form literature review
    Highlight 3-5 insights.
    Avoid trivial insights that are common knowledge for your audience.
    Avoid salesly insights that are not backed up by data.
    Highlight also insights from the literature review in the paper.
    Make sure to mention a literal quote from the paper that supports your insight
        """,
        'literature_review': 'What is the most interesting learning from this paper literature review? Quote the interesting part literally and explain why its interesting',
        'hardest_part': """What is the more complex part of the paper?
        First identify what it is and define it well. Explain terms that are not necessarily explained in the paper but are crucial to understand the hardest part.
        Then break down the topic on its parts as they are explained in the paper. Quote literally a phrase form the paper where it talks about it.
        First explain it normally and then explain it in analogies.
        """,
        'methodology': """Is the methodoloy and claims of the  paper sound? What are the weaknessess? Be skeptical, act like a scientific reviewer and provide a critique of the methodology of the paper""",
        'recommended_actions': """What are top actions recommended as learnings from this paper? """,
    }

    def __init__(self, audience_description=None, keywords=None, keywords_to_exclude=None, paper_questions=None,
                 topics=None, name=None):
        self.audience_description = audience_description if audience_description else Audience.DEAFULT_DESCRIPTION
        self.keywords = keywords if keywords else Audience.DEFAULT_KEYWORDS_OF_INTEREST
        self.keywords_to_exclude = keywords_to_exclude if keywords_to_exclude else Audience.DEFAULT_KEYWORS_EXCLUDE
        self.paper_questions = paper_questions if paper_questions else Audience.DEFAULT_PAPER_QUESTIONS
        if topics and type(topics) != dict:
            raise ValueError("topics should be a dict, found ", type(topics))

        self.topics = topics
        self.name = name

    def get_topics(self) -> dict:
        return self.topics

    def get_preferences(self) -> str:
        """
        Returns all the preferences of the profile encoded in a string
        """

        if self.keywords:
            keywords_str = f"""Important relevant topics: \n - {'\n - '.join(self.keywords)}
           """
        else:
            keywords_str = ""

        return f"""{self.audience_description}
{keywords_str}
Non relevant topics (make sure they are not mentioned in the results): \n - {'\n - '.join(self.keywords_to_exclude)}
        """
