import os
from unittest import mock

from state_of_the_art.insight_extractor.insight_extractor import (
    InsightExtractor,
    StructuredPaperInsights,
)


EXAMPLE_LLM_OUTPUT = {
    "institutions": "Institute of Computing Technology, Chinese Academy of Sciences",
    "published_date": "June 24, 2024",
    "published_where": "WSDM ’24, March 4–8, 2024, Mérida, Yucatán, Mexico",
    "top_insights": [
        "The traditional approaches to Marketing Mix Modeling (MMM) using regression techniques fall short in dealing with the complexity and non-linearity of marketing channels and their interactions.",
        "CausalMMM is proposed to dynamically discover interpretable causal structures from data, making it more adaptable and accurate for predicting Gross Merchandise Volume (GMV) across different shops.",
        "CausalMMM integrates Granger causality within a variational inference framework, leveraging both temporal and saturation marketing response patterns to enhance prediction accuracy.",
    ],
    "going_deep": "This paper introduces CausalMMM, a novel approach to Marketing Mix Modeling (MMM) that addresses significant limitations of traditional methods. Traditional MMM relies heavily on regression techniques, which assume linear relationships and independence between different marketing channels. This assumption often fails in practice because marketing channels (such as paid search, display ads, etc.) interact in complex ways. For instance, a display ad might increase awareness that subsequently leads to more searches for a product.\n\nCausalMMM differentiates itself by automatically discovering and learning the causal structures among these different marketing channels. This is achieved using a framework that integrates Granger causality within variational inference. Granger causality helps determine if one time series can predict another, while variational inference provides a way to handle the uncertainty and complexity of these structures dynamically.\n\nA key advantage of CausalMMM is its ability to capture and incorporate various marketing response patterns like the carryover effect (where advertising impact persists over time) and saturation effect (diminishing returns with increased advertising spend). These patterns are important in making accurate predictions about GMV, especially since the effects of marketing are both immediate and lagged. The proposed method is validated through a series of experiments demonstrating its superiority in predicting causal structures and GMV over traditional methods.",
    "core_terms_defintion": [
        "Marketing Mix Modeling (MMM): A method used to estimate the impact of various marketing tactics (like advertising, promotions) on sales or market share, traditionally using linear regression models.",
        "Granger Causality: A statistical hypothesis test to determine if one time series can predict another. If the past values of one time series contain information that helps predict the future values of another, then Ganger causality is assumed to exist.",
        "Variational Inference: A statistical method for approximating complex distributions. It is often used in Bayesian statistics to approximate posterior distributions by turning the problem into an optimization problem.",
        "Carryover Effect: In advertising, it refers to the lingering impact of an advertisement on consumer behavior, extending beyond the initial exposure. The effectiveness of an ad persists over time.",
    ],
    "strenghs_from_paper": [
        "CausalMMM's ability to dynamically discover causal structures sets it apart, making it adaptable to the specific behaviors of different shops.",
        "Integration of Granger causality provides a sophisticated way to identify predictive relationships between marketing channels, enhancing interpretability and accuracy.",
        "The use of variational inference ensures that the model can handle the uncertainty and complex dependencies inherent in marketing data effectively.",
    ],
    "weakeness_from_paper": [
        "The approach might be computationally intensive, which could limit its applicability for small enterprises with limited data and resources.",
        "The reliance on accurate historical data can be a drawback if the data is noisy or missing. This might challenge the model's ability to learn the correct causal structures.",
    ],
    "top_recommended_actions": [
        "Consider implementing CausalMMM to improve the accuracy of marketing budget allocations across various channels, thereby potentially increasing overall GMV.",
        "Use CausalMMM to explore and understand the interactions between different marketing channels, which can provide deeper insights into effective marketing strategies.",
        "Leverage the model to account for the carryover and saturation effects in your marketing analysis, providing a more nuanced understanding of campaign effectiveness over time.",
    ],
    "external_resoruces_recommendations": [
        '"Causal Inference in Statistics: A Primer" by Judea Pearl for foundational knowledge on causality and causal structures.',
        "Research papers on Granger Causality and its applications in time-series analysis to further understand the core concepts used in CausalMMM.",
        "Journal articles on variational inference methods to grasp the mathematical underpinnings and applications in complex probability distributions.",
    ],
}

@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_post_extraction():
    InsightExtractor().post_extraction('foo', EXAMPLE_LLM_OUTPUT, 'a path', 'http://asdfasdd', 'a title')


def test_insigts_structure():
    result = InsightExtractor()._convert_sturctured_output_to_insights(EXAMPLE_LLM_OUTPUT, "https://arxiv.org/abs/2202.02484v1")
    print(result)
    for key, value in result:
        assert key is not None
        assert value is not None



@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_structured_output():
    result_str, structured = StructuredPaperInsights().get_result("paper content")

    assert isinstance(result_str, str)
    assert isinstance(structured, dict)


@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_extract():
    InsightExtractor().extract_from_url(
        "https://arxiv.org/abs/2202.02484v1", open_existing=False
    )
