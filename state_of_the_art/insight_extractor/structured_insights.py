from enum import Enum
from state_of_the_art.config import config
from state_of_the_art.tables.questions_table import QuestionsTable
from openai import OpenAI


import json
import os
from typing import Optional, Tuple


def convert_questions_to_openai_call(data):
    result = {}
    for i, row in data.iterrows():
        data = {"type": "string", "description": row["question"]}
        if row["min_items"] or row["max_items"]:
            data = {
                "type": "array",
                "items": {"type": "string"},
                "description": row["question"],
            }

            if row["min_items"]:
                data["minItems"] = int(row["min_items"])

            if row["max_items"]:
                data["maxItems"] = int(row["max_items"])

        result[row["short_version"]] = data
    return result


class SupportedModels(Enum):
    gpt_4o_mini = "gpt-4o-mini"
    gpt_4o = "gpt-4o"


class StructuredPaperInsights:
    def __init__(self, model_to_use: Optional[str] = None):
        self.profile = config.get_current_audience()
        self.QUESTIONS: dict[str, str] = self.profile.paper_questions
        self.profile = config.get_current_audience()
        self.model_to_use = model_to_use

    def get_result(self, paper_content: str, question=None) -> Tuple[str, dict]:
        if os.environ.get("SOTA_TEST"):
            return "Mocked result", {}

        if question:
            print(f"Using question to extract insights ({question})")
            parameters = {question: {"type": "string", "description": question}}
        else:
            questions = QuestionsTable().read()
            parameters = convert_questions_to_openai_call(questions)

        client = OpenAI(api_key=config.OPEN_API_KEY)
        used_model = (
            self.model_to_use if self.model_to_use else SupportedModels.gpt_4o.value
        )
        print("Using model: ", used_model)
        print("Paper preview to summarize: ", paper_content[0:3000])

        if len(paper_content) < 300:
            raise Exception(f"Paper content too short to send to OpenAI content: {paper_content}")

        if len(paper_content) > 120000:
            paper_content = paper_content[0:120000]

        result = client.chat.completions.create(
            model=used_model,
            messages=[{"role": "user", "content": paper_content}],
            functions=[
                {
                    "name": "get_insights_from_paper",
                    "description": f"""This function returns expert data science insights that ecompasses the knwoeldge of all world top scientists.
It returns the most insightful and actionable information from the given paper content
The written style is in richard feyman style of explanations
It optimized the answers for the following audience: {self.profile.get_preferences()[0:300]}
""",
                    "parameters": {"type": "object", "properties": parameters},
                }
            ],
            function_call={"name": "get_insights_from_paper"},
        )

        if not hasattr(result.choices[0].message, "function_call"):
            raise Exception(
                f"""Function call extraction operation failed returned {result.choices[0].message.content} instead """
            )

        print("Result: ", str(result))
        structured_results = result.choices[0].message.function_call.arguments
        structured_results = json.loads(str(structured_results))
        print("structured_results:", structured_results)
        return json.dumps(structured_results, indent=3), structured_results
