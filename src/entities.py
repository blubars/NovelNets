import spacy
import os
import json
from spacy.matcher import Matcher
import ner

SECTION_PATH = '../data/txt/sections/'
ENTITIES_PATH = 'entities.json'

# hand-made patterns and maybe future methods to make patterns 
# automatically

# docs: https://spacy.io/usage/linguistic-features#rule-based-matching

def get_matcher(nlp):
    matcher = Matcher(nlp.vocab)
    # TODO: how do we do this in an automated fashion?
    #  ...or all by hand i guess.
    load_patterns(matcher)
    return matcher

def on_match(matcher, doc, i, matches):
    # callback when entity pattern matched
    pass

def get_saved_entities():
    with open(get_entities_file_path(), 'r') as f:
        return json.load(f)

def get_entities_file_path():
    return os.path.join(os.getcwd(), ENTITIES_PATH)

def add_entity_psuedonym(entity, psuedonym):
    entities = get_saved_entities()
    if not entities.get(entity):
        entities[entity] = []

    entities[entity].append([{"ORTH" : part } for part in psuedonym.split()])

    with open(get_entities_file_path(), 'w') as f:
        json.dump(entities, f)
    
def load_patterns(matcher):
    # possible automated method:
    #nlp = spacy.load('en_core_web_sm')
    #matcher = PhraseMatcher(nlp.vocab)
    #terminology_list = ['Barack Obama', 'Angela Merkel', 'Washington, D.C.']
    #patterns = [nlp(text) for text in terminology_list]
    #matcher.add('TerminologyList', None, *patterns)
    entities = get_saved_entities()

    # load from above hand-made patterns
    for _id, patterns in entities.items():
        matcher.add(_id, None, *patterns)


def print_list(lst, indent=2):
    indstr = ""
    for i in range(indent):
        indstr += ' '
    for item in lst:
        print("{}{}".format(indstr, item))

def process_section(section_num):
    print("+-------------------------------------")
    print("| Processing section " + str(section_num))
    print("+-------------------------------------")
    path = "{}infinite-jest-section-{:03d}.txt".format(SECTION_PATH, section_num)

    with open(path, 'r') as f:
        section_text = f.read()

    doc = ner.tokenize(section_text)

    matcher, matches = ner.match_people(doc)

    missing, overlap, found = ner.find_missing_entities(doc)
    found_entities = sorted(list({ matcher.vocab.strings[m[0]] for m in matches })) 
    missing = sorted(list(missing))

    print("MATCHED ENTITIES:")
    print_list(found_entities)
    print("MISSING ENTITIES:")
    print_list(missing)

    for missing_entity in missing:
        print(f"missed entity: '{missing_entity}'. is this an entity? y/n")

        answer = input()

        if answer == 'y':
            handle_missed_entity(missing_entity)


def handle_missed_entity(missing_entity):
    entities = get_saved_entities()
    entity_names = sorted(list(entities.keys()))
    for i, entity in enumerate(entity_names):
        print(f"- {i}\t{entity}")

    print(f"if {missing_entity} is a psuedonym of someone in the list, enter their number. Else 'n' or enter.")
    answer = input()

    if answer == 'n' or not len(answer):
        handle_create_new_entity(missing_entity)
    else:
        entity_index = int(answer)
        psuedonym = missing_entity
        handle_create_entity_pseudonym(entity_names[entity_index], psuedonym)
    

def handle_create_new_entity(psuedonym):
    print("input an entity id for this entity psuedonym:")
    entity = input()
    print(f"add entity [{entity}] with psuedonym [{psuedonym}]? ('n' to skip)")
    answer = input()
    if answer != 'n':
        add_entity_psuedonym(entity, psuedonym)

def handle_create_entity_pseudonym(entity, psuedonym):
    print(f"add to entity [{entity}] psuedomyn [{psuedonym}]? ('n' to skip)")
    answer = input()
    if answer != 'n':
        add_entity_psuedonym(entity, psuedonym)

if __name__ == '__main__':
    sections = [i for i in range(1, 193)]
    processed_sections = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]

    # section 21 is POV (Hal)
    # section 36 we're missing 2 ingersolls for possibly a hyphen?

    sections_to_process = [i for i in sections if i not in processed_sections]

    for section_to_process in sections_to_process:
        process_section(section_to_process)



