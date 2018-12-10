import argparse
import sys
import spacy
import os
import json
import ner
from utils import get_entities, set_entities

################################################################################
# file stuff
################################################################################
def add_entity_psuedonym(entity, psuedonym):
    entities = get_entities()
    if not entities.get(entity):
        entities[entity]['patterns'] = []

    entities[entity]['patterns'].append([{"ORTH" : part } for part in psuedonym.split()])
    set_entities(entities)

def add_entity_attribute(entity, attribute, value):
    entities = get_entities()
    if not entities[entity].get('attributes'):
        entities[entity]['attributes'] =  {}

    entities[entity]['attributes'][attribute] = value
    set_entities(entities)

def print_list(lst, indent=2):
    indstr = ""
    for i in range(indent):
        indstr += ' '
    for item in lst:
        print("{}{}".format(indstr, item))

################################################################################
# entity processing
################################################################################
def process_section(section_num):
    print("+-------------------------------------")
    print("| Processing section " + str(section_num))
    print("+-------------------------------------")
    path = "{}infinite-jest-section-{:03d}.txt".format(get_sections_path(), section_num)

    with open(path, 'r') as f:
        section_text = f.read()

    doc = ner.tokenize(section_text)

    matcher, matches = ner.match_people(doc)

    missing, overlap, found = ner.find_missing_entities(doc)
    found_entities = sorted(list({ matcher.vocab.strings[m[0]] for m in matches })) 
    missing = sorted(list(missing))

    print("MATCHED ENTITIES:")
    print_list(found_entities)
    print("FOUND ENTITIES:")
    print_list(found)
    print("MISSING ENTITIES:")
    print_list(missing)

    for missing_entity in missing:
        print(f"missed entity: '{missing_entity}'. is this an entity? y/n")

        answer = input()

        if answer == 'y':
            handle_missed_entity(missing_entity)

    return missing

def handle_missed_entity(psuedonym):
    entities = get_entities()
    entity_names = sorted(list(entities.keys()))
    for i, entity in enumerate(entity_names):
        print(f"- {i}\t{entity}")

    print(f"if {psuedonym} is a psuedonym of someone in the list, enter their number. Else an id to use.")
    answer = input()

    prompt_string = ""
    if answer.isalpha():
        entity = answer
        prompt_string = f"add entity [{entity}] with psuedonym [{psuedonym}]? ('n' to skip)"
    else:
        entity = entity_names[int(answer)]
        prompt_string = f"add to entity [{entity}] psuedomyn [{psuedonym}]? ('n' to skip)"
    
    print(prompt_string)
    answer = input()
    if answer != 'n':
        add_entity_psuedonym(entity, psuedonym)

################################################################################
# attribute processing
################################################################################
def add_attribute_to_entities(attribute, skip_processed=False):
    entities = get_entities()

    for entity, entity_data in sorted(entities.items()):
        attributes = entity_data.get('attributes', None)
        if attributes and skip_processed:
            # if the attribute has ANY value (including None)
            # skip it if we're skipping things we've processed
            if attribute in set(attributes.keys()):
                continue

        handle_add_entity_attribute(entity, attribute)

def handle_add_entity_attribute(entity, attribute):
    entities = get_entities()

    attribute_values = set()
    for entity_attributes in [v['attributes'] for v in entities.values()]:
        value = entity_attributes.get(attribute, None)

        if value:
            attribute_values.add(value)

    attribute_values = sorted(list(attribute_values))

    print(f"if the entity has attribute {attribute} in the list, enter its number. If the attribute is a number, enter 'z'. If it has no value, hit enter. If it has a new value, enter that value.")

    for i, val in enumerate(attribute_values):
        print(f"- {i + 1}\t{val}")
    
    print(f"ENTITY: {entity}")
    answer = input()

    if not len(answer):
        value = None
    elif answer.isalpha():
        value = answer
    elif answer.isdigit():
        index = int(answer) - 1
        value = attribute_values[index]
    elif answer == 'z':
        print(f"enter numerical attribute {attribute} value for entity {entity}:")
        answer = input()

        # parse a float if there's a '.'
        if answer.count('.'):
            value = float(answer)
        else:
            value = int(answer)

    add_entity_attribute(entity, attribute, value)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--entities', '-e', default=False, action="store_true", help="add entities")
    parser.add_argument('--section', '-s', default=0, help="section to add entities from")
    parser.add_argument('--attributes', '-a', default=False, action="store_true", help="add attributes")
    parser.add_argument('--name', '-n', default="", help="attribute to add")
    parser.add_argument('--skip_processed', default=False, action="store_true", help="if true, skip entities with a value for the attribute or sections which we have processed")

    args = parser.parse_args()

    sections = [i for i in range(1, 193)]
    # processed_sections = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192]

    # SECTION NOTES:
    # 3: * Hal is 1st person, 'I', but never picked up by NER. 
    #      Is hal the only 1st person?
    # 5: * aren't actually any characters except Hal, doctors, C.T.
    #      But he's thinking of some; 'John N. R. Wayne', 'Dymphna', 
    #      'Petropolis Kahn', 'Stice', 'Polep', 'Donald Gately'
    # 6: * Only one character (Erdedy), but mentions Randi in passing
    #      and some woman bringing pot repeatedly but no name. both in
    #      thought only, not in person.
    # 7: * Confusing A.F. Just Hal talking with a 'professional 
    #      conversationalist' who turns out to be his dad. only 
    #      the 2 characters are present.
    # 9: * what. 'medical attache' and his 'wife'. 
    #      Mentions 'Prince Q---------'  ?
    # 12:  Still Mario & Hal talking at night, mention the Moms & Himself
    # 14:  Just Orin by himself being depressed, scattered thoughts.
    # 15:  Really just Hal thinking/background
    # 21:   Hal's pov
    # 36:   we're missing 2 ingersolls for possibly a hyphen?
    # 89:   will require close reading. (which I haven't done)
    # 94:   ditto
    # remove 'John' from john wayne

    # GlennK == Glenny Kubitz?
    # Jennie Bash/Jennifer Belbin getting crossed?
    # TinyEwell --> 

    if args.entities:
        sections_to_process = [i for i in sections if i not in processed_sections]
        if args.section:
            sections_to_process = [args.section]

        missing = set()
        for section_to_process in sections_to_process:
            for missed in process_section(section_to_process):
                missing.add(missed)

        for m in missing:
            print(m)
    elif args.attributes:
        attribute = args.name
        if attribute:
            add_attribute_to_entities(attribute, args.skip_processed)
        else:
            print('no attribute! quitting')

    # TODO:
    # - add ignore list
    # - autopopulate the processed sections list

    # - delete unused entities
    # - rerun on new entities
    #   - with scopes? 
