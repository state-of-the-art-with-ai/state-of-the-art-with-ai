
import os
import sys
import datetime
from typing import Optional

from state_of_the_art.config import config
from state_of_the_art.papers import PapersData



def rank_by_relevance(*, from_date: Optional[str]=None, to_date: Optional[str]=None, look_back_days=7, dry_run=False):
    """
    Ranks existing papers by relevance
    """

    MAX_ARTICLES_TO_RETURN=15
    prompt = f"""You are an world class expert in Data Science and computer science.
Your taks is spotting key insights of what is going on in academia an in the industry via arxiv articles provided to you.
Your audience is 
{config.audience_description}
Sort the papers from most relevant to less, return not more than {MAX_ARTICLES_TO_RETURN}
Highlight only topics that are exciting or import so you reading the paper.
The articles for you to work with will be provided below in the following format (Title, URL)
the order they are provided is not optimized, figure out the best order to present them to your audience.

Try also to include meta-analysis and reviews of the field.

Articles:
##start {{text}} ##end

Expected Output Format: ##start
Title: (Relevance score of recommendation) The title
Relevance: Why it my be relevant for jean (max 20 words)
Arxiv URL: the article url
##end

Example: ##start

(0.9) Title: "A new approach to ml pipeline testing" 
Arxiv URL: the article url
Relevance: Relevant because it presents a new approach to testing pipelines and could change how production systems are built.

(0.7) Title: "a new mixed of experts llm breaking bechmarks"
Relevance: "Relevant because it presents a new large language model that could be used to improve quality and speed of delivery of recommendation system"
Arxiv URL: the article url
##end

Output: ##start
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
    articles = get_articles_str(max_papers, from_date, to_date)

    user_input = input(f"Will generate a summary from {max_papers} articles between {from_date} and {to_date}. Press c to continue \n")
    if user_input != 'c':
        print("Aborting")
        sys.exit(1)


    if not dry_run:
        result = chain.run(articles)
    else:
        result = "Dry run result"

    result = f"Results generated at {datetime.datetime.now().isoformat()} for period ({from_date}, {to_date}): \n\n" + result
    from tiny_data_wharehouse.data_wharehouse import DataWharehouse
    tdw = DataWharehouse()
    if not dry_run:
        tdw.write_event('state_of_the_art_summary', {'summary': result, 'from_date': from_date, 'to_date': to_date, 'prompt': prompt })
    print(result)


def get_articles_str(max_papers, from_date, to_date)->str:
    papers = PapersData().load_between_dates(from_date, to_date)
    print("Found  ", len(papers), " articles with date filters")
    papers = papers[0:max_papers]

    papers_str = " "
    for i in papers.iterrows():
        papers_str += f"""
Title: {i[1]['title']}
Arxiv URL: {i[1]['url']}
        """
    return papers_str

if __name__ == "__main__":
    import fire
    fire.Fire()
