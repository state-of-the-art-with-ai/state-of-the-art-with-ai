import os
import pytest
from unittest import mock


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(os.environ, {"SOTA_TEST": "1"}):
        yield
