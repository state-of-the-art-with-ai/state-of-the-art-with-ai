from state_of_the_art.utils.llm import LLM


class TopicExtractor:
    def __init__(self):
        self.llm = LLM()

    def extract_semantic_query(self, description) -> str:
        """
        Extracts a topic from a text
        """
        prompt = """"You are a topic extractor for project descriptions. Your taks is to find semantic keywords for a given topic
this keywords will be used as search arguments for papers in arxiv.
return the 1 sentence that best describes the topic the best so we can help the user to find the best papers in the topic
if you detect some domain specific words that are not common in scientific papers find a way to replace them with words that are more common in scientific papers
limit it to 10 words max
Topic: {text}
        Your query:"""
        return self.llm.call(prompt, description)
