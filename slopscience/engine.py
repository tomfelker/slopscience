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
Good morning, {name}!

Welcome to your job at the research institute!  Our patrons want to remind us of the research goal:
    We are studying a plausible mission architecture for getting to the moon by 2028.

They also stipulate that there are no funds for new experiments, we must instead cite existing research.  The mission itself, of course, will have significant cost.

You've just arrived in your office, your coffee is warm, and you have a few pages on your desk.

You can check them over, give it a good think, and of course you can write some new pages, in the same format.
Multiple short pages are encouraged.  Alas, our mail delivery is still not working, but the letters do go out.

Pages you write will handled differently depending on their type:
* "note" are private, and will stay on your desk for tomorrow, space permitting
* "letter" will be delivered to other researchers.  Names must match perfectly, 
* "article" will be submitted to journals, pending review.
You may also see pages of type:
* "article_for_review" - at your leisure, please respond to these with <action type="approve" article_id="blah"/>, or <action type="deny" article_id="blah"/>
* "subscribed_article" - articles from journals you have subscribed to
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
                {"role": "system", "content": flattened_pages}
            ],
            api_base="http://localhost:11434",
            max_tokens=self.max_generated_tokens,
            extra_body={"think": False}
        )

        print(f"=== {scientist.name} ===")
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
