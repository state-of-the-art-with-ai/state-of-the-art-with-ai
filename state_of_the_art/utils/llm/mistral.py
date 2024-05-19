

class Mistral():
    def __init__(self):
        from llama_index.llms.ollama import Ollama
        self.llm = Ollama(model="mistral", request_timeout=180, temperature=0)
    def call_llm(self, prompt, prompt_input) -> str:
        prompt = prompt.replace("{text}", prompt_input)
        return str(self.llm.complete(prompt))