import os
from unittest import mock

from state_of_the_art.paper_insight.paper_insight import PaperInsightExtractor


@mock.patch.dict(os.environ, {"SOTA_TEST": "1"})
def test_extract():
    PaperInsightExtractor().generate("https://arxiv.org/abs/2202.02484v1", open_existing=False)
