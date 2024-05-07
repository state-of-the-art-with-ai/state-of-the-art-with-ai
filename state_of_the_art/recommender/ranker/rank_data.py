from typing import Any


class RankGeneratedData:
    prompt: str
    from_date: Any
    to_date: Any
    summary: str

    def __init__(
        self, *, from_date, to_date, prompt, summary, papers_analysed, llm_result: str
    ) -> None:
        self.from_date = from_date
        self.to_date = to_date
        self.prompt = prompt
        self.summary = summary
        self.papers_analysed = papers_analysed
        self.llm_result = llm_result

    def to_dict(self):
        return {
            "summary": self.summary,
            "from_date": self.from_date,
            "to_date": self.to_date,
            "prompt": self.prompt,
            "papers_analysed": self.papers_analysed,
        }
