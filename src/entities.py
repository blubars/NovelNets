import argparse
import sys
import spacy
import os
import json
import ner
import text_io
import hashlib

################################################################################
# entity processing
################################################################################
class EntityIO:
    """ Save/restore known recognized entities. """
    def __init__(self, base_data_path):
        entities_dir = os.path.join(base_data_path, "ner")
        self.entities_path = os.path.join(entities_dir, "entities.json")
        if not os.path.exists(entities_dir):
            os.mkdir(entities_dir)

    def get_entities_hash(self):
        with open(self.get_entities_path(), 'rb') as f:
            data = f.read()
        entities_hash = hashlib.md5(data).hexdigest()
        return entities_hash

    def entity_file_exists(self):
        return os.path.exists(self.get_entities_path())

    def get_entities(self):
        try:
            with open(self.get_entities_path(), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            #print("Error: no entities file found. Please generate it!")
            #sys.exit(1)
            return {}

    def set_entities(self, entities):
        with open(self.get_entities_path(), 'w') as f:
            json.dump(entities, f, indent=4, sort_keys=True)

    def get_entities_path(self):
        return self.entities_path

    def process_section(self, textIO, section_number):
        print("+-------------------------------------")
        print("| Processing section " + str(section_number))
        print("+-------------------------------------")
        section_text = textIO.interpolate_section_endnotes(textIO.get_section(section_number))

        ner_matcher = ner.NERMatcher(self)
        result = ner_matcher.recognize_text(section_text, print_results=True)

        for missing_entity in result['missed']:
            print(f"missed entity: '{missing_entity}'. is this an entity? (y/N)")
            answer = input()
            if answer == 'y':
                self.handle_missed_entity(missing_entity)


    def handle_missed_entity(self, alias):
        entities = self.get_entities()
        entity_names = sorted(list(entities.keys()))
        if len(entity_names) > 0:
            for i, entity in enumerate(entity_names):
                print(f"- {i}\t{entity}")

            print(f"if {alias} is an alias of someone in the list, enter their number. Else an id to use.")
        else:
            print(f"Adding '{alias}'. Please enter an id to use.")
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
            self.add_entity_alias(entity, alias)

################################################################################
# file stuff
################################################################################
    def add_entity_alias(self, entity, alias):
        entities = self.get_entities()
        if not entities.get(entity):
            # new entity ID.
            entities[entity] = {}
            entities[entity]['patterns'] = []
            entities[entity]['attributes'] = {}

        entities[entity]['patterns'].append([{"ORTH" : part } for part in alias.split()])
        self.set_entities(entities)

    def add_entity_attribute(self, entity, attribute, value):
        entities = self.get_entities()
        if not entities[entity].get('attributes'):
            entities[entity]['attributes'] =  {}

        entities[entity]['attributes'][attribute] = value
        self.set_entities(entities)

    ################################################################################
    # attribute processing
    ################################################################################
    def add_attribute_to_entities(self, attribute, skip_processed=False):
        entities = self.get_entities()

        for entity, entity_data in sorted(entities.items()):
            attributes = entity_data.get('attributes', None)
            if attributes and skip_processed:
                # if the attribute has ANY value (including None)
                # skip it if we're skipping things we've processed
                if attribute in set(attributes.keys()):
                    continue

            self.handle_add_entity_attribute(entity, attribute)

    def handle_add_entity_attribute(self, entity, attribute):
        entities = self.get_entities()

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

        self.add_entity_attribute(entity, attribute, value)


def run_entity_processing(entityIO, textIO, sections, add_entities=False, 
        attributes=False, name="", skip_processed=False):
    """ Process text one section at a time, prompting user for confirmation
        of new entities, and saving known entities into the JSON file.
        Options: 
          - add_entities: add entities
          - section: section to add entities from
          - attributes: add attributes
          - name: attribute to add
          - skip_processed: if true, skip entities with a value for the 
            attribute or sections which we have processed
    """

    processed_sections = []
    if add_entities:
        sections_to_process = [i for i in sections if i not in processed_sections]
        for section_to_process in sections_to_process:
            entityIO.process_section(textIO, section_to_process)
    elif attributes:
        attribute = name
        if attribute:
            entityIO.add_attribute_to_entities(attribute, skip_processed)
        else:
            print('no attribute! quitting')


#if __name__ == '__main__':
#    parser = argparse.ArgumentParser()
#    parser.add_argument('--entities', '-e', default=False, action="store_true", help="add entities")
#    parser.add_argument('--section', '-s', default=0, help="section to add entities from")
#    parser.add_argument('--attributes', '-a', default=False, action="store_true", help="add attributes")
#    parser.add_argument('--name', '-n', default="", help="attribute to add")
#    parser.add_argument('--skip_processed', default=False, action="store_true", help="if true, skip entities with a value for the attribute or sections which we have processed")
#    args = parser.parse_args()

    # TODO:
    # - add ignore list
    # - autopopulate the processed sections list

    # - delete unused entities
    # - rerun on new entities
    #   - with scopes? 
