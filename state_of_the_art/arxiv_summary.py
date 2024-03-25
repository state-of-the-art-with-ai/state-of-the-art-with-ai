import datetime

from state_of_the_art.arxiv_utils import arxiv_search


def summarize_papers():
    MAX_ARTICLES_TO_RETURN=7
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
- MLops
- analytics
- Data Science
- Machine Learning
- Large language models
- Ai for social good
- Knowledge graphs
- Data science management
- Deep Learning
- Computer science
- exeperimentation

Focus on computer science avoid other areas like:
- Phisics
- Biology
- Chemistry
- Medicine
- Astronomy

Sort the papers from most relevant to less, return not more than {MAX_ARTICLES_TO_RETURN}
The articles for you to work with will be provided below in the following format (Title, Abstract, URL)
the order they are provided is not optimized, figure out the best order to present them to Jean.
Articles:
##start {{text}} ##end

Expected Output Format: ##start
(Relevance score of recommendation) Title: the title
Summary: Summary of the article which conveys the main learning one can get about it (max 80 words)
Relevance: Why its relevant for jean (max 25 words)
Arxiv URL: the article url
##end

Example: ##start

(0.9) Title: "A new approach to MLOps"
Summary: <the summary>
Relevance: Relevant because it presents a new approach to MLOps and could change how GetYourGuide deploys models.
Arxiv URL: the article url

(0.7) Title: "a new mixed of experts llm breaking bechmarks"
Summary: <the summary>
Relevance: "Relevant because it presents a new large language model that could be used to improve quality and speed of delivery of recommendation system"
Arxiv URL: the article url
##end

Output: ##start
    """

    from langchain import PromptTemplate, LLMChain
    from langchain_community.chat_models import ChatOpenAI

    PROMPT_TWEET = PromptTemplate(template=prompt, input_variables=["text"])
    QUERY = "data science"
    MAX_RESULTS = 50
    llm = ChatOpenAI(temperature=0.0, model='gpt-4-turbo-preview', openai_api_key='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')
    chain =LLMChain(llm=llm, prompt=PROMPT_TWEET,verbose=True)

    articles = arxiv_search(query=QUERY, max_results=MAX_RESULTS, short_version=False)

    result = chain.run(articles)
    print(f"\n Results generated at {datetime.datetime.now().isoformat()} : \n\n")
    print(result)




if __name__ == "__main__":
    summarize()
