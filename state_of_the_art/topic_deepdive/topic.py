
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


bidding = Topic(
    synonyms=['bidding', 'google ads', 'paid search', 'bid optimization', 'bidding', 'bid management', 'bid optimization', 'search engine marketing', 'paid advertising', 'bid', 'portifolio optimization'],
    subtopics=[]
)

experimentation = Topic(
    synonyms=['experimentation', 'experiment design', 'experiment analysis', 'experimentation and reporting'],
    subtopics=['markov chain attribution', 'marketing measurement', 'marketing metrics', 'marketing analytics', 'marketing attribution', 'marketing ROI', 'mc roas', 'markov chain attribution']
)

management_dataproduct = Topic(
    synonyms=['data products management', 'data science leadership', 'success metrics'],
    subtopics=[]
)

collaboration = Topic(
    synonyms=['tech teams collaboration beyond immediate team', 'tech organizations cohesion', 'achieving impact beydon the team', 'top performing organization', 'data prodcuts'],
    subtopics=[]
)

topics = {
    'deep_learning': deep_learning,
    'xsell': xsell,
    'bidding': bidding,
    'experimentation': experimentation,
    'management_dataproduct': management_dataproduct,
    'collaboration': collaboration
}