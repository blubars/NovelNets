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
import os
import math
from collections import defaultdict, namedtuple
from copy import deepcopy
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
from webweb.webweb import webweb

from utils import get_sections_path
import ner

#########################################################
# Globals
#########################################################
SAVE_GRAPH_PATH = '../data/graph/'
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

def print_debug(level, s):
    if DEBUG >= level:
        print(s)

def match_to_string(match, doc):
    mid, start, end = match
    span = doc[start:end]
    return "'{}': {}, {}".format(span.text, start, end)

# store a snapshot of the graph in time.
# just a collection of vertices & edges right now.
class GraphSnapshot:
    def __init__(self, V=None, E=None, section=None):
        self.sections = []
        if section:
            self.sections.append(section)
        if V:
            self.V = V
        else:
            self.V = set()
        # edgelist is dict of dicts of weights.
        #   E[key1][key2] = weight
        if E:
            self.E = E
        else:
            self.E = defaultdict(lambda: defaultdict(int))

    def __str__(self):
        s_str = "** SECTIONS {} **\n".format(self.sections)
        v_str = "  Nodes:\n"
        for v in self.V:
            v_str += "    {}\n".format(v)
        e_str = "  Edges:\n"
        for k1,innerdict in self.E.items():
            for k2,v in innerdict.items():
                e_str += "    ({}<->{}: {})\n".format(k1, k2, v)
        return s_str + v_str + e_str

    def merge(self, other):
        merged_V = self.V + other.V
        merged_E = deepcopy(self.E)
        for k1,innerdict in other.E.items():
            for k2,v in innerdict.items():
                merged_E[k1][k2] += v
        g = GraphSnapshot(merged_V, merged_E)
        g.sections = self.sections + other.sections

    def delta(self, other):
        delta_V = self.V - other.V
        # TODO: how to handle difference btw edges?
        # might want to treat edges as binary rather than weighted 
        # for this purpose.
        delta_E = deepcopy(self.E)
        for k1,innerdict in other.E.items():
            for k2,v in innerdict.items():
                delta_E[k1][k2] -= v
        return GraphSnapshot(delta_V, delta_E)

    def save(self, path, name_id_map):
        section_num = self.sections[0]
        edge_path = "{}/{}-edgelist.txt".format(path, section_num)
        self.save_edgelist(edge_path, name_id_map)
        node_path = "{}/{}-nodelist.txt".format(path, section_num)
        self.save_nodelist(node_path, name_id_map)

    def load(self, path, name_id_map):
        section_num = self.sections[0]
        edge_path = "{}/{}-edgelist.txt".format(path, section_num)
        self.load_edgelist(edge_path, name_id_map)
        node_path = "{}/{}-nodelist.txt".format(path, section_num)
        self.load_nodelist(node_path, name_id_map)

    def save_nodelist(self, fname, name_id_map):
        with open(fname, 'w') as f:
            for key in self.V:
                node_id = name_id_map[key]
                f.write("{}\t{}\n".format(node_id, key))

    def save_edgelist(self, fname, name_id_map):
        with open(fname, 'w') as f:
            for k1,innerdict in self.E.items():
                for k2,v in innerdict.items():
                    node1 = name_id_map[k1]
                    node2 = name_id_map[k2]
                    f.write("{}\t{}\t{}\n".format(node1, node2, v))

    def load_nodelist(self, fname, name_id_map):
        with open(fname, 'r') as f:
            for line in f:
                node_id, key = line.split()
                self.V.add(key)

    def load_edgelist(self, fname, name_id_map):
        with open(fname, 'r') as f:
            for line in f:
                node1, node2, weight = line.split()
                self.E[int(node1)][int(node2)] = int(weight)


class Graphify:
    def __init__(self, path, edge_thresh, edge_repeat_thresh):
        self.section_path = path
        self.G = nx.Graph()
        self.people = set()
        self.name_id_map = {}
        self.unused_id = 0
        self.edge_threshold = edge_thresh
        self.edge_repeat_threshold = edge_repeat_thresh

        self.web = webweb()
        self.web.display.colorBy = 'degree'
        self.web.display.sizeBy = 'degree'
        self.web.display.l = 60
        self.web.display.c = 120

        self.graph_sequence = [] # list of snapshots

    def process_book(self, section_seq):
        for section_num in section_seq:
            self.process_section(section_num)
            self.add_graph_frame()

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
        missing, overlap, found = ner.find_missing_entities(doc)
        print("MISSING ENTITIES:")
        print_list(missing)
        print("FOUND ENTITIES:")
        print_list(found)
        # 1. recognize entities
        added_V = self.make_nodes(doc, matches)
        # 2. link entities. (rule?)
        added_E = self.make_edges(doc, matches)
        # 3. graph.
        # self.display_graph(str(section_num))
        snapshot = GraphSnapshot(added_V, added_E, section_num)
        self.graph_sequence.append(snapshot)
        return snapshot

    def make_nodes(self, doc, matches):
        print_debug(1, "NODES:")
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
            print_debug(1, "  New node: ({}, {})".format(key, entity_id))
            self.G.add_node(entity_id)
            self.G.nodes[entity_id]['name'] = key
        return section_people

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
            print_debug(3, "  - Skipped match b/c same entity")
            return False
        if first_start > second_start:
            return self.add_edge_from_matches(second, first)
        if second_start - first_start > self.edge_threshold:
            print_debug(3, "  - Skipped match b/c outside edge thresh")
            return False

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
        return True

    def make_edges(self, doc, matches):
        # dict for counting weights
        new_edges = defaultdict(lambda: defaultdict(int))
        # dict for tracking edge thresholds for smoothing.
        # heuristic to avoid multi-counting
        edge_block_threshs = defaultdict(lambda: defaultdict(int))
        # dumbest way possible: link if within THRESHOLD tokens of eachother.
        # note: this adds 1 edges per match pair, only in one direction.
        for i in range(len(matches)-1):
            for j in range(i+1, len(matches)):
                first = matches[i]
                second = matches[j]
                print_debug(3, "[Process match:{}, {}]"
                   .format(match_to_string(first, doc), match_to_string(second, doc)))
                key1 = self.get_entity_from_match(first)
                key2 = self.get_entity_from_match(second)
                if key1 > key2:
                    key1, key2 = key2, key1
                match_start = min(first[1], second[1])
                match_end = max(first[2], second[2])
                if match_start > edge_block_threshs[key1][key2]:
                    # don't add a new edge if we're within the blocking 
                    # threshold from the previous edge.
                    new_edge = self.add_edge_from_matches(first, second)
                    if new_edge:
                        new_edges[key1][key2] += 1
                        edge_block_threshs[key1][key2] = match_end + self.edge_repeat_threshold
                else:
                    print_debug(3, "  - Skipped match b/c within thresh ({})"
                        .format(edge_block_threshs[key1][key2]))
        print_debug(1, "EDGES:")
        for key1, inner_dict in new_edges.items():
            for key2, weight in inner_dict.items():
                print_debug(1, "  {} <--> {} ({} <--> {}), weight:+{}"
                    .format(key1, key2, self.get_entity_id(key1), \
                            self.get_entity_id(key2), weight))
        return new_edges

    def save(self, path):
        # write each snapshot to a file. also write the aggregate.
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        # write aggregate list of vertices (keys + ids) to file
        with open(path + '/aggregate_nodes.txt', 'w') as f:
            for key in self.people:
                node_id = self.get_entity_id(key)
                f.write("{}\t{}\n".format(node_id, key))
        # write complete graph
        nx.write_weighted_edgelist(self.G, path + '/aggregate_edgelist.txt')
        # write each section snapshot to file
        sect_path = path + '/sections'
        try:
            os.mkdir(path + '/sections')
        except FileExistsError:
            pass
        for snap in self.graph_sequence:
            snap.save(sect_path, self.name_id_map)

    def load(self, path, section_seq):
        # load graph from edgelist
        # load vertices
        self.people = set()
        self.G = nx.read_edgelist(path + '/aggregate_edgelist.txt', nodetype=int, data=(('weight', int),))
        with open(path + '/aggregate_nodes.txt', 'r') as f:
            for line in f:
                node_id, key = line.split()
                node_id = int(node_id)
                self.name_id_map[key] = node_id
                try:
                    self.G.nodes[node_id]['name'] = key
                except KeyError:
                    self.G.add_node(node_id, attr_dict={'name':key})
                self.people.add(key)
        self.graph_sequence = []
        sect_path = path + '/sections'
        for i in section_seq:
            snap = GraphSnapshot(section=i)
            snap.load(sect_path, self.name_id_map)
            self.graph_sequence.append(snap)


    def print_graph_edgelist(self):
        print("Graph edges & weights")
        for n, nbrsdict in self.G.adjacency():
            for nbr,eattr in nbrsdict.items():
                print((n,nbr,eattr['weight']))
        #print(self.G.edges(data='weight'))

    def add_graph_frame(self):
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
    gg = Graphify(get_sections_path(), 300, 50)
    gg.process_book(range(1,193))
    gg.save(SAVE_GRAPH_PATH)
    #gg.load(SAVE_GRAPH_PATH, range(1,5))
    #gg.web.draw()

    #for snapshot in gg.graph_sequence:
    #    print(snapshot)


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


