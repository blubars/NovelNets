import spacy
import json
import sys
import re
import io
import os
from spacy.matcher import Matcher
import io
from model import load_spacy

class Match(dict):
    def __init__(self, key="", start=0, end=0, text=""):
        # init a dict so we can json.dump this
        dict.__init__(self, key=key, start=start, end=end, text=text)

        self.key = key
        self.start = start
        self.end = end
        self.text = text

    def __str__(self):
        return "'{}': {}, {}".format(self.text, self.start, self.end)

class NERMatcher:
    """ Run NER on input text. Relies on EntityIO class for
        reading/writing saved entities from previous disambiguation """
    def __init__(self, entityIO):
        self.entityIO = entityIO

    def on_match(self, matcher, doc, i, matches):
        # callback when entity pattern matched
        pass

    def print_list(self, lst, indent=2):
        indstr = ""
        for i in range(indent):
            indstr += ' '
        for item in lst:
            print("{}{}".format(indstr, item))

    def recognize_text(self, text, print_results=False):
        nlp = load_spacy('en_core_web_md')
        doc = nlp(text)
        matches = self.get_doc_matches(doc)

        matched_entities = self.get_matched_entities(matches)
        matched_entity_aliases = self.get_matched_entity_aliases(matches)
        missed_entities = self.get_missed_entities(doc)

        if print_results:
            print("MATCHED ENTITIES:")
            self.print_list(matched_entities)
            print("MATCHED ALIASES:")
            self.print_list(matched_entity_aliases)
            print("MISSED:")
            self.print_list(missed_entities)

        return {
            'matches' : matches,
            'text_length' : len(doc),
            'found' : {
                'entities' : matched_entities,
                'aliases' : matched_entity_aliases,
            },
            'missed' : missed_entities,
        }

    def get_doc_matches(self, doc):
        matcher = self.get_matcher()
        return [self.make_match(matcher, doc, _match) for _match in matcher(doc)]

    def get_matched_entities(self, matches):
        found = {match.key for match in matches}
        return sorted(list(found))

    def get_matched_entity_aliases(self, matches):
        found = {"{} ({})".format(match.text, match.key) for match in matches}
        return sorted(list(found))

    def get_missed_entities(self, doc):
        nlp = load_spacy('en_core_web_md')

        matcher = self.get_matcher()

        missing = set()

        # get auto-entity matches
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                name = re.sub('[\s+|\n+|]', ' ', ent.text.strip())

                # continue processing only if there's remaining characters
                if not name:
                    continue

                # the matcher will return an empty list if there is no match
                if len(matcher(nlp(name))) == 0:
                    missing.add(name)

        return sorted(list(missing))

    def make_match(self, matcher, doc, match):
        match_id, start, end = match
        key = matcher.vocab.strings[match_id]
        text = doc[start:end].text

        return Match(key, start, end, text)

    def get_matcher(self):
        nlp = load_spacy('en_core_web_md')
        matcher = Matcher(nlp.vocab)

        entities = self.entityIO.get_entities()

        # load from above hand-made patterns
        for _id in entities.keys():
            patterns = entities[_id]['patterns']
            matcher.add(_id, None, *patterns)
        return matcher
