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
            self.display_graph(str(section_num))

    def make_nodes(self, doc, matches):
        #self.people = ner.get_people(text)
        #self.G.add_nodes_from(self.people)
        self.people = set()
        for match_id, start, end in matches:
            key = self.matcher.vocab.strings[match_id] # this is dumb.
            self.people.add(key)
            #span = doc[start:end]
        print("NODES:\n{}".format(self.people))

    def make_edges(self, doc, matches):
        edgelist = []
        # dumbest way possible: link if within 100 tokens of eachother.
        for m1 in matches:
            for m2 in matches:
                #match_id, start, end
                #span = doc[start:end]
                if m1[0] == m2[0]:
                    continue
                if m2[1] - m1[1] < 100:
                    edgelist.append((m1, m2))
        for m1,m2 in edgelist:
            n1 = self.matcher.vocab.strings[m1[0]]
            n2 = self.matcher.vocab.strings[m2[0]]
            #print("Add edge:'{}, {}, pos=({},{})".format(
            #    doc[m1[1]:m1[2]], doc[m2[1]:m2[2]],
            #    m1[1], m2[1]))
            self.G.add_edge(n1, n2)
        if DEBUG:
            print("EDGES:")
            for m1,m2 in edgelist:
                print("  '{} <--> {}, pos=({},{})".format(
                    doc[m1[1]:m1[2]], doc[m2[1]:m2[2]],
                    m1[1], m2[1]))


    def display_graph(self, name):
        fig = plt.figure(1)
        ax = plt.gca()
        nx.draw(self.G, ax=ax) #labels=labels)
        plt.title("Section " + name)
        plt.tight_layout()
        #plt.show()
        plt.savefig("section_" + name + ".pdf")
        plt.close(fig)

if __name__ == "__main__":
    # build a graph per section.
    gg = Graphify(SECTION_PATH)
    gg.process_section(1)


