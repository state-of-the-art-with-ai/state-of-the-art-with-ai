
from state_of_the_art.arxiv_utils import download_paper
from state_of_the_art.config import config
import sys

class InsightExtractor:
    def extract(self, pdf_file: str):
        local_location = download_paper(pdf_file)

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

        user_input = input(f"Do you want ton continue to generate insights? Type c to continue \n")
        if user_input != 'c':
            print("Aborting")
            sys.exit(1)


        prompt = f"""You are an world class expert in Data Science and computer science.
    Your taks is selecting key insights of the state of the art in academia an in the industry via the content of the article that is provided to you.
    Highlight only key insights, ideally actionalable ones. The insights can come form the results of the paper or form literature review
    Do not highlight more than 3 insights.
    you Optimize your suggestions to:

    {config.audience_description}

    Follow the follinwg example structure when reporting your insights
    Insight extraction example: ##start

    Insight example 1: "One can understand if networks are modular in neural nets by using a a method using differentiable weight masks" 
    More details on how: "using binary weight masks to identify individual weights and subnets
responsible for specific functions testing several standard architectures
and datasets demonstrate how common NNs fail to reuse submodules and offer
new insights into the related issue of systematic generalization on language tasks"
    Institution : Microsoft 
    Authors: Róbert Csordás, Alex lamb
    Arxiv Paper : {pdf_file} (use this literal value always)
    Relevance: Explain why its relevant

    ## end

    Article to extract inisghts now starts: ##start
    {{text}}
    ## end of article ontent


    Now begings the Insight extraction: ##start
        """


        from langchain import PromptTemplate, LLMChain
        from langchain_community.chat_models import ChatOpenAI

        PROMPT_TWEET = PromptTemplate(template=prompt, input_variables=["text"])
        llm = ChatOpenAI(temperature=0.0, model=config.sort_papers_gpt_model, openai_api_key=config.open_ai_key)
        chain =LLMChain(llm=llm, prompt=PROMPT_TWEET, verbose=True)
        # two weeks ago
        result = chain.run(PAPER_CONTENT)

        print(result)
