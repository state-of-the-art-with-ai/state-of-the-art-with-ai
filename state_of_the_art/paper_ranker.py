
import os
import sys
import datetime
from typing import Optional
from state_of_the_art.arxiv_utils import load_papers_between_published_dates

from state_of_the_art.config import config



def rank_by_relevance(*, from_date: Optional[str]=None, look_back_days=7, dry_run=False):
    MAX_ARTICLES_TO_RETURN=15
    prompt = f"""You are an world class expert in Data Science and MLOPs.
Your taks is spotting key insights of what is going on in academia an in the industry via arxiv articles provided to you.
Your audience is Jean Machado, a Data Science Manager for GetYoruGuide.
Jean wants the following out of this summaries:
1. to have actionable insights and learnings he can apply
2. to understand exciting and important topics with further depth
3. to stay on the bleading edge of the field
Highlight only topics that are exciting so you maximize the likelihood of Jean reading the paper if relevant.
You prefer highly regarded publications rather than unkwown ones.

Some topics interesting for Jean.
- Data Science
- MLops
- Machine Learning
- Large language models
- Ai for social good
- Ai regulation
- Deep Learning
- Knowledge graphs
- Data science management
- Computer science
- exeperimentation
- analytics

Try also to include meta-analysis and reviews of the field.

Focus on computer science avoid other areas like:
- Phisics
- Biology
- Chemistry
- Medicine
- Astronomy

Sort the papers from most relevant to less, return not more than {MAX_ARTICLES_TO_RETURN}
The articles for you to work with will be provided below in the following format (Title, URL)
the order they are provided is not optimized, figure out the best order to present them to Jean.
Articles:
##start {{text}} ##end

Expected Output Format: ##start
(Relevance score of recommendation) Title: the title
Relevance: Why it my be relevant for jean (max 20 words)
Arxiv URL: the article url
##end

Example: ##start

(0.9) Title: "A new approach to MLOps" 
Arxiv URL: the article url
Relevance: Relevant because it presents a new approach to MLOps and could change how GetYourGuide deploys models.

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
    to_date = datetime.date.today().isoformat()
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
    papers = load_papers_between_published_dates(from_date, to_date)
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
