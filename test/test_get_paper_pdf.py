import pytest
from state_of_the_art.paper.local_paper_copy import get_paper_copy_path


def test_get_pdf():
    url = "https://arxiv.org/abs/2202.13868"
    result = get_paper_copy_path(url)
    assert result is not None


def test_get_missing_pdf():
    url = "asdasdfas1"

    with pytest.raises(Exception, match="Local copy not found"):
        get_paper_copy_path(url)
