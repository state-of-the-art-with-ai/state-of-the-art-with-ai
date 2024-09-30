import os
from subprocess import PIPE, Popen
import subprocess
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

        self._send_email(
            to=recepient, subject=subject, message=content, attachement=attachment
        )

    def _send_email(
        self, *, to: str, subject=None, message: Optional[str] = None, attachement=None
    ):
        if message:
            message = message.replace("'", "")

        password = os.environ["SECOND_MAIL_APPS_PASSWORD"]
        if False:
            body_content = f"""From: {self.SEND_FROM_EMAIL}
To: {to}
Subject: {subject}

{message}"""
        else:
            body_content = f"""From: {self.SEND_FROM_EMAIL}
To: {to}
Subject: {subject}
Content-Type: text/html; charset="UTF-8"

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  </head>
  <body>
    {message}
 </body>
</html>
"""

        with open("/tmp/foo", "w") as myfile:
            myfile.write(body_content)

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
        p = subprocess.Popen(cmd, shell=True, text=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        out, error  = p.communicate()
        print(out)
        print(error)

def main():
    import fire

    fire.Fire(EmailService)


if __name__ == "__main__":
    main(0)
