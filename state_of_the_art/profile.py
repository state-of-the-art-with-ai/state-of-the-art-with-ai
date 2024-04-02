
from typing import Any, List
import os

COMMON_KEYWORDS = [
    'cs.AI', 'cs.LG', 'cs.SI', 'stat.ML',
    'cs', 'ai', 'machine learning', 
    'ads', 'attribution', 'marketing measurement', 'data science', 'mlops', 
    'machine learning', 'ai decision making and agents', 'large language models', 'ai for social good', 
    'data science management and data science teams  performance', 'ai regulation', 'deep learning & neural nets',
    'computer science', 'exeperimentation', 'analytics', 'knowledge graphs', 'graph neural networks']

KEYWORS_EXCLUDE = ['physics', 'biology', 'bioinformatics and biomedicine', 'medicine', 'astronomy', 'chemistry', 'construction engineering', 'material science']

class Profile:
    audience_description: str
    keyworkds: List[str]
    keywords_to_exclude: List[str]
    time_frame: Any = None

    def __init__(self, *, audience_description:str, keywords: List[str], keywords_to_exclude: List[str], time_frame=None) -> None:
        self.audience_description = audience_description
        self.keyworkds = keywords
        self.keywords_to_exclude = keywords_to_exclude
        self.time_frame = time_frame
    
    def get_preferences(self) -> str:
        """
        Returns all the preferences of the profile encoded in a string
        """
        return f"""General Preferences: {self.audience_description}
Important relevant Keywords: {'\n - '.join(self.keyworkds)}

Keywords to exclude (do not return any content related to it): {'\n - '.join(self.keywords_to_exclude)}
        """

jean = Profile(
    audience_description="""Jean Machado, a Data Science Manager for GetYoruGuide.
Jean wants the following out this tool:
2. to understand exciting and important topics with further depth
1. to have actionable insights and learnings he can apply
3. to stay on the bleading edge of the field

to see what is going on on important institutions and companies in the field of data science and machine learning
    """,
    keywords = COMMON_KEYWORDS,
    keywords_to_exclude = KEYWORS_EXCLUDE
)


gdp = Profile(
    audience_description="""
Growth Data Products is a team in GetYourGuide that is responsible for the data science and machine learning for growing the business
You provide insights to GDP manager to share with the team :)
The mission of the team is to  optimize multi-channel customer acquisition and customer loyalty by building data products.
to see what is going on on important institutions and companies in the field of data science and machine learning
    """,
    keywords = COMMON_KEYWORDS,
    keywords_to_exclude = ['physics', 'biology', 'medicine', 'astronomy', 'chemistry', 'construction engineering', 'material science', 'football']
)


def get_current_profile(self=None):
    profiles = {
        'jean': jean,
        'gdp': gdp,
    }
    current_profile = 'jean'
    current_profile = os.environ.get('SOTA_PROFILE', 'jean')
    print(f"Using profile {current_profile}")
    return profiles[current_profile]

