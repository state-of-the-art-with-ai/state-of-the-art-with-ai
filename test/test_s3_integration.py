from state_of_the_art.infrastructure.s3 import S3
import os

from unittest import mock

import pytest


def test_s3():
    S3().validate_credentials()
    S3().pull_events_data()
    S3().push_local_events_data()
