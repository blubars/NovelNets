#! /usr/bin/env python3

#########################################################
# File Description:
#   Turn a book, delimited into sections, into a graph.
# Authors: Hunter Wapman, Brian Lubars, Carl Mueller
# Date: 11/16/18
#########################################################

# 1. read in named entities
# 2. for each section:
#    a. recognize entities
#    b. link entities. (rule?)
#    c. graph.

# Problems & ideas to improve:
# 1. smooth weights over sections, don't count edges
#    too many times within one interaction
# 2. minimum threshold: don't include edges if only 
#    mentioned once? could just be talking about someone.
#     -- how do we know if someone's there vs. being
#        talked about?
# 3. it seems to be matching multiple times, 
#    if multiple patterns even within one entity apply
# 4. doesn't match across '.', e.g. 'Comp. Director'

#########################################################
# Imports
#########################################################
from collections import defaultdict
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from webweb.webweb import webweb
import math

import ner

#########################################################
# Globals
#########################################################
SECTION_PATH = '../data/txt/sections/'
DEBUG = 1

#########################################################
# Function definitions
#########################################################
# util to print list w/ indentation
def print_list(lst, indent=2):
    indstr = ""
    for i in range(indent):
        indstr += ' '
    for item in lst:
        print("{}{}".format(indstr, item))

class Graphify:
    def __init__(self, path, edge_threshold):
        self.section_path = path
        self.G = nx.Graph()
        self.people = set()

        self.name_id_map = {}
        self.unused_id = 0
        self.threshold = edge_threshold
        self.web = webweb()

    def process_section(self, section_num):
        print("+-------------------------------------")
        print("| Processing section " + str(section_num))
        print("+-------------------------------------")
        path = "{}infinite-jest-section-{:03d}.txt".format(self.section_path, section_num)
        with open(path, 'r') as f:
            section_text = f.read()

        doc = ner.tokenize(section_text)
        self.matcher, matches = ner.match_people(doc)
        if DEBUG > 1:
            print("MATCHES:")
            for m in matches:
                print("  '{}': ({}, {})".format(
                    self.get_entity_from_match(m), m[1], m[2]))
        #if DEBUG:
        missing, overlap, found = ner.find_missing_entities(doc)
        print("MISSING ENTITIES:")
        print_list(missing)
        print("FOUND ENTITIES:")
        print_list(found)
        # 1. recognize entities
        self.make_nodes(doc, matches)
        # 2. link entities. (rule?)
        self.make_edges(doc, matches)
        # 3. graph.
        # self.display_graph(str(section_num))
        if DEBUG > 1:
            self.print_graph_edgelist()

    def make_nodes(self, doc, matches):
        if DEBUG:
            print("NODES:")
        section_people = set() # ppl in this section
        for match_id, start, end in matches:
            key = self.matcher.vocab.strings[match_id] # this is dumb.
            section_people.add(key)
            #if key not in self.people:
        new_people = section_people - self.people
        # keep node ids in same order each run by sorting here.
        for key in sorted(list(new_people)):
            self.people.add(key)
            entity_id = self.get_entity_id(key)
            if DEBUG:
                print("  New node: ({}, {})".format(key, entity_id))
            self.G.add_node(entity_id)
            self.G.nodes[entity_id]['name'] = key

        #print("NEW NODES:\n{}".format(new_people))

    def get_entity_id(self, entity_string):
        if self.name_id_map.get(entity_string, None) == None:
            self.name_id_map[entity_string] = self.unused_id
            self.unused_id += 1

        return self.name_id_map.get(entity_string)

    def get_entity_from_match(self, match):
        return self.matcher.vocab.strings[match[0]]

    def get_entity_id_from_match(self, match):
        return self.get_entity_id(self.get_entity_from_match(match))

    def add_edge_from_matches(self, first, second):
        first_id, first_start, first_end = first
        second_id, second_start, second_end = second
        if first_id == second_id:
            return None
        if first_start > second_start:
            return self.add_edge_from_matches(second, first)
        if second_start - first_start > self.threshold:
            return None

        key1 = self.get_entity_from_match(first)
        key2 = self.get_entity_from_match(second)
        first_entity_id = self.get_entity_id(key1)
        second_entity_id = self.get_entity_id(key2)
        if self.G.has_edge(first_entity_id, second_entity_id):
            self.G[first_entity_id][second_entity_id]['weight'] += 1
        else:
            self.G.add_edge(first_entity_id, second_entity_id, weight=1)
        if DEBUG > 1:
            print("  - Incr weight ({}({}),{}({})), pos=({},{})".format(
                key1, first_entity_id, key2, second_entity_id,
                first_start, second_start))
        return (key1, key2)

    def make_edges(self, doc, matches):
        new_edges = defaultdict(lambda: defaultdict(int))
        # dumbest way possible: link if within THRESHOLD tokens of eachother.
        # note: this adds 1 edges per match pair, only in one direction.
        for i in range(len(matches)-1):
            for j in range(i+1, len(matches)):
                first = matches[i]
                second = matches[j]
                new_edge = self.add_edge_from_matches(first, second)
                if new_edge:
                    key1, key2 = new_edge
                    if key1 > key2:
                        key1, key2 = key2, key1
                    new_edges[key1][key2] += 1
        if DEBUG:
            print("EDGES:")
            for key1, inner_dict in new_edges.items():
                for key2, weight in inner_dict.items():
                    print("  {} <--> {}, weight:+{}".format(key1, key2, weight))
                    print("\t  {} <--> {}, weight:+{}".format(self.get_entity_id(key1), self.get_entity_id(key2), weight))

    def print_graph_edgelist(self):
        print("Graph edges & weights")
        for n, nbrsdict in self.G.adjacency():
            for nbr,eattr in nbrsdict.items():
                print((n,nbr,eattr['weight']))
        #print(self.G.edges(data='weight'))

    def add_graph_frame(self):
        #for n in self.G.nodes():
        #    print(n)
        self.web.networks.infinite_jest.add_frame_from_networkx_graph(self.G)

    def display_graph(self, section_num):
        labels = {}
        for n in self.G.nodes():
            labels[n] = self.G.node[n]['name']
        fig = plt.figure(1)
        ax = plt.gca()
        # nx.draw(self.G, ax=ax, labels=labels)
        # plt.title("Section " + str(section_num))
        # plt.tight_layout()
        #plt.show()
        # plt.savefig("section_" + str(section_num) + ".pdf")
        # plt.close(fig)

if __name__ == "__main__":
    # build a graph per section.
    gg = Graphify(SECTION_PATH, 500)

    for section in range(1,36):
        gg.process_section(section)
        gg.add_graph_frame()
        gg.display_graph(section)

    gg.web.draw()

    # PROGRESS: 
    #   sections 1-15 done. slow going.
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


