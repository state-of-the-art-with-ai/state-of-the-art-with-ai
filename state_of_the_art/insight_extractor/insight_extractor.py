import os

from state_of_the_art.config import config
from state_of_the_art.utils.llm.llm import LLM
from state_of_the_art.utils.mail import SotaMail
from state_of_the_art.utils import pdf
from state_of_the_art.insight_extractor.content_extractor import get_content_from_url


class InsightExtractor:
    """
    Looks into a single paper and extracts insights
    """

    TABLE_NAME = "sota_paper_insight"

    def extract_from_url_in_clipboard(self):
        """
        loads the url frrom clipboard then calls the extract function
        """
        import subprocess

        url = subprocess.check_output("clipboard get_content", shell=True, text=True)
        self.extract_from_url(url)

    def extract_from_url(self, url: str, open_existing=True, function_call=True, email_skip=False):
        """
        Generates insights for a given paper
        """

        url = self._clean_url(url)

        if open_existing and self._open_insight_summary_if_exists(url):
            return

        article_content, title, document_pdf_location = get_content_from_url(url)
        if function_call:
            print("Calling gpt function")
            result = InsigthStructured().get_result(article_content)
        else: 
            result = InsigthPrompt().get_result(article_content)

        result = f"""Title: {title}
Abstract: {url}
{result}
        """

        pdf.create_pdf(
            data=result, output_path="/tmp/current_paper.pdf", disable_open=True
        )
        paper_path = pdf.create_pdf_path("p " + title)
        print("Saving paper insights to ", paper_path)
        pdf.merge_pdfs(paper_path, ["/tmp/current_paper.pdf", document_pdf_location])

        config.get_datawarehouse().write_event(
            self.TABLE_NAME,
            {"abstract_url": url, "insights": result, "pdf_path": paper_path},
        )

        if os.environ.get("SOTA_TEST") or email_skip:
            print("Skipping email")
        else:
            SotaMail().send("", f"Insights from {title}", paper_path)


    def _open_insight_summary_if_exists(self, abstract_url) -> bool:
        df = config.get_datawarehouse().event(self.TABLE_NAME)
        filtered = df[(df["abstract_url"] == abstract_url) & ~(df["pdf_path"].isnull())]
        if filtered.empty:
            return False

        path = filtered["pdf_path"].values[0]
        if not os.path.exists(path):
            print("File not found: ", path)
            return False
        print("Paper insights path: ", path)
        pdf.open_pdf(path)
        print("Paper already processed")
        return True

    def _clean_url(self, url):
        print("Given url: ", url)
        url = url.strip()
        url = url.replace("file://", "")
        return url


class BasePrompt():
    def __init__(self):
        self.profile = config.get_current_audience()
        self.QUESTIONS: dict[str, str] = self.profile.paper_questions
        self.profile = config.get_current_audience()

class InsigthPrompt(BasePrompt):
    def __init__(self):
        super().__init__()

    def get_result(self, text: str) -> str:
        return LLM().call(self.get_prompt(), text)

    def get_prompt(self) -> str:
        counter = 1
        QUESTIONS = ""
        for key, question in self.QUESTIONS.items():
            QUESTIONS += f"""===
Topic ({key}): {question}
==="""
            counter += 1

        self.PROMPT = (
            lambda QUESTIONS_STR: f"""Your job is to answer Data Science and AI questions in an understandable way.
You inpersonates a board of scientists and field experts that togeter answer all the questions based on their individual opinions and way of writing. 

Person 1. Richard Feynman, has concise and simple answers using simple language and helps you to build an intuition about the topic, uses analogies often.
Person 2. Andrej Karpathy, very technical and precise, uses a lot of technical terms and is very detailed.

We value diversity in the answers. Make sure that the same question get answered by more then 1 person when its complex or nunanced.
Especially for questions that are open ended, harder, or require many examples please answer with multiple people.
Make sure to mention the new person that is answering the question at the moment and mark when a transition happens. Ex: Question 1. Person 1 (Name): ..., Person 2 (Name): Additionally to what Person 1 said, I think... Question 2. Person 1 (Name): ... Person 3 (Name): I disagree with Person 1, because ... 
We should start with simple answers first from teh most qualified person to answer the question and then go to more complex answers.
Make sure that in the answers they dont repeat each other, just add new information.
Mention the topic and question number in your answers. Do not worry about the lenght of the answers, if you need to write a lot to break down the concept do it.
Make sure to cover all the questions do not stop after answering the first one.
Make the content very clean and minimalistic, use 3 new lines to space the questions
Optimize your answers to the following audience: {self.profile.get_preferences()}

Article content starts ###start
{{text}}
### end of article content

The tasks now follow
tasks start###
{QUESTIONS_STR}
### task ends

start of answers ###start
0. Question (topic_example)
Person 1: 
This is the answer based on person 1 opinion
Person 2: 
Here goes the addition to answer on from person 2 perspective

1. Question ("""
        )

        prompt = self.PROMPT(QUESTIONS)
        return prompt
    
class InsigthStructured(BasePrompt):
    def __init__(self):
        super().__init__()

    def get_result(self, text: str) -> str:
        from openai import OpenAI

        client = OpenAI(
            api_key=config.OPEN_API_KEY
        )
        result = client.chat.completions.create(
            model = 'gpt-4o',
            messages = [{'role': 'user', 'content': text}],
            functions = [
                {
                    "name": "get_insights_from_paper",
                    "description":f"""This function returns expert data science insights that ecompasses the knwoeldge of all world top scientists.
It returns the most insightful and actionable information from the given paper content
The written style is in richard feyman style of explanations
It optimized the answers for the following audience: {self.profile.get_preferences()[0:300]}
""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "institutions": {
                                "type": "string",
                                "description": "the insitutions that published the paper"
                            },
                            "published_date": {
                                "type": "string",
                                "description": "when the paper was published?"
                            },
                            "published_where": {
                                "type": "string",
                                "description": "where paper was published?"
                            },
                            "top_insights": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 3,
                                "maxItems": 5,
                                "description": """returns most valuable insights from the paper max 3 sentences per insight
                                The insights cover well which problem they are trying to solve.
                                """,
                            },
                            "going_deep": {
                                "type": "string",
                                "description": "return a summary on explaining in an clear way the core of the paper"
                            },
                            "core_terms_defintion": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 4,
                                "description": "define core terms in the paper use analogies if needed when they are very complex",
                            },
                            "strenghs_from_paper": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 3,
                                "description": "what are particular strenghts of this paper that make them stand out in relation to others in similar field?",
                            },
                            "weakeness_from_paper": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 2,
                                "description": "what are particular weakenessess of this paper that make it less useful?",
                            },
                            "top_recommended_actions": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 3,
                                "description": "what are actionable recommendations from this paper?",
                            },
                            'external_resoruces_recommendations': {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "minItems": 3,
                                "description":"""returns further resources recommendations from the board of experts if somebody whants to go deep into it.
                                Books, articles, papers or people to follow related to the topic that helps to get a deeper understanding of it.
                                """
                            }
                        },
                    }
                }
            ],
            function_call = 'auto'
        )
        result = str(result.choices[0].message.function_call.arguments)
        import json
        print("Result", result)
        return json.dumps(json.loads(result), indent=4)
