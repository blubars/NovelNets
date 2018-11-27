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

from ner import run_ner, get_people, match_people, tokenize

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
            doc = tokenize(section_text)
            matches = match_people(doc)
            # 1. recognize entities
            self.make_nodes(doc, matches)
            # 2. link entities. (rule?)
            self.make_edges(doc, matches)
            # 3. graph.
            self.display_graph(str(section_num))

    def make_nodes(self, doc, matches):
        #self.people = get_people(text)
        #self.G.add_nodes_from(self.people)
        self.people = set()
        for match_id, start, end in matches:
            self.people.add(match_id)
            #span = doc[start:end]
        print("NODES:\n{}".format(self.people))

    def make_edges(self, doc, matches):
        edgelist = []
        # dumbest way possible: link if within 100 tokens of eachother.
        for m1 in matches:
            for m2 in matches:
                #match_id, start, end
                #span = doc[start:end]
                if m1.match_id == m2.match_id:
                    continue
                if m2.start - m1.start < 100:
                    edgelist.append(m1, m2)
                print("'{}', start:{}, end:{}".format(span.text, start, end))
        print("Add edge:'{}', pos:({},{})".format(span.text, start, end))
        for edge in edgelist:
            n1 = m1.match_id
            n2 = m2.match_id
            print("Add edge:'{}, {}, pos=({},{})".format(
                doc[m1.start:m1.end], doc[m2.start:m2.end],
                m1.start, m2.start))
            G.add_edge(n1, n2)

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


