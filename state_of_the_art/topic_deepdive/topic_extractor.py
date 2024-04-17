from typing import Optional
import sys

class TopicExtractor:
    def extract(self, project_description: Optional[str] = None):
        """
        return keywords from project descriptions

        :return:
        """

        if not project_description:
            if not sys.stdin.isatty():
                data = sys.stdin.readlines()
                project_description = "".join(data)


        if not project_description:
            raise Exception("No project description provided")

        prompt = f"""Your task is to extract keywords from project descriptions that will yield relevant papers from the arxiv api.
The descriptions are about tech projects and your goal is to help to find papers that will drive the project towards a more innovative solution.
that match the key topics under consideration.
Terminology that is not common in  academia should be avoided or find a way to map it to academic terms.
Avoid super broad and generic ones that will yield results that are not actionable examples:
Machine Learning Models
Data Pipeline Development
return no more than 10 suggested keywords.
put your higher confidence and more niche suggestions first.
project description starts###{{text}}
###project description ends

Your keywords suggestions starts###

        """
        from state_of_the_art.llm import LLM
        result = LLM().call(prompt, project_description)
        return result

if __name__ == "__main__":
    import fire
    fire.Fire(TopicExtractor)