


from state_of_the_art.utils import pdf
from state_of_the_art.utils.llm.llm import LLM
from typing import Optional


class ReportReview:

    def review_from_clipboard(self):
        import subprocess; 
        
        content = subprocess.getoutput('clipboard get_content')
        self.review_content(content)



    def review_content(self, content: Optional[str] = None):

        if not content:
            print("Content not provided via argument. Reading from stdin")
            import sys
            data = sys.stdin.readlines()
            content = "".join(data)

        
        prompt = """
        You are a panel of scientists and scientific reviewers. You have been asked to review this report about scientific papers.
        You analyse what is written about the papers and comment on i.t

        Answer the follwowing questions:
        1. What needs to be added or removed ot make the report more scientific?
        2. What are weasnesses of the report? What are the strengths of the report?
        3. Is the institution reporting it reliable? Why or why not?

        Report follows:
        {text}
        """

        result = LLM().call(prompt=prompt, prompt_input=content)

        pdf.create_pdf(data=result, output_path_description="review_report")


        return result

        
