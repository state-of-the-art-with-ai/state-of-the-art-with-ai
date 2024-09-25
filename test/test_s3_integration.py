

from state_of_the_art.infrastructure.s3 import S3


def test_s3():
    S3().validate_credentials()