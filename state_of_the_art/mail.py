
import os
class Mail:
    def send(self, content, subject):
        os.system(f"mail.py send_email --to 'j34nc4rl0@gmail.com' --subject '{subject}' --message '{content}'")