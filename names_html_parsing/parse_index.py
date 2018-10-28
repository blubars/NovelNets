#! /usr/bin/env python3

#########################################################
# File Description:
#   Parse Infinite Jest Online Index page into 
#   named entities, hopefully.
#########################################################
import re
import json
from html.parser import HTMLParser
from collections import namedtuple

FILENAME = "infinite_jest_online_index.html"
#FILENAME = "test.html"

entities = []
NamedEntity = namedtuple('NamedEntity', 
        ['name', 'description', 'pages', 'notes', 'raw'])

states = {
        "INIT": 0,
        "SECTION START": 1,     # h1      **
        "ENTITY START": 2,      # p start **
        "NAME START": 3,        # b start
        "NAME END": 4,          # b end
        "DESCRIPTION START": 5, # br      **
        "DESCRIPTION END": 6,
        "ENTITY END": 7         # p end   **
}

def entity_to_json(e):
    d = {
            "name": e.name,
            "description": e.description,
            "pages": e.pages,
            "notes": e.notes
        }
    return json.dumps(d)

def print_entities(es):
    for i,e in enumerate(es):
        print("[{}] Name: {}".format(i, e.name))
        print("      Descr: {}".format(e.description))
        print("      Pgs: {}".format(e.pages))
        print("      Fns: {}".format(e.notes))
        print("")

def make_entity(_name, _text):
    e = { "name": _name, "raw": _text }
    return e

class IJParser(HTMLParser):
    state = states["INIT"]
    cur_section = ""
    cur_entity = None

    def complete_entity(self):
        # stupid check to see if valid section ([A-Z])
        if not self.cur_section.isupper():
            self.cur_entity = None
            return
        #print("FINISHING ENTITY: {}".format(self.cur_entity))
        elif not self.cur_entity is None:
            clean_name = self.cur_entity["name"].strip()
            clean_desc = self.cur_entity["raw"].strip()
            if clean_name != "":
                # find page numbers
                notes = re.findall(r"\bfn\.([0-9]+)/[0-9]+", clean_desc)
                temp = re.sub(r"-[0-9]+;",";",clean_desc)
                pgs = re.findall(r"\b([0-9]+);", temp)
                #pg_ranges = re.findall(r"\b([0-9]+-[0-9]+);", clean_desc)
                e = NamedEntity(
                        name=clean_name,
                        description=clean_desc,
                        pages=list(map(lambda x:int(x), pgs)),
                        notes=list(map(lambda x:int(x), notes)),
                        raw=clean_desc)
                entities.append(e)
                self.cur_entity = None

    def handle_state_change(self, new_state):
        #print("New state: {}".format(new_state))
        if states[new_state] == self.state:
            return
        if self.state == states["SECTION START"]:
            self.cur_section = self.cur_section.strip()
            print("NEW SECTION: {}".format(self.cur_section))
        # SECTION START
        if new_state == "SECTION START":
            if self.state != states["INIT"] and self.state != states["ENTITY END"]:
                print("Error, bad state transition")
            self.complete_entity()
        # ENTITY START: create new entity
        if new_state == "ENTITY START":
            if self.state != states["SECTION START"] and self.state != states["ENTITY END"]:
                print("Error, bad state transition")
            self.cur_entity = make_entity("", "")
        # ENTITY END: finish entity, add to list
        if new_state == "ENTITY END":
            if self.state != states["DESCRIPTION START"]:
                print("Error, bad state transition")
            self.complete_entity()

        # finish state transition
        self.state = states[new_state]

    def handle_starttag(self, tag, attrs):
        #print("Encountered a start tag:", tag)
        # state transitions:
        if tag == "h1":
            self.handle_state_change("SECTION START")
        elif tag == "p":
            self.handle_state_change("ENTITY START")
        elif tag == "br":
            self.handle_state_change("DESCRIPTION START")

    def handle_endtag(self, tag):
        #print("Encountered an end tag :", tag)
        # state transitions:
        if tag == "p":
            self.handle_state_change("ENTITY END")

    def handle_data(self, data):
        #print("Encountered some data  :'{}'".format(data))
        # state processing
        if self.state == states["SECTION START"]:
            self.cur_section += data
        elif self.state == states["ENTITY START"]:
            self.cur_entity["name"] += data
        elif self.state == states["DESCRIPTION START"]:
            self.cur_entity["raw"] += data
        # drop data if in wrong state

if __name__ == "__main__":
    with open(FILENAME) as f:
        parser = IJParser()
        for line in f:
            parser.feed(line)
        print("Num entities: {}".format(len(entities)))
        print_entities(entities)
        with open("entities.json", 'w') as fout:
            out_d = {"entities": []}
            for e in entities:
                d = { "name": e.name,
                      "description": e.description,
                      "pages": e.pages,
                      "notes": e.notes }
                out_d["entities"].append(d)
            fout.write(json.dumps(out_d, indent=2))


