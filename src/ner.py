
import spacy
import json
import re
import io
from spacy.matcher import Matcher
from utils import get_entities
import io
import entities
from model import load_spacy


def on_match(matcher, doc, i, matches):
    # callback when entity pattern matched
    pass


def tokenize(raw_text):
    # loads or is cached
    nlp = load_spacy('en_core_web_md')
    return nlp(raw_text)


def get_matcher(nlp):
    matcher = Matcher(nlp.vocab)

    entities = get_entities()

    # load from above hand-made patterns
    for _id in entities.keys():
        patterns = entities[_id]['patterns']
        matcher.add(_id, None, *patterns)
    return matcher

def match_people(doc):
    # loads or is cached
    nlp = load_spacy('en_core_web_md')
    # use spacy Matcher to find known patterns
    matcher = get_matcher(nlp)
    matches = matcher(doc)
    #for match_id, start, end in matches:
    #    span = doc[start:end]
    #    print("'{}', start:{}, end:{}".format(span.text, start, end))
    return matcher, matches

def find_missing_entities(doc):
    # loads or is cached
    nlp = load_spacy('en_core_web_md')
    found = set()
    overlap = set()
    missing = set()
    # get hand-labeled matches
    hand_matcher, hand_matches = match_people(doc)
    for match_id, start, end in hand_matches:
        key = hand_matcher.vocab.strings[match_id] # this is dumb.
        span = str(doc[start:end])
        found.add(span + " (" + key + ")")
    # get auto-entity matches
    auto_entities = doc.ents
    auto_people = set()
    for ent in auto_entities:
        if ent.label_ == 'PERSON':
            name = re.sub('[\s+|\n+|]', ' ', ent.text.strip())
            auto_people.add(name)
    for token in auto_people:
        ms = hand_matcher(nlp(token))
        if len(ms) == 0:
            # auto token doesn't match any known hand-labeled entity
            if len(token):
                # only add it if it's got length
                missing.add(token)
        else:
            key = hand_matcher.vocab.strings[ms[0][0]] # this is dumb.
            overlap.add(token + " (" + key + ")")
    return missing, overlap, found


def run_ner(raw_text):
    doc = tokenize(raw_text)

    # matcher = Matcher(nlp.vocab)
    # nlp.add_pipe(matcher, before='ner')

    return doc.ents

def get_people(text_data):
    people = set()
    entities = run_ner(text_data)
    #person_ents = [re.sub('[\s+|\n+|]', ' ', ent.text.strip()) for ent in entities if ent.label_ == 'PERSON']
    for ent in entities:
        if ent.label_ == 'PERSON':
            name = re.sub('[\s+|\n+|]', ' ', ent.text.strip())
            people.add(name)
    return people

if __name__ == "__main__":
    section_text = ""#""get_section_text('./data/txt/sections/*.txt')
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
