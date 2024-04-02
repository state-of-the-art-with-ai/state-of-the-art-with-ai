
from state_of_the_art.open_ai_utils import call_chatgpt
INPUT_EXAMPLE = """
Results generated at 2024-04-02T23:09:00.683295 for period (2024-03-19, 2024-04-02): 

(0.9) Title: "A Survey on Self-Supervised Pre-Training of Graph Foundation Models: A Knowledge-Based Perspective"
Relevance: Relevant because it provides a comprehensive overview of self-supervised pre-training tasks for graph foundation models from a knowledge perspective, which is crucial for advancing graph neural networks and their applications.
Arxiv URL: http://arxiv.org/abs/2403.16137v1

(0.8) Title: "The Evolution of Football Betting- A Machine Learning Approach to Match Outcome Forecasting and Bookmaker Odds Estimation"
Relevance: Relevant because it explores the use of machine learning in predicting football match outcomes and estimating bookmaker odds, which is significant for sports analytics and betting industries.
Arxiv URL: http://arxiv.org/abs/2403.16282v1

(0.7) Title: "AI for Biomedicine in the Era of Large Language Models"
Relevance: Relevant because it discusses the impact of large language models on biomedical and health informatics, highlighting the potential for AI to revolutionize medical research and healthcare.
Arxiv URL: http://arxiv.org/abs/2403.17660v1

(0.6) Title: "Bioinformatics and Biomedical Informatics with ChatGPT: Year One Review"
Relevance: Relevant because it reviews the applications of ChatGPT in bioinformatics and biomedical informatics, showcasing the potential of LLMs in advancing research and applications in these fields.
Arxiv URL: http://arxiv.org/abs/2403.16303v2

(0.5) Title: "Electromagnetic-Field-Based Circuit Theory and Charge-Flux-Flow Diagrams"
Relevance: Relevant because it introduces a new circuit theory based on electromagnetic fields, which could lead to advancements in electrical engineering and circuit design.
Arxiv URL: http://arxiv.org/abs/2403.16025v1

(0.4) Title: "Blockchain-based Pseudonym Management for Vehicle Twin Migrations in Vehicular Edge Metaverse"
Relevance: Relevant because it explores the use of blockchain for managing pseudonyms in vehicle twin migrations within the vehicular edge metaverse, which is significant for the development of intelligent transportation systems.
Arxiv URL: http://arxiv.org/abs/2403.15271v1

(0.3) Title: "Operational Experience and R&D results using the Google Cloud for High Energy Physics in the ATLAS experiment"
Relevance: Relevant because it discusses the integration of Google Cloud Platform in the ATLAS experiment at CERN, showcasing the potential of cloud computing in high energy physics research.
Arxiv URL: http://arxiv.org/abs/2403.15873v1

(0.2) Title: "Digital Twin Assisted Intelligent Network Management for Vehicular Applications"
Relevance: Relevant because it presents a digital twin-assisted framework for intelligent network management in vehicular applications, which is crucial for the development of smart transportation systems.
Arxiv URL: http://arxiv.org/abs/2403.16021v1

(0.1) Title: "Exploring the Boundaries of Ambient Awareness in Twitter"
Relevance: Relevant because it investigates ambient awareness on Twitter, providing insights into how users gain knowledge about their network, which is significant for social media analytics and user behavior studies.
Arxiv URL: http://arxiv.org/abs/2403.17767v2

(0.0) Title: "Towards a Zero-Data, Controllable, Adaptive Dialog System"
Relevance: Relevant because it proposes a framework for developing dialog systems that can adapt to new tasks without additional training, which is significant for the advancement of conversational AI.
Arxiv URL: http://arxiv.org/abs/2403.17710v1
##end

"""

class RankerFormatter:

    def format(self):
        prompt = f"""Format the following string into a list in json format return only the json no other character also exclude json blocks like ```json and ``` 
text:
{{text}}
output:
"""
        return call_chatgpt(prompt, INPUT_EXAMPLE)


if __name__ == "__main__":
    import fire
    fire.Fire()




