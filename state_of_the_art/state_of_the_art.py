
from state_of_the_art.arxiv_utils import register_new_papers
from state_of_the_art.spot_papers import rank_sota_by_relevance
from state_of_the_art.summaries import TopSummaries, SummariesData
from state_of_the_art.papers import PapersData


def register_all_papers():
    register_new_papers(query='cs')
    register_new_papers(query='ai')
    register_new_papers(query='machine learning')


def register_and_sort_papers():
    register_all_papers()
    rank_sota_by_relevance()

def main():
    import fire
    fire.Fire()

if __name__ == "__main__":
    main()
