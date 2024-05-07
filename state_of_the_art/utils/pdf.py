from typing import List


def create_pdf(data, output_path, disable_open=False):

    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    data = data.encode("latin-1", "replace").decode("latin-1")
    pdf.write(5, data)
    pdf.output(output_path)
    if not disable_open:
        open_pdf(output_path)


def open_pdf(output_path):
    import os

    os.system(f"open {output_path}")


def read_content(pdf_path):
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


def merge_pdfs(output_path, pdfs: List[str]):
    from PyPDF2 import PdfMerger

    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)
    merger.write(output_path)
    merger.close()
    open_pdf(output_path)


if __name__ == "__main__":
    import fire

    fire.Fire()
