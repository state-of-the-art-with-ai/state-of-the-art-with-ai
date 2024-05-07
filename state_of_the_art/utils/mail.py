import os


class Mail:
    pdf_email = "machado.c.jean_ybQiVz@kindle.com"

    def send(self, content=None, subject=None, skip_write=False, attachment=None):
        # write content o file
        if not skip_write:
            with open("/tmp/mail_content.txt", "w") as f:
                f.write(content)

        attachment_part = ""
        if attachment:
            attachment_part = f" --attachement '{attachment}' "
            os.system(
                f"cat /tmp/mail_content.txt | mail.py send_email --to '{Mail.pdf_email}' --subject '{subject}' {attachment_part} "
            )
            os.system(
                f"cat /tmp/mail_content.txt | mail.py send_email --to 'j34nc4rl0@gmail.com' --subject '{subject}' {attachment_part} "
            )
        else:
            os.system(
                f"cat /tmp/mail_content.txt | mail.py send_email --to 'j34nc4rl0@gmail.com' --subject '{subject}' {attachment_part} "
            )
