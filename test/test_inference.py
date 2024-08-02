

def test_inference():
    from state_of_the_art.relevance_model.inference import Inference
    result = Inference().predict('test')
    assert isinstance(result, int)