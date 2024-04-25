from state_of_the_art.preferences.audience import Audience
from state_of_the_art.preferences.preferences import SotaPreferences
from state_of_the_art.topic_deepdive.topic import Topic
topics = {
    'deep_learning': Topic(
        semantic_query='deep learning neural networks',
        synonyms=['deep learning', 'neural networks', 'convolutional neural networks', 'recurrent neural networks',
                  'transformers', 'attention', 'self-attention', 'attention mechanism', 'attention layer'],
        subtopics=['deep learning', 'neural networks', 'convolutional neural networks', 'recurrent neural networks',]
    ),
    'bidding': Topic(
        semantic_query='bid bidding',
        synonyms=['bidding', 'auction', 'google ads', 'paid search', 'bid optimization', 'bidding', 'bid management', 'bid optimization', 'search engine marketing', 'paid advertising', 'bid', 'portifolio optimization'],
        subtopics=[]
    ),
    'clv':  Topic(
        semantic_query='customer lifetime value clv',
        synonyms=['customer lifetime value', 'clv'],
    ),
    'xsell':  Topic(
        semantic_query='cross sell collaborative filtering',
        synonyms=['cross sell', 'cross sell recommendations', 'collaborative filtering', 'cross sell optimization'],
        subtopics=['recommnder systems', 'cross sell', 'cross sell recommendation', 'cross sell strategy', 'cross sell optimization']
    ),
    'experimentation': Topic(
        semantic_query='ab test experimentation online controlled experiments',
        synonyms=[
            'experimentation',
            'ab-test',
            'experiment design', 'experiment analysis', 'experimentation and reporting'],
        subtopics=[
                    'statistical signficance', 'ab-test', 'experiment design', 'experiment analysis', 'experimentation and reporting'
                    'markov chain attribution', 'marketing measurement',
                   'marketing metrics',
                   'marketing analytics',
                   'marketing attribution',
                   'marketing ROI', 'mc roas', 'markov chain attribution']
    ),
    'management_dataproduct': Topic(
        semantic_query='data products management',
        synonyms=['data products management', 'data science leadership', 'success metrics'],
        subtopics=[]
    ),
    'collaboration': Topic(
        semantic_query='tech teams collaboration beyond immediate team in tech organizations',
        synonyms=['tech teams collaboration beyond immediate team', 'tech organizations cohesion', 'achieving impact beydon the team', 'top performing organization', 'data prodcuts'],
        subtopics=[]
    )
}



gdp = Audience(
    audience_description="""
Growth Data Products is a team in GetYourGuide that is responsible for the data science and machine learning for growing the business
You provide insights to GDP manager to share with the team :)
The mission of the team is to  optimize multi-channel customer acquisition and customer loyalty by building data products.
to see what is going on on important institutions and companies in the field of data science and machine learning
    """,
)


art = Audience(
    audience_description="""
    The activity ranking team team has the following mission:
    We provide customers with a highly relevant and personalized ranking of activities to make easier purchase decisions. We also enable our suppliers to grow through a fair assessment of their activities.
    Responsibilities
    Search ranking logic:
    Global baseline ranking used on GYG web (POIs and search results), native apps and partner widget
    Ranking service used to fine tune the global ranking for each request based on request context
""",
)

sdp = Audience(
    audience_description="""
    the supply data products team has the following mission:
    Our mission is to build impactful data products to automate, advance, and empower our supply domain.
    
revelant topics examples are:
demand forecast
inventory management
coverage of locations
catalog

""",
)
tdp = Audience(
    audience_description="""
    The traveler data products team has the following mission:
Develop data driven capabilities to support scaling and optimization of products in the traveler group domain of GYG.

Entity Ranking:
Logic to rank collection filters, POIs, … on Destination Pages
Entity Ranking Service
(Similar) Recommendations
Recommendations model logic
Reco service incl. ADP user history
Query Understanding
""",
)

tdp = Audience(
    audience_description="""
    The traveler data products team has the following mission:
Develop data driven capabilities to support scaling and optimization of products in the traveler group domain of GYG.

Entity Ranking:
Logic to rank collection filters, POIs, … on Destination Pages
Entity Ranking Service
(Similar) Recommendations
Recommendations model logic
Reco service incl. ADP user history
Query Understanding
""",
)

mlp = Audience(
    audience_description="""
    Machine learning platform team
    Has the following mission
    Enable data scientists and engineers to deliver production-ready data products faster and reliably by leveraging MLOps best practices providing self-service tools and automation. 

""",
)
jean = Audience(
    audience_description=f"""Jean Machado, a Data Science Manager for GetYourGuide.
Jean wants the following out this tool:
2. to understand exciting and important topics with further depth
1. to have actionable insights and learnings he can apply in his teams
3. to stay on the bleeding edge of the field

to see what is going on on important institutions and companies in the field of data science and machine learning.

Jean manages the following teams in GetYourGuide:
{gdp.audience_description}

and 

{mlp.audience_description}

    """,
    topics=topics,
    keywords=['cs.AI', 'cs.LG', 'cs.SI', 'stat.ML',
              'ai', 'machine learning',
              'data science',
              'large language models',
              'ai for social good',
              'ai ethics'
              'data science management and data science teams  performance',
              'ai regulation',
              'deep learning & neural nets',
              'mlops',
              'ads',
              'computer science',
              'knowledge graphs',
              'graph neural networks',
              'ai productivity',
              'explainable ai',
              'xai'
              ]

)

sota_preferences = SotaPreferences(audiences={'jean': jean, 'gdp': gdp, 'art': art, 'sdp': sdp, 'tdp': tdp, 'mlp': mlp}, default_profile='jean')
