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
            if DEBUG:
                missing, overlap = ner.find_missing_entities(doc)
                print("MISSING ENTITIES:")
                print_list(missing)
                print("FOUND ENTITIES:")
                print_list(overlap)
            # 1. recognize entities
            self.make_nodes(doc, matches)
            # 2. link entities. (rule?)
            self.make_edges(doc, matches)
            # 3. graph.
            # self.display_graph(str(section_num))

    def make_nodes(self, doc, matches):
        if DEBUG:
            print("NODES:")
        section_people = set() # ppl in this section
        for match_id, start, end in matches:
            key = self.matcher.vocab.strings[match_id] # this is dumb.
            section_people.add(key)
            #if key not in self.people:
        new_people = section_people - self.people
        for key in new_people:
            self.people.add(key)
            entity_id = self.get_entity_id(key)
            if DEBUG:
                print("  New node: ({}, {})".format(key, entity_id))
            self.G.add_node(entity_id)
            self.G.nodes[entity_id]['name'] = key

        #print("NEW NODES:\n{}".format(new_people))

    def get_entity_id(self, entity_string):
        if self.name_id_map.get(entity_string) is None:
            self.name_id_map[entity_string] = self.unused_id
            self.unused_id += 1

        return self.name_id_map.get(entity_string)

    def get_entity_from_match(self, match):
        return self.matcher.vocab.strings[match[0]]

    def get_entity_id_from_match(self, match):
        return self.get_entity_id(self.get_entity_from_match(match))

    def make_edges(self, doc, matches):
        if DEBUG:
            print("EDGES:")
        new_edges = defaultdict(lambda: defaultdict(int))
        edgelist = []
        # dumbest way possible: link if within THRESHOLD tokens of eachother.
        for m1 in matches:
            for m2 in matches:
                #match_id, start, end
                #span = doc[start:end]
                if m1[0] == m2[0]:
                    continue

                if m1[0] > m2[0]:
                    m1, m2 = m2, m1

                if abs(m2[1] - m1[1]) < self.threshold:
                    key1 = self.get_entity_from_match(m1)
                    key2 = self.get_entity_from_match(m2)
                    new_edges[key1][key2] += 1
                    edgelist.append((m1, m2))
                    if DEBUG > 1:
                        print("  {} <--> {}, pos=({},{})".format(
                            doc[m1[1]:m1[2]], doc[m2[1]:m2[2]],
                            m1[1], m2[1]))

        for m1, m2 in edgelist:
            entity_1_id = self.get_entity_id_from_match(m1)
            entity_2_id = self.get_entity_id_from_match(m2)

            if self.G.has_edge(entity_1_id, entity_2_id):
                self.G[entity_1_id][entity_2_id]['weight'] += 1
            else:
                self.G.add_edge(entity_1_id, entity_2_id, weight=1)

        if DEBUG:
            for key1, inner_dict in new_edges.items():
                for key2, weight in inner_dict.items():
                    print("  {} <--> {}, weight:+{}".format(key1, key2, weight))

    def add_graph_frame(self):
        self.web.networks.infinite_jest.add_frame_from_networkx_graph(self.G)

    def display_graph(self, section_num):
        labels = {}
        for n in self.G.nodes():
            labels[n] = self.G.node[n]['name']
        fig = plt.figure(1)
        ax = plt.gca()
        nx.draw(self.G, ax=ax, labels=labels)
        plt.title("Section " + str(section_num))
        plt.tight_layout()
        #plt.show()
        plt.savefig("section_" + str(section_num) + ".pdf")
        plt.close(fig)

if __name__ == "__main__":
    # build a graph per section.
    gg = Graphify(SECTION_PATH, 1000)

    for section in range(1,10):
        gg.process_section(section)
        #gg.add_graph_frame()
        gg.display_graph(section)

    #gg.web.draw()


