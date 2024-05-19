

class Mistral():
    def __init__(self):
        from llama_index.llms.ollama import Ollama
        self.llm = Ollama(model="mistral", request_timeout=60)
    def call_llm(self, prompt, prompt_input):

        prompt = prompt.replace("{text}", prompt_input)

        return self.llm.complete(prompt)