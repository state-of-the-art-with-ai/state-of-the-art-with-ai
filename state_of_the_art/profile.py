
from typing import Any, List

class Profile:
    audience_description: str
    arxiv_topics: List[str]
    time_frame: Any = None

    def __init__(self, *, audience_description:str, arxiv_topics: List[str], time_frame=None) -> None:
        self.audience_description = audience_description
        self.arxiv_topics = arxiv_topics
        self.time_frame = time_frame

jean = Profile(
    audience_description="""Jean Machado, a Data Science Manager for GetYoruGuide.
Jean wants the following out this tool:
2. to understand exciting and important topics with further depth
1. to have actionable insights and learnings he can apply
3. to stay on the bleading edge of the field

Highlight only topics that are exciting so you maximize the likelihood of Jean reading the paper if relevant.
You prefer highly regarded publications rather than unkwown ones.

Some topics interesting for Jean.
- Data Science
- MLops
- Machine Learning
- Ai decision making and agents
- Large language models
- Ai for social good
- Data science management and data science teams  performance
- Ai regulation
- Deep Learning & neural nets
- Computer science
- exeperimentation
- analytics
- Knowledge graphs
- Graph neural networks

Topics not interesting to jean are
- Phisics
- Biology
- Medicine
- Astronomy
- Chemistry
- construction engineering
- material science
    """,
    arxiv_topics = ['cs', 'ai', 'machine learning', 'cs.AI', 'cs.LG', 'cs.SI', 'stat.ML']
)


gdp = Profile(
    audience_description="""
Growth Data Products is a team in GetYourGuide that is responsible for the data science and machine learning for growing the business
You provide insights to GDP manager to share with the team :)
The mission of the team is to  optimize multi-channel customer acquisition and customer loyalty by building data products.
    """,
    arxiv_topics = ['cs', 'ai', 'machine learning', 'cs.AI', 'cs.LG', 'cs.SI', 'stat.ML']
)


def get_current_profile(self=None):
    profiles = {
        'jean': jean,
        'gdp': gdp,
    }
    current_profile = 'jean'
    print(f"Using profile {current_profile}")
    return profiles[current_profile]

