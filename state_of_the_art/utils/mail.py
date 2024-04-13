
import os
class Mail:
    def send(self, content, subject):
        #write content o file
        with open('/tmp/mail_content.txt', 'w') as f:
            f.write(content)

        os.system(f"cat /tmp/mail_content.txt | mail.py send_email --to 'j34nc4rl0@gmail.com' --subject '{subject}' ")