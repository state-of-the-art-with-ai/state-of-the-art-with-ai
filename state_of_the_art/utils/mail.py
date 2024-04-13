
import os
class Mail:
    def send(self, content=None, subject=None, skip_write=False):
        #write content o file
        if not skip_write:
            with open('/tmp/mail_content.txt', 'w') as f:
                f.write(content)

        result = os.system(f"cat /tmp/mail_content.txt | mail.py send_email --to 'j34nc4rl0@gmail.com' --subject '{subject}' ")
        print(result)