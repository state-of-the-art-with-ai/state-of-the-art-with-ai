from state_of_the_art.deprecated_recommender.generator import Recommender
import os
from unittest import mock


@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_generate_fast():
    """
    Run the recommender end2end but disable slow parts
    """
    recommender = Recommender()

    result = recommender.generate(
        skip_register=True, disable_pdf=True, query="test jean"
    )
    assert result is not None
    assert len(result) > 0
