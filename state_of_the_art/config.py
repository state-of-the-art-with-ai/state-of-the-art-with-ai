import os

class Config():
    topics_to_query_arxiv = ['cs', 'ai', 'machine learning', 'cs.AI']
    HOME = os.path.expanduser("~")
    PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers"
    NEW_PAPERS_FOLDER = os.path.expanduser("~")+"/.arxiv_papers_new"

    # the maximum number of papers to compute while sorting the batch of papers
    sort_papers_max_to_compute = 4000
    sort_papers_gpt_model = 'gpt-4-turbo-preview'
    open_ai_key = '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'
    audience_description = """Jean Machado, a Data Science Manager for GetYoruGuide.
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

Topics not interesting to jean are
- Phisics
- Biology
- Medicine
- Astronomy
- Chemistry
    """

    
    @staticmethod
    def load_config():
        return Config()



config = Config.load_config()
