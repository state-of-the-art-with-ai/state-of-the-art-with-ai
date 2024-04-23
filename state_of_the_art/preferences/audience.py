
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


DEAFULT_DESCRIPTION = """
The broad public interested in the latest developments in the field of data science and machine learning.
"""

class Audience():
    def __init__(self, audience_description = None, keywords = None, keywords_to_exclude = None):
        self.audience_description = audience_description if audience_description else DEAFULT_DESCRIPTION
        self.keywords = keywords if keywords else COMMON_KEYWORDS
        self.keywords_to_exclude = keywords_to_exclude if keywords_to_exclude else KEYWORS_EXCLUDE

    def get_preferences(self) -> str:
        """
        Returns all the preferences of the profile encoded in a string
        """
        return f"""General Preferences: {self.audience_description}
Important relevant topics: \n - {'\n - '.join(self.keywords)}

Non relevant topics (make sure they are not mentioned in the results): \n - {'\n - '.join(self.keywords_to_exclude)}
        """
