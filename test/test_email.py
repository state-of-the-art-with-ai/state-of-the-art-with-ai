from state_of_the_art.utils.mail import EmailService
import pytest


@pytest.mark.skipif(True, reason="do not want spammy emails")
def test_email():

    content = """
    <h1>Test email</h1>
    <a href="https://www.google.com">Click here</a>
    """
    EmailService().send(content=content, subject="test email")
