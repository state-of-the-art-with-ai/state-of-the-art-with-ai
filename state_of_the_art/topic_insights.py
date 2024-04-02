from state_of_the_art.config import config
ALL_CATEGORIES = """
Physics
Astrophysics (astro-ph new, recent, search )
includes:Astrophysics of Galaxies; Cosmology and Nongalactic Astrophysics; Earth and Planetary Astrophysics; High Energy Astrophysical Phenomena; Instrumentation and Methods for Astrophysics; Solar and Stellar Astrophysics
Condensed Matter (cond-mat new, recent, search )
includes:Disordered Systems and Neural Networks; Materials Science; Mesoscale and Nanoscale Physics; Other Condensed Matter; Quantum Gases; Soft Condensed Matter; Statistical Mechanics; Strongly Correlated Electrons; Superconductivity
General Relativity and Quantum Cosmology (gr-qc new, recent, search )
High Energy Physics - Experiment (hep-ex new, recent, search )
High Energy Physics - Lattice (hep-lat new, recent, search )
High Energy Physics - Phenomenology (hep-ph new, recent, search )
High Energy Physics - Theory (hep-th new, recent, search )
Mathematical Physics (math-ph new, recent, search )
Nonlinear Sciences (nlin new, recent, search )
includes:Adaptation and Self-Organizing Systems; Cellular Automata and Lattice Gases; Chaotic Dynamics; Exactly Solvable and Integrable Systems; Pattern Formation and Solitons
Nuclear Experiment (nucl-ex new, recent, search )
Nuclear Theory (nucl-th new, recent, search )
Physics (physics new, recent, search )
includes:Accelerator Physics; Applied Physics; Atmospheric and Oceanic Physics; Atomic and Molecular Clusters; Atomic Physics; Biological Physics; Chemical Physics; Classical Physics; Computational Physics; Data Analysis, Statistics and Probability; Fluid Dynamics; General Physics; Geophysics; History and Philosophy of Physics; Instrumentation and Detectors; Medical Physics; Optics; Physics and Society; Physics Education; Plasma Physics; Popular Physics; Space Physics
Quantum Physics (quant-ph new, recent, search )
Mathematics
Mathematics (math new, recent, search )
includes: (see detailed description):Algebraic Geometry; Algebraic Topology; Analysis of PDEs; Category Theory; Classical Analysis and ODEs; Combinatorics; Commutative Algebra; Complex Variables; Differential Geometry; Dynamical Systems; Functional Analysis; General Mathematics; General Topology; Geometric Topology; Group Theory; History and Overview; Information Theory; K-Theory and Homology; Logic; Mathematical Physics; Metric Geometry; Number Theory; Numerical Analysis; Operator Algebras; Optimization and Control; Probability; Quantum Algebra; Representation Theory; Rings and Algebras; Spectral Theory; Statistics Theory; Symplectic Geometry
Computer Science
Computing Research Repository (CoRR new, recent, search )
includes: (see detailed description):Artificial Intelligence; Computation and Language; Computational Complexity; Computational Engineering, Finance, and Science; Computational Geometry; Computer Science and Game Theory; Computer Vision and Pattern Recognition; Computers and Society; Cryptography and Security; Data Structures and Algorithms; Databases; Digital Libraries; Discrete Mathematics; Distributed, Parallel, and Cluster Computing; Emerging Technologies; Formal Languages and Automata Theory; General Literature; Graphics; Hardware Architecture; Human-Computer Interaction; Information Retrieval; Information Theory; Logic in Computer Science; Machine Learning; Mathematical Software; Multiagent Systems; Multimedia; Networking and Internet Architecture; Neural and Evolutionary Computing; Numerical Analysis; Operating Systems; Other Computer Science; Performance; Programming Languages; Robotics; Social and Information Networks; Software Engineering; Sound; Symbolic Computation; Systems and Control
Quantitative Biology
Quantitative Biology (q-bio new, recent, search )
includes: (see detailed description):Biomolecules; Cell Behavior; Genomics; Molecular Networks; Neurons and Cognition; Other Quantitative Biology; Populations and Evolution; Quantitative Methods; Subcellular Processes; Tissues and Organs
Quantitative Finance
Quantitative Finance (q-fin new, recent, search )
includes: (see detailed description):Computational Finance; Economics; General Finance; Mathematical Finance; Portfolio Management; Pricing of Securities; Risk Management; Statistical Finance; Trading and Market Microstructure
Statistics
Statistics (stat new, recent, search )
includes: (see detailed description):Applications; Computation; Machine Learning; Methodology; Other Statistics; Statistics Theory
Electrical Engineering and Systems Science
Electrical Engineering and Systems Science (eess new, recent, search )
includes: (see detailed description):Audio and Speech Processing; Image and Video Processing; Signal Processing; Systems and Control
Economics
Economics (econ new, recent, search )
includes: (see detailed description):Econometrics; General Economics; Theoretical Economics
"""
class TopicInsights:
    def get_categories_for_topic(self):

        use_case = """
    Growth Data Products is a team in GetYourGuide that is responsible for the data science and machine learning for growing the business
    The mission of the team is to  optimize multi-channel customer acquisition and customer loyalty by building data products.

        """

        prompt = f"""
        Your are a arxiv topic recommender for state of the art papers.
        The topics that exist are the following: {ALL_CATEGORIES}
        Recommend topics for the following use-case:
        {{text}}
        """

        from langchain import PromptTemplate, LLMChain
        from langchain_community.chat_models import ChatOpenAI

        PROMPT_TWEET = PromptTemplate(template=prompt, input_variables=["text"])
        llm = ChatOpenAI(temperature=0.0, model=config.sort_papers_gpt_model, openai_api_key=config.open_ai_key)
        chain =LLMChain(llm=llm, prompt=PROMPT_TWEET, verbose=True)
        # two weeks ago
        result = chain.run(use_case)

        print(result)