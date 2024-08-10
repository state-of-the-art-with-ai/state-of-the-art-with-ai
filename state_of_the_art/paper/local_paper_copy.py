import os
from tiny_data_warehouse import DataWarehouse

def open_paper_locally(abstract_url: str):

    paper_path = get_paper_copy_path(abstract_url)
    os.system("open " + paper_path)


def get_paper_copy_path(abstract_url: str) -> str:
    """
    returns the local copy of the paper
    """

    tdw = DataWarehouse()
    df = tdw.event("sota_paper_insight").sort_values(
        by="tdw_timestamp", ascending=False
    )
    filtered_df = df[df["abstract_url"] == abstract_url]
    if filtered_df.empty:
        raise Exception(f"Local copy not found for paper: {abstract_url}")
    
    filtered_df = filtered_df[filtered_df['pdf_path'].notnull()]
    if filtered_df.empty:
        raise Exception(f"All extracted insights with empty pdf_path: {abstract_url}")

    result = filtered_df.iloc[0]["pdf_path"]
    
    if not result:
        raise Exception(f"Pdf path not stored for paper {abstract_url}")
    
    return result
