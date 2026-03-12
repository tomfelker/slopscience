import random
from .page import Page

def sample_down(lst, max_n):
    if len(lst) <= max_n:
        return list(lst)
    return random.sample(lst, max_n)

class Scientist:
    def __init__(self, name):
        self.notes = []
        self.inbox = []
        self.name = name
        self.soul = Page(type='soul', title='', author=name, content='')

    def sample_context(self, max_notes, max_letters):
        return sample_down(self.notes, max_notes) + sample_down(self.inbox, max_letters)

    def receive_letter(self, page):
        self.inbox.append(page)

    def receive_note(self, page):
        self.notes.append(page)

class Journal:
    def __init__(self, name):
        self.name = name
        self.accepted_articles = []
        self.pending_articles = []

    def receive_submission(self, page):
        self.pending_articles.append(page)

class Academia:
    def __init__(self):
        self.scientists = {}
        self.journals = {}

    def add_scientist(self, scientist):
        self.scientists[scientist.name] = scientist

    def add_journal(self, journal):
        self.journals[journal.name] = journal

    def route_page(self, page, source_scientist):
        if page.type == 'note':
            source_scientist.receive_note(page)
        elif page.type == 'letter':
            page.sent_from = source_scientist.name
            if page.sent_to in self.scientists:
                self.scientists[page.sent_to].receive_letter(page)
        elif page.type == 'article':
            if page.sent_to in self.journals:
                self.journals[page.sent_to].receive_submission(page)
