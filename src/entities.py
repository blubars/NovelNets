import argparse
import sys
import spacy
import os
import json
import ner
from utils import get_entities, set_entities
import text_io

################################################################################
# file stuff
################################################################################
def add_entity_alias(entity, alias):
    entities = get_entities()
    if not entities.get(entity):
        entities[entity]['patterns'] = []

    entities[entity]['patterns'].append([{"ORTH" : part } for part in alias.split()])
    set_entities(entities)

def add_entity_attribute(entity, attribute, value):
    entities = get_entities()
    if not entities[entity].get('attributes'):
        entities[entity]['attributes'] =  {}

    entities[entity]['attributes'][attribute] = value
    set_entities(entities)

################################################################################
# entity processing
################################################################################
def process_section(section_num):
    print("+-------------------------------------")
    print("| Processing section " + str(section_number))
    print("+-------------------------------------")
    section_text = text_io.interpolate_section_endnotes(text_io.get_section(section_number))

    result = ner.recognize_text(section_text, print_results=True)

    for missing_entity in result['missed']:
        print(f"missed entity: '{missing_entity}'. is this an entity? y/n")

        answer = input()

        if answer == 'y':
            handle_missed_entity(missing_entity)

    return missing

def handle_missed_entity(alias):
    entities = get_entities()
    entity_names = sorted(list(entities.keys()))
    for i, entity in enumerate(entity_names):
        print(f"- {i}\t{entity}")

    print(f"if {alias} is an alias of someone in the list, enter their number. Else an id to use.")
    answer = input()

    prompt_string = ""
    if answer.isalpha():
        entity = answer
        prompt_string = f"add entity [{entity}] with alias [{alias}]? ('n' to skip)"
    else:
        entity = entity_names[int(answer)]
        prompt_string = f"add to entity [{entity}] psuedomyn [{alias}]? ('n' to skip)"
    
    print(prompt_string)
    answer = input()
    if answer != 'n':
        add_entity_alias(entity, alias)

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
