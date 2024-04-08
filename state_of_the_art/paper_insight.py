
from state_of_the_art.paper_miner import ArxivMiner
from state_of_the_art.config import config
import sys
from state_of_the_art.open_ai_utils import calculate_cost
from state_of_the_art.paper import Paper

class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """
    def extract(self, url: str):

        local_location = Paper(arxiv_url=url).download()


        from pypdf import PdfReader

        reader = PdfReader(local_location)
        number_of_pages = len(reader.pages)
        page = reader.pages[0]
        PAPER_CONTENT = ""
        for page in reader.pages:
            PAPER_CONTENT += page.extract_text()

        print(PAPER_CONTENT)

        print("Number of pages: ", number_of_pages)
        print("Number of characters: ", len(PAPER_CONTENT))
        print("Number of tokens: ", len(PAPER_CONTENT)/4)
        cost = calculate_cost(chars_input=len(PAPER_CONTENT), chars_output=4000)

        user_input = input(f"Do you want ton continue to generate insights at a cost of $ {cost}? Type c to continue \n")
        if user_input != 'c':
            print("Aborting")
            sys.exit(1)


        prompt = f"""You are an world class expert in Data Science and computer science.
Your taks is selecting key insights of the state of the art in academia an in the industry via the content of the article that is provided to you.
Highlight only key insights, ideally actionalable ones. The insights can come form the results of the paper or form literature review
Do not highlight more than 3 insights.
you Optimize your suggestions to the following audience: {config.get_current_profile().get_preferences()}
Avoid trivial insights that are common knowledge for your audience.
Avoid salesly insights that are not backed up by data.
Hightlight also inishgts from the literature review in the paper.

Follow the folloinwg example structure when reporting your insights

Insight example: ##start

Insight example 1: "One can understand if networks are modular in neural nets by using a a method using differentiable weight masks" 
More details on how: "using binary weight masks to identify individual weights and subnets
responsible for specific functions testing several standard architectures
and datasets demonstrate how common NNs fail to reuse submodules and offer
new insights into the related issue of systematic generalization on language tasks"
Institution : Microsoft 
Authors: Róbert Csordás, Alex lamb
Arxiv Paper : {url} (use this literal value always)
Relevance: Explain why its relevant
Exact part in text: mention here a few words from the text that support the insight

## end

Article to extract insights now starts: ##start
{{text}}
## end of article to extract insights


Now begings the Insight extraction: ##start"""


        from langchain import PromptTemplate, LLMChain
        from langchain_community.chat_models import ChatOpenAI

        PROMPT_TWEET = PromptTemplate(template=prompt, input_variables=["text"])
        llm = ChatOpenAI(temperature=0.0, model=config.sort_papers_gpt_model, openai_api_key=config.open_ai_key)
        chain =LLMChain(llm=llm, prompt=PROMPT_TWEET, verbose=True)
        # two weeks ago
        result = chain.run(PAPER_CONTENT)

        print(result)

        from tiny_data_wharehouse.data_wharehouse import DataWharehouse
        tdw = DataWharehouse()
        tdw.write_event('sota_paper_insight', {'pdf_url': url, 'insights': result, 'prompt': prompt})
