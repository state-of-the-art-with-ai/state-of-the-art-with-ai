from typing import Any, List
import os

COMMON_KEYWORDS = [
    'cs.AI', 'cs.LG', 'cs.SI', 'stat.ML',
    'ai', 'machine learning',
    'ads','data science', 'mlops',
    'large language models', 'ai for social good', 'ai ethics'
    'data science management and data science teams  performance', 'ai regulation', 'deep learning & neural nets',
    'computer science','knowledge graphs', 'graph neural networks', 'ai productivity', 'explainable ai', 'xai']

"""
keywords that did not work well
'cs',
'attribution', 
'marketing measurement', 
'experimentation', 
'analytics',
"""

KEYWORS_EXCLUDE = ['physics', 'biology', 'bioinformatics and biomedicine', 'medicine', 'astronomy', 'chemistry',
                   'construction engineering', 'material science', 'robotics', 'mobility', 'geology']


PAPER_TASKS = {
    'top_insights': """Select key insights of the of  article that is provided to you.
Highlight only key insights, ideally actionalable ones. The insights can come form the results of the paper or form literature review
Do not highlight more than 3 insights.
Avoid trivial insights that are common knowledge for your audience.
Avoid salesly insights that are not backed up by data.
Hightlight also insights from the literature review in the paper.

Follow the following example structure when reporting your insights

Insight example 1: "One can understand if networks are modular in neural nets by using a a method using differentiable weight masks" 
More details on how: "using binary weight masks to identify individual weights and subnets
responsible for specific functions testing several standard architectures
and datasets demonstrate how common NNs fail to reuse submodules and offer
new insights into the related issue of systematic generalization on language tasks"
Institution : Microsoft 
Authors: Róbert Csordás, Alex lamb
Relevance: Explain why its relevant
Exact part in text: mention here a few words from the text that support the insight
## end

#start 
    """,
    'methodology': """Summarize the evaluation methodology of the paper claims as conclusions.
Then evaluate: Is the methodoloy of hte claims paper sound? Are there weaknessess? Act like a scientific reviewer and provide a critique of the methodology of the paper

Return an overview and list the possible weakensses of the methodology of the paper
""",
    'literature_review': 'What is the most interesting part of this paper in the literature review?',
    'hardest_part': """ Explain the hardest part technical part of the the paper.
First identify what it is and define it well. Explain terms that are not necessarily explained in the paper but are crucial to understand the hardest part.
Then break down the topic on its parts and explain them as well.
First explain it normally and then explain it in analogies.
No more than 10 sentences.
"""
}

class Audience:
    audience_description: str
    keywords: List[str]
    keywords_to_exclude: List[str]
    time_frame: Any = None
    paper_tasks: dict = PAPER_TASKS

    def __init__(self, *, audience_description: str, keywords: List[str], keywords_to_exclude: List[str],
                 time_frame=None) -> None:
        self.audience_description = audience_description
        self.keywords = keywords
        self.keywords_to_exclude = keywords_to_exclude
        self.time_frame = time_frame

    def get_preferences(self) -> str:
        """
        Returns all the preferences of the profile encoded in a string
        """
        return f"""General Preferences: {self.audience_description}
Important relevant topics: \n - {'\n - '.join(self.keywords)}

Non relevant topics (make sure they are not mentioned in the results): \n - {'\n - '.join(self.keywords_to_exclude)}
        """


jean = Audience(
    audience_description="""Jean Machado, a Data Science Manager for GetYourGuide.
Jean wants the following out this tool:
2. to understand exciting and important topics with further depth
1. to have actionable insights and learnings he can apply
3. to stay on the bleeding edge of the field

to see what is going on on important institutions and companies in the field of data science and machine learning
    """,
    keywords=COMMON_KEYWORDS,
    keywords_to_exclude=KEYWORS_EXCLUDE
)

gdp = Audience(
    audience_description="""
Growth Data Products is a team in GetYourGuide that is responsible for the data science and machine learning for growing the business
You provide insights to GDP manager to share with the team :)
The mission of the team is to  optimize multi-channel customer acquisition and customer loyalty by building data products.
to see what is going on on important institutions and companies in the field of data science and machine learning
    """,
    keywords=COMMON_KEYWORDS,
    keywords_to_exclude=KEYWORS_EXCLUDE
)


def get_current_audience(self=None):
    profiles = {
        'jean': jean,
        'gdp': gdp,
    }
    current_profile = os.environ.get('SOTA_PROFILE', 'jean')
    print(f"Using profile {current_profile}")
    return profiles[current_profile]
