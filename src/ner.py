import spacy
from utils import get_section_text
import json
import re
import io

nlp = spacy.load('en_core_web_md')


def run_ner(text_data):

    doc = nlp(text_data)

    # matcher = Matcher(nlp.vocab)
    # nlp.add_pipe(matcher, before='ner')

    return doc.ents

def get_people(text_data):
    people = set()
    for key, value in section_text.items():
        entities = run_ner(value)
        person_ents = [re.sub('[\s+|\n+|]', ' ', ent.text.strip()) for ent in entities if ent.label_ == 'PERSON']
        people.add(person_ents)
    return people

if __name__ == "__main__":
    section_text = get_section_text('./data/txt/sections/*.txt')
    data = {}
    people = set()
    orgs = set()
    for key, value in section_text.items():
        entities = run_ner(value)
        person_ents = [re.sub('[\s+|\n+|]', ' ', ent.text.strip()) for ent in entities if ent.label_ == 'PERSON']
        org_ents = [ent.text.strip() for ent in entities if ent.label_ == 'ORGS']
        [people.add(p) for p in person_ents]
        [orgs.add(o) for o in org_ents]
    data['people'] = list(people)
    data['organizations'] = list(orgs)
    with io.open('./data/named_entities.json', 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)
