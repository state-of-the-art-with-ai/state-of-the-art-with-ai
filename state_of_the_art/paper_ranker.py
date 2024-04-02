
import sys
import datetime
from typing import Optional, Any

from state_of_the_art.config import config
from state_of_the_art.papers import PapersData
from state_of_the_art.open_ai_utils import calculate_cost

class RankGeneratedData:
    prompt: str
    from_date: Any
    to_date: Any
    summary: str


    def __init__(self, from_date, to_date, prompt, summary=None) -> None:
        self.from_date = from_date
        self.to_date = to_date
        self.prompt = prompt
        self.summary = summary

    def to_dict(self):
        return {'summary': self.summary, 'from_date': self.from_date, 'to_date': self.to_date, 'prompt': self.prompt }


def rank(*, from_date: Optional[str]=None, to_date: Optional[str]=None, look_back_days=7, dry_run=False):
    """
    Ranks existing papers by relevance
    """
    print("Look back days ", look_back_days)

    MAX_ARTICLES_TO_RETURN=15
    prompt = f"""You are an world class expert in Data Science and computer science.
Your taks is spotting key insights of what is going on in academia an in the industry via arxiv articles provided to you.
Your audience is {config.get_current_profile().audience_description}
Highlight only topics that are exciting or import so you reading the paper.
The articles for you to work with will be provided below in the following format (Title, Abstract, URL)
the order they are provided is not optimized, figure out the best order to present them to your audience.
Do not be biased by the given order of the papers, it does not mean more recent is more relevant.
Sort the papers from most relevant to less, return not more than {MAX_ARTICLES_TO_RETURN}
Try also to include meta-analysis and reviews of the field.

Example of expected output format: ##start

(0.9) Title: "A new approach to ml pipeline testing" 
Arxiv URL: the article url
Relevance: Relevant because it presents a new approach to testing pipelines and could change how production systems are built.

(0.7) Title: "a new mixed of experts llm breaking bechmarks"
Relevance: "Relevant because it presents a new large language model that could be used to improve quality and speed of delivery of recommendation system"
Arxiv URL: the article url
## end of example


Articles to rank
##start {{text}} ##end of articles


Ranked output of articles: ##start
    """

    from langchain import PromptTemplate, LLMChain
    from langchain_community.chat_models import ChatOpenAI

    PROMPT_TWEET = PromptTemplate(template=prompt, input_variables=["text"])
    llm = ChatOpenAI(temperature=0.0, model=config.sort_papers_gpt_model, openai_api_key=config.open_ai_key)
    chain =LLMChain(llm=llm, prompt=PROMPT_TWEET,verbose=True)
    
    # two weeks ago
    from_date = from_date if from_date else (datetime.date.today() - datetime.timedelta(days=look_back_days)).isoformat()
    to_date = to_date if to_date else datetime.date.today().isoformat()
    max_papers = config.sort_papers_max_to_compute

    articles = PapersData().load_between_dates(from_date, to_date)
    print("Found  ", len(articles), f" articles with date filters but filtering down to {max_papers} ")
    articles = articles[0:max_papers]
    articles_str = get_articles_str(articles)
    cost = calculate_cost(chars_input=len(articles), chars_output=4000)

    user_input = input(f"""Ranking generation of ({len(articles.index)}) articles from {from_date} to {to_date} cost estimate ${cost}.
Press c to continue: """)
    if user_input != 'c':
        print("Aborting")
        sys.exit(1)


    if not dry_run:
        result = chain.run(articles_str)
    else:
        result = "Dry run result"

    result = f"Results generated at {datetime.datetime.now().isoformat()} for period ({from_date}, {to_date}): \n\n" + result
    from tiny_data_wharehouse.data_wharehouse import DataWharehouse
    tdw = DataWharehouse()
    ranking_data = RankGeneratedData(from_date=from_date, to_date=to_date, prompt=prompt, summary=result)
    if not dry_run:
        tdw.write_event('state_of_the_art_summary', ranking_data.to_dict())
    print(result)


def get_articles_str(papers)->str:

    papers_str = " "
    for i in papers.iterrows():
        papers_str += f"""
Title: {i[1]['title']}
Abstract: {i[1]['abstract'][0:config.MAX_ABSTRACT_SIZE_RANK]}
Arxiv URL: {i[1]['url']}
Published: {str(i[1]['published']).split(' ')[0]}
        """
    return papers_str

if __name__ == "__main__":
    import fire
    fire.Fire()
