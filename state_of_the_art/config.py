


class Config():
    topics_to_query_arxiv = ['cs', 'ai', 'machine learning', 'cs.AI']
    # the maximum number of papers to compute while sorting the batch of papers
    sort_papers_max_to_compute = 4000
    sort_papers_gpt_model = 'gpt-4-turbo-preview'
    open_ai_key = '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'

    
    @staticmethod
    def load_config():
        return Config()



config = Config.load_config()
