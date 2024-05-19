from state_of_the_art.recommender.recommender import Recommender
import os
from unittest import mock


@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_generate():
    recommender = Recommender()
    result = recommender.generate(skip_register=True, query='test jean')
    assert result is not None
    assert len(result) > 0
