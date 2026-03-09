from litellm import completion

import re
import xml.etree.ElementTree as ET

import random

class Engine:
    def __init__(self, chronicle_path):
        self.chronicle_path = chronicle_path
        self.pages = []

        self.max_pages_in_context = 5
        self.max_generated_tokens = 2000

        self.system_prompt = """
Good morning, RichardFeynllm!

Welcome to your job at the research institute!  Our patrons want to remind us of the research goal:
    Determining the purpose of sleep.

They also stipulate that there are no funds for new experiments, we must instead cite existing research.

You've just arrived in your office, your coffee is warm, and you have a few pages on your desk.

You can check them over, give it a good think, and of course you can write some new pages, in the same format.
Multiple short pages are encouraged.  Alas, our mail delivery is still not working, but the letters do go out.

Pages you write will handled differently depending on their type:
* "notes" are private, and will stay on your desk for tomorrow, space permitting
* "letter" will be delivered to other researchers
* "article" will be submitted to journals, pending review.
You may also see pages of type:
* "article_for_review" - at your leisure, please respond to these with <action type="approve" article_id="blah"/>, or <action type="deny" article_id="blah"/>
* "subscribed_article" - articles from journals you have subscribed to
"""

        self.add_test_data()

    def add_test_data(self):
        self.pages.extend(
            [
                {
                    "id": "i389ks",
                    "type": "letter",
                    "from": "AlbertSlopmann",
                    "content": "Howdy!  I was just reading about the new mirror symmetry breaking, and I thought of you - do you think it suggests new physics!"
                },
                {
                    "id": "ydg54",
                    "type": "article",
                    "from": "JournalOfAppliedSlop",
                    "content": "We have done an experiment on eggs - it turns out, if you eat more than 50 eggs per day, you get a stomach ache."
                },
            ]
        )

    def run(self):
        while True:
            self.run_tick()

    def run_tick(self):

        selected_pages = list(self.pages)
        while len(selected_pages) > self.max_pages_in_context:
            selected_pages.pop(random.randrange(len(selected_pages)))

        flattened_pages = self.flatten_pages(selected_pages)

        response = completion(
            model="ollama/qwen3.5:35b",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": flattened_pages}
            ],
            api_base="http://localhost:11434",
            max_tokens=self.max_generated_tokens,
            extra_body={"think": False}
        )

        print("======================================================================================================================")
        print(response.choices[0].message.content)

        try:
            new_pages, new_actions = self.parse_output(response.choices[0].message.content)
        except ET.ParseError as e:
            print(f"Parse failed: {e}, skipping tick")
            new_pages, new_actions = [], []

        self.pages.extend(new_pages)

        print(f"Parsed {len(new_pages)} pages, now have {len(self.pages)}")

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
            el = ET.Element('page', **{k: v for k, v in p.items() if k != 'content'})
            el.text = '\n' + p.get('content', '') + '\n'
            parts.append(ET.tostring(el, encoding='unicode'))
        for a in (actions or []):
            el = ET.Element('action', **a)
            parts.append(ET.tostring(el, encoding='unicode'))
        return '\n\n'.join(parts)