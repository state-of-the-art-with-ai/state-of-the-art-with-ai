import os

import logging
from subprocess import PIPE, Popen
from typing import Optional


class EmailService:
    default_destination = "j34nc4rl0@gmail.com"
    SEND_FROM_EMAIL = "j34nc4rl0@gmail.com"

    def send(self, content=None, subject=None, attachment=None, recepient=None):
        # write content o file

        recepient = recepient or EmailService.default_destination
        if not content and not attachment:
            raise ValueError("You must provide content or attachment to send an email")

        if content and attachment:
            raise ValueError("You must provide content or attachment, not both")

        if attachment:
            self._send_email(
                to=recepient, subject=subject, message=content, attachement=attachment
            )
            return

        with open("/tmp/mail_content.txt", "w") as f:
            f.write(content)
        os.system(
            f"cat /tmp/mail_content.txt | mail.py send_email --to '{recepient}' --subject '{subject}'"
        )
        self._send_email(
            to=recepient, subject=subject, message=content, attachement=attachment
        )

    def _send_email(
        self, *, to: str, subject=None, message: Optional[str] = None, attachement=None
    ):
        if message:
            message = message.replace("'", "")

        password = os.environ["SECOND_MAIL_APPS_PASSWORD"]
        logging.debug(f"Pass: {password}")
        os.system(
            f"echo 'From: {self.SEND_FROM_EMAIL}\nTo: {self.SEND_FROM_EMAIL}\nSubject: {subject}\n\n{message}' > /tmp/foo"
        )

        attachement_part = ""
        if attachement:
            if not os.path.exists(attachement):
                raise FileNotFoundError(f"File {attachement} not found")
            attachement_part = f" -F 'file=@{attachement};type=application/octet-string;encoder=base64' "
            cmd = f"""curl --url 'smtps://smtp.gmail.com:465' --ssl-reqd --mail-from '{self.SEND_FROM_EMAIL}' -H "Subject: {subject}" --mail-rcpt '{to}' --user '{self.SEND_FROM_EMAIL}:{password}' {attachement_part}  """

        else:
            cmd = f"""curl --url 'smtps://smtp.gmail.com:465' --ssl-reqd --mail-from '{self.SEND_FROM_EMAIL}' --mail-rcpt '{to}' --user '{self.SEND_FROM_EMAIL}:{password}' -T /tmp/foo  """

        print("Command to run:", cmd)

        self._run(cmd)

    def _run(self, cmd):
        command = cmd
        with Popen(command, stdout=PIPE, stderr=None, shell=True) as process:
            output = process.communicate()[0].decode("utf-8")
            print("Email output", output)

            if process.returncode != 0:
                raise Exception("Error sending email" + output)


def main():
    import fire

    fire.Fire(SendEmail)


if __name__ == "__main__":
    main(0)
