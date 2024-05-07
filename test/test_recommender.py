from state_of_the_art.recommender.recommender import Recommender
import os
from unittest import mock


@mock.patch.dict(os.environ, {"LLM_MOCK": "1"})
def test_generate():
    recommender = Recommender()
    result = recommender.generate(skip_register=True)
    assert result is not None
    assert len(result) > 0
