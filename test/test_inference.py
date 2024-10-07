import pytest


@pytest.mark.skipif(True, reason="not ready for ci yet")
def test_inference():
    from state_of_the_art.relevance_model.inference import TextEvaluationInference

    result = TextEvaluationInference().predict("test")
    assert isinstance(result, int)
