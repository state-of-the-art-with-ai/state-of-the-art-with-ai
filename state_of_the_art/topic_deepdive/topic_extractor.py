
class TopicExtractor:
    def extract(self, project_description: str):
        """
        return keywords from project descriptions

        :return:
        """

        prompt = f"""Your task is to extract search keywords from project descriptions.
The descriptions are about tech projects and you want to help to find papers in the arxiv api
that match the key topics under consideration.

project description starts###{{text}}
###project description ends

Keywords examples start###
- bidding
- marketing optimizations

###keywords examples end
Your keywords suggestions starts###

        """
        from state_of_the_art.llm import LLM
        result = LLM().call(prompt, project_description)
        return result

if __name__ == "__main__":
    import fire
    fire.Fire()