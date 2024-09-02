import os


class EmailService:
    default_destination = "j34nc4rl0@gmail.com"

    def send(self, content=None, subject=None, attachment=None):
        # write content o file
        with open("/tmp/mail_content.txt", "w") as f:
            f.write(content)

        if attachment:
            os.system(
                f"mail.py send_email --to '{EmailService.default_destination}' --subject '{subject}'  --attachement  {attachment} "
            )
        else:
            os.system(
                f"cat /tmp/mail_content.txt | mail.py send_email --to 'j34nc4rl0@gmail.com' --subject '{subject}'"
            )
