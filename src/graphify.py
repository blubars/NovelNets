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

from ner import run_ner
from utils import get_section_text, get_people

#########################################################
# Globals
#########################################################
SECTION_PATH = './data/txt/sections/'

#########################################################
# Function definitions
#########################################################

class Graphify:
    def __init__(self, path):
        self.section_path = path
        self.G = nx.Graph()

    def process_section(self, section_num):
        path = self.section_path + str(section_num) + '.txt'
        section_text = get_section_text(path)
        for key, value in section_text.items():
            print(key)
            print(value)
            return
            # 1. recognize entities
            self.make_edges(section)
            # 2. link entities. (rule?)
            self.make_nodes(section)
            # 3. graph.
            self.display_graph(str(section_num))

    def make_nodes(self, text):
        self.people = get_people(text)
        self.G.add_nodes_from(self.people)

    def make_edges(self, text):
        for edge in edgelist:
            G.add_edge(n1, n2)

    def display_graph(self, name):
        fig = plt.figure(1)
        ax = plt.gca()
        nx.draw(G, ax=ax, node_color=C, labels=labels)
        plt.title("Section " + name)
        plt.tight_layout()
        plt.show()
        plt.savefig("section_" + name + ".pdf")
        plt.close(fig)

if __name__ == "__main__":
    # build a graph per section.
    gg = Graphify(SECTION_PATH)
    gg.process_section(1)


