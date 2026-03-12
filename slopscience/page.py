import hashlib

class Page:
    def __init__(self, type, title, author, content, sent_from = '', sent_to = ''):
        self.type = type
        self.title = title
        self.author = author
        self.content = content

        self.id = hashlib.sha256(f'{self.type}:{self.title}:{self.author}{self.content}'.encode()).hexdigest()
        self.short_id = self.id[0:8] # TODO: CorrectHorseBatteryStaple

        self.sent_from = sent_from
        self.sent_to = sent_to

