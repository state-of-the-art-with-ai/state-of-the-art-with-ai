from state_of_the_art.preferences.audience import Audience
from state_of_the_art.preferences.preferences import SotaPreferences
from state_of_the_art.topic_deepdive.topic import Topic
topics = {
    'deep_learning': Topic(
        synonyms=['deep learning', 'neural networks', 'convolutional neural networks', 'recurrent neural networks',
                  'transformers', 'attention', 'self-attention', 'attention mechanism', 'attention layer'],
        subtopics=['deep learning', 'neural networks', 'convolutional neural networks', 'recurrent neural networks',]
    ),
    'bidding': Topic(
        synonyms=['bidding', 'auction', 'google ads', 'paid search', 'bid optimization', 'bidding', 'bid management', 'bid optimization', 'search engine marketing', 'paid advertising', 'bid', 'portifolio optimization'],
        subtopics=[]
    ),
    'clv':  Topic(
        synonyms=['customer lifetime value', 'clv'],
    ),
    'xsell':  Topic(
        synonyms=['cross sell', 'cross sell recommendations', 'collaborative filtering', 'cross sell optimization'],
        subtopics=['recommnder systems', 'cross sell', 'cross sell recommendation', 'cross sell strategy', 'cross sell optimization']
    ),
    'experimentation': Topic(
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
        synonyms=['data products management', 'data science leadership', 'success metrics'],
        subtopics=[]
    ),
    'coVllaboration': Topic(
        synonyms=['tech teams collaboration beyond immediate team', 'tech organizations cohesion', 'achieving impact beydon the team', 'top performing organization', 'data prodcuts'],
        subtopics=[]
    )
}

paper_questions = {
    'institution': 'Which institution published this paper?',
    'problem_definition': """Which is the key problem the paper is trying to address? Make it simple and focus on the core of the prblem while explaining it.""",
    'top_insights': """What are the key insights of the paper?
Highlight only key insights, ideally actionable ones.
The insights can come form the results of the paper or form literature review
Highlight 3-4 insights.
Avoid trivial insights that are common knowledge for your audience.
Avoid salesly insights that are not backed up by data.
Highlight also insights from the literature review in the paper.
Make sure to mention a literal quote from the paper that supports your insight
    """,
    'literature_review': 'What is the most interesting learning from this paper literature review? Quote the interesting part literally and explain why its interesting',
    'state_of_art_before': 'What was the state of the art before this paper? Analyse and summarize what does the paper mention in the literature review about it?',
    'hardest_part': """What is the more complex part of the paper?
First identify what it is and define it well. Explain terms that are not necessarily explained in the paper but are crucial to understand the hardest part.
Then break down the topic on its parts as they are explained in the paper. Quote literally a phrase form the paper where it talks about it.
First explain it normally and then explain it in analogies.
""",
    'methodology': """Is the methodoloy and claims of the  paper sound? What are the weaknessess? Be skeptical, act like a scientific reviewer and provide a critique of the methodology of the paper""",
    'main_finding': """What is the main finding of this paper? """,
    'do_i_want_to_read_this': 'As a human being with limited time should i read this paper or should I look into others instead? Give a confidence score from 0 to 100 if i should read it and explain why',
}


jean = Audience(
    audience_description="""Jean Machado, a Data Science Manager for GetYourGuide.
Jean wants the following out this tool:
2. to understand exciting and important topics with further depth
1. to have actionable insights and learnings he can apply
3. to stay on the bleeding edge of the field

to see what is going on on important institutions and companies in the field of data science and machine learning
    """,
    paper_questions=paper_questions,
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

gdp = Audience(
    audience_description="""
Growth Data Products is a team in GetYourGuide that is responsible for the data science and machine learning for growing the business
You provide insights to GDP manager to share with the team :)
The mission of the team is to  optimize multi-channel customer acquisition and customer loyalty by building data products.
to see what is going on on important institutions and companies in the field of data science and machine learning
    """,
    paper_questions=paper_questions,
    topics=topics,
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
    topics=topics,
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
    topics=topics,
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
    topics=topics,
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
    topics=topics,
)

mlp = Audience(
    audience_description="""
    Machine learning platform team
    
    Has the following mission
    Enable data scientists and engineers to deliver production-ready data products faster and reliably by leveraging MLOps best practices providing self-service tools and automation. 

""",
    topics=topics,
)

sota_preferences = SotaPreferences(audiences={'jean': jean, 'gdp': gdp, 'art': art, 'sdp': sdp, 'tdp': tdp, 'mlp': mlp})
