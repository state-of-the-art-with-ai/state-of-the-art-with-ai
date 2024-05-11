import os
from typing import List, Optional


def create_pdf(
    *,
    data: str,
    output_path_description: Optional[str] = None,
    output_path: Optional[str] = None,
    disable_open=False,
):

    from fpdf import FPDF

    if not output_path:
        output_path = create_pdf_path(output_path_description)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    data = data.encode("latin-1", "replace").decode("latin-1")
    pdf.write(5, data)
    pdf.output(output_path)
    if not disable_open and not os.environ.get("SOTA_TEST"):
        open_pdf(output_path)

    return output_path


def create_pdf_path(description_path: str, disable_timestamp=False):
    import datetime

    description_path = description_path.strip()
    now = datetime.datetime.now().isoformat().split(".")[0]

    if not disable_timestamp:
        description_path = now + " " + description_path
    description_path = description_path.replace(" ", "_")
    description_path = "".join(x for x in description_path if x.isalnum() or x == "_")
    base_path = "/Users/jean.machado/projects/state-of-the-art-via-ai/reports/"

    if os.environ.get("SOTA_TEST"):
        base_path = "/tmp/"
        print("Given that tests are enabled will use /tmp/ as base path for pdfs.")

    return base_path + description_path + ".pdf"


def open_pdf(output_path):
    import os

    os.system(f"open {output_path}")


def read_content(pdf_path):
    print("Reading content from pdf: ", pdf_path)
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    number_of_pages = len(reader.pages)
    PAPER_CONTENT = ""
    for page in reader.pages:
        PAPER_CONTENT += page.extract_text()

    print("Number of pages: ", number_of_pages)
    print("Number of characters: ", len(PAPER_CONTENT))
    print("Number of tokens: ", len(PAPER_CONTENT) / 4)

    print("Number of pages: ", number_of_pages)
    print("Number of characters: ", len(PAPER_CONTENT))
    print("Number of tokens: ", len(PAPER_CONTENT) / 4)
    return PAPER_CONTENT


def merge_pdfs(output_path: str, pdfs: List[str]):
    from PyPDF2 import PdfMerger

    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()
    if not os.environ.get("SOTA_TEST"):
        open_pdf(output_path)


if __name__ == "__main__":
    import fire

    fire.Fire()
