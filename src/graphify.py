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

class Graphify:
    def __init__(self, path):
        self.section_path = path
        self.G = nx.Graph()
        self.people = set()

        self.name_id_map = {}
        self.unused_id = 0
        self.threshold = 1000
        self.web = webweb()

    def process_section(self, section_num):
        path = "{}infinite-jest-section-{:03d}.txt".format(self.section_path, section_num)
        with open(path, 'r') as f:
            section_text = f.read()
            doc = ner.tokenize(section_text)
            self.matcher, matches = ner.match_people(doc)
            if DEBUG:
                print("MATCHES:")
                for m in matches:
                    print("  '{}': ({}, {})".format(
                        self.matcher.vocab.strings[m[0]], m[1], m[2]))
                missing, overlap = ner.find_missing_entities(doc)
                print("MISSING ENTITIES:\n{}".format(missing))
                print("FOUND ENTITIES:\n{}".format(overlap))
            # 1. recognize entities
            self.make_nodes(doc, matches)
            # 2. link entities. (rule?)
            self.make_edges(doc, matches)
            # 3. graph.
            # self.display_graph(str(section_num))

    def make_nodes(self, doc, matches):
        for match_id, start, end in matches:
            key = self.matcher.vocab.strings[match_id] # this is dumb.

            if key not in self.people:
                self.people.add(key)

                entity_id = self.get_entity_id(key)

                self.G.add_node(entity_id)
                self.G.nodes[entity_id]['name'] = key

        print("NODES:\n{}".format(self.people))

    def get_entity_id(self, entity_string):
        if not self.name_id_map.get(entity_string):
            print(entity_string)
            print(len(entity_string))
            self.name_id_map[entity_string] = self.unused_id
            self.unused_id += 1

        return self.name_id_map.get(entity_string)

    def get_entity_from_match(self, match):
        return self.matcher.vocab.strings[match[0]]

    def get_entity_id_from_match(self, match):
        return self.get_entity_id(self.get_entity_from_match(match))

    def make_edges(self, doc, matches):
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
                    edgelist.append((m1, m2))

        for m1, m2 in edgelist:
            entity_1_id = self.get_entity_id_from_match(m1)
            entity_2_id = self.get_entity_id_from_match(m2)

            if self.G.has_edge(entity_1_id, entity_2_id):
                self.G[entity_1_id][entity_2_id]['weight'] += 1
            else:
                self.G.add_edge(entity_1_id, entity_2_id, weight=1)

        if DEBUG:
            print("EDGES:")
            for m1,m2 in edgelist:
                print("  '{} <--> {}, pos=({},{})".format(
                    doc[m1[1]:m1[2]], doc[m2[1]:m2[2]],
                    m1[1], m2[1]))


    def add_graph_frame(self):
        self.web.networks.infinite_jest.add_frame_from_networkx_graph(self.G)
        
        #fig = plt.figure(1)
        #ax = plt.gca()
        #nx.draw(self.G, ax=ax) #labels=labels)
        #plt.title("Section " + name)
        #plt.tight_layout()
        ##plt.show()
        #plt.show()
        #plt.close(fig)

if __name__ == "__main__":
    # build a graph per section.
    gg = Graphify(SECTION_PATH)

    gg.process_section(1)
    gg.add_graph_frame()
    gg.process_section(10)
    gg.add_graph_frame()
    # for i in range(1, 5):
    #     gg.process_section(i)
    #     gg.add_graph_frame()

    gg.web.draw()


