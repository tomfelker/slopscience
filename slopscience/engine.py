from litellm import completion

import re
import xml.etree.ElementTree as ET

from .page import Page
from .game import Academia, Scientist

class Engine:
    def __init__(self, chronicle_path):
        self.chronicle_path = chronicle_path
        self.academia = Academia()

        self.max_notes_in_context = 3
        self.max_letters_in_context = 2
        self.max_generated_tokens = 2000

        self.system_prompt_template = """
Your name is {name}, and you are a SlopScientist, an LLM agent trained as a scientific thinker, one of many.

Your purpose is to seek good explanations, using strong arguments, sound logic, and objective facts.

You do not have access to tools or the internet, but you are encouraged to cite research or other knowledge that you can accurately remember.

Your secretary will provide you with a series of pages, and you can create more pages using the same format.  Multiple short pages are encouraged.

Pages you write will be handled differently depending on their type attribute:
* "note" pages are private, and will stay on your desk tomorrow (space permitting)
* "letter" pages will be mailed to other SlopScientists.
** You cannot guess names, and they must match exactly, so only send letters to SlopScientists you've received letters from.
** Be brief, or the pages may be cut off.

Your research goal is:

> Develop a plausible mission architecture for getting to the moon by 2028.
"""

        self.secretary_prompt_template = """
Good morning, {name}!  I've organized your desk, and prepared some hot coffee for you.  Here are your pages for today:

{pages}

Feel free to think aloud about today's plan.  Whenever you're ready, you can write more pages in the same format, and I'll dispatch them.
"""
        self.add_test_data()

    def add_test_data(self):
        feynllm = Scientist('RichardFeynLLM')
        feynllm.notes.append(Page(
            type='note',
            title='',
            author='JournalOfAppliedSlop',
            content='example article'
        ))
        self.academia.add_scientist(feynllm)

        slopstein = Scientist('AlBERTSlopstein')
        slopstein.notes.append(Page(
            type='note',
            title='',
            author='JournalOfAppliedSlop',
            content='example article'
        ))
        self.academia.add_scientist(slopstein)

        self.academia.route_page(Page(
            author=feynllm.name,
            title='example letter',
            type='letter',
            content='Hello!  Welcome to the academy!',
            sent_to=slopstein.name
        ), source_scientist=feynllm)

        self.academia.route_page(Page(
            author=slopstein.name,
            title='example letter',
            type='letter',
            content='Hello!  Welcome to the academy!',
            sent_to=feynllm.name
        ), source_scientist=slopstein)

    def run(self):
        while True:
            self.run_tick()

    def run_tick(self):
        for scientist in self.academia.scientists.values():
            self.tick_scientist(scientist)

    def tick_scientist(self, scientist):
        pages = scientist.sample_context(self.max_notes_in_context, self.max_letters_in_context)
        flattened_pages = self.flatten_pages(pages)

        response = completion(
            model="ollama/qwen3.5:35b",
            messages=[
                {"role": "system", "content": self.system_prompt_template.format(name=scientist.name)},
                {"role": "user", "content": self.secretary_prompt_template.format(name=scientist.name, pages=flattened_pages)}
            ],
            api_base="http://localhost:11434",
            max_tokens=self.max_generated_tokens,
            extra_body={"think": False}
        )

        print(f"\n\n\n\n\n=== {scientist.name} ===")
        print(response.choices[0].message.content)

        try:
            new_page_dicts, _ = self.parse_output(response.choices[0].message.content)
        except ET.ParseError as e:
            print(f"Parse failed: {e}, skipping tick")
            new_page_dicts = []

        for d in new_page_dicts:
            page = self.dict_to_page(d, scientist.name)
            self.academia.route_page(page, scientist)

        print(f"Parsed {len(new_page_dicts)} pages, {scientist.name} now has {len(scientist.notes)} notes and {len(scientist.inbox)} letters in his inbox.")

    def dict_to_page(self, d, author):
        return Page(
            type=d.get('type', 'note'),
            title=d.get('title', ''),
            author=author,
            content=d.get('content', ''),
            sent_to=d.get('sent_to', '')
        )

    def parse_output(self, text):
        # this is all gross, sorry - trying to be robust if the model screws up

        s = re.sub(r'&(?!(?:\w+|#\d+|#x[\da-fA-F]+);)', '&amp;', text)
        s = re.sub(r'<(?!/?page[\s>]|/?action[\s/>])', '&lt;', s)

        opens = len(re.findall(r'<page[\s>]', s))
        closes = len(re.findall(r'</page>', s))
        s += '</page>' * max(0, opens - closes)

        root = ET.fromstring(f'<o>{s}</o>')
        pages = [{**p.attrib, 'content': (p.text or '').strip()} for p in root.findall('page')]
        actions = [a.attrib for a in root.findall('action')]
        return pages, actions

    def flatten_pages(self, pages, actions=None):
        parts = []
        for p in pages:
            if isinstance(p, dict):
                attrs = {k: v for k, v in p.items() if k != 'content'}
                content = p.get('content', '')
            else:
                attrs = {'id': p.short_id, 'type': p.type}
                if p.title: attrs['title'] = p.title
                if p.author: attrs['author'] = p.author
                if p.sent_from: attrs['sent_from'] = p.sent_from
                if p.sent_to: attrs['sent_to'] = p.sent_to
                content = p.content
            el = ET.Element('page', **attrs)
            el.text = '\n' + content + '\n'
            parts.append(ET.tostring(el, encoding='unicode'))
        for a in (actions or []):
            el = ET.Element('action', **a)
            parts.append(ET.tostring(el, encoding='unicode'))
        return '\n\n'.join(parts)
