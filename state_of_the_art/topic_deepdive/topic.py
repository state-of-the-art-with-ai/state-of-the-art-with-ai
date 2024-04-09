
from typing import List

class Topic:
    synonyms: List[str]
    subtopics: List[str]

    def __init__(self, synonyms: List[str], subtopics: List[str] = None) -> None:
        self.synonyms = synonyms
        self.subtopics = subtopics

deep_learning = Topic(
    synonyms=['deep learning', 'neural networks', 'convolutional neural networks', 'recurrent neural networks',
              'transformers', 'attention', 'self-attention', 'attention mechanism', 'attention layer'],
    subtopics=['deep learning', 'neural networks', 'convolutional neural networks', 'recurrent neural networks',]
)

xsell = Topic(
    synonyms=['cross sell', 'cross sell recommendations', 'collaborative filtering', 'cross sell optimization'],
    subtopics=['recommnder systems', 'cross sell', 'cross sell recommendation', 'cross sell strategy', 'cross sell optimization']
)

marketing_measurment = Topic(
    synonyms=['marketing measurement', 'marketing metrics', 'marketing analytics', 'marketing attribution', 'marketing ROI'],
    subtopics=[]
)

bidding = Topic(
    synonyms=['bidding', 'bid optimization', 'bidding', 'bid management', 'bid optimization'],
    subtopics=['bidding', 'bid optimization', 'bidding strategy', 'bid management', 'bid optimization']
)

experimentation_and_reporting = Topic(
    synonyms=['experimentation', 'experiment design', 'experiment analysis', 'experimentation and reporting'],
    subtopics=[]
)

topics = {
    'deep_learning': deep_learning,
    'xsell': xsell,
    'marketing_measurment': marketing_measurment,
    'bidding': bidding,
    'experimentation': experimentation_and_reporting
}