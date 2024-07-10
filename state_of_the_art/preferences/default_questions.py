DEFAULT_PAPER_QUESTIONS = {
    "institution": "Which institution published this paper?",
    "top_insights": """What are the most relevant learnings of the paper?
The insights can come form the results of the paper and form literature review Highlight at a minimum 5 insights.
    Avoid trivial or salesly insights that are common knowledge for your audience or not backed by data.

    Some examples of great insights are:
    - Paper Identifies four universal stages of inference in LLMs: detokenization, feature engineering, prediction ensembling, and residual sharpening. These stages help us understand how LLMs process information and make prediction
    - Small Multilingual Language Models (SMLMs) like XLM-R and mT5 outperform larger English-centric LLMs in zero-shot cross-lingual sentiment analysis. This means they can better handle sentiment analysis tasks in multiple languages without additional training data in those languages.
    - The market structure significantly affects the behavior of autobidder dynamics. Even in this constrained setting we establish the possibility of multiple attracting equilibria as well as unstable equilibria


    
    """,
    'insights deep dive': '''For the top 3 insights you selected as most relevant, go deeper and analyse why they are relevant.
Make sure to mention a the literal parts from the paper that supports your insight.
Explain it from a hihg level and also form a bottom up perspective.
    ''',
    "define_terms": """Which terms are the top 10 (at most) critical to understand the paper?
Prioritize mathematical terms definitons. Define them shortly and clearly. ideally 1 sentence no more than 2 per defintion.
Use analogies or examples to make the definitions clear when needed""",
    "recommended_actions": """What are top actions recommended as learnings from this paper? """,
    "problem_solving": "What problem is the paper solving? Explain the core questions to me and quote part of the problem literally from the paper. ALso highlight how the problem is being solved",
    "literature_review": "What is the most interesting learning from this paper literature review? Quote the interesting part literally and explain why its interesting",
    "criticize_methodology": """Is the methodoloy and claims of the  paper sound? What are the weaknessess? Is the paper complete enough or is not transparent enough to make it replciable? Be skeptical, do not spare words to make a clear case covering its weakneesses. Act like a scientific reviewer and provide a critique of the methodology of the paper""",
    "deeper": """'What to learn to go deeper in this topic? What are the top 3-5 topics, the top 3 authors and the top 3 papers and top 3 books to read to go deeper in this topic?""",
}
