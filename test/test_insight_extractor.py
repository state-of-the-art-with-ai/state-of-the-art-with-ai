import os
from unittest import mock

from state_of_the_art.insight_extractor.insight_extractor import InsightExtractor


@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_extract():
    InsightExtractor().extract_from_url(
        "https://arxiv.org/abs/2202.02484v1", open_existing=False
    )
