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
from collections import defaultdict
from copy import deepcopy
import networkx as nx
import json
import math
from utils import get_entities, get_entities_hash
import text_io
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

def print_graph(G):
    print(len(list(G.nodes)))
    print(len(G.edges()))
    print()

class Match():
    def __init__(self, match, matcher, doc):
        self.match = match
        self.key = matcher.vocab.strings[match[0]]
        self.start = match[1]
        self.end = match[2]
        self.span = doc[self.start:self.end]

    def __str__(self):
        return "'{}': {}, {}".format(self.span.text, self.start, self.end)

# store a snapshot of the graph in time.
# just a collection of vertices & edges right now.
class GraphSnapshot:
    def __init__(self, V=set(), E=defaultdict(lambda: defaultdict(int)), section=None, section_length=None):
        self.section = section
        self.section_length = section_length
        self.V = V
        # edgelist is dict of dicts of weights.
        #   E[key1][key2] = weight
        self.E = E

    def __str__(self):
        s_str = "** SECTION {} **\n".format(self.section)
        v_str = "  Nodes:\n"
        for v in self.V:
            v_str += "    {}\n".format(v)
        e_str = "  Edges:\n"
        for k1, innerdict in self.E.items():
            for k2, v in innerdict.items():
                e_str += "    ({}<->{}: {})\n".format(k1, k2, v)
        return s_str + v_str + e_str

    def merge(self, other):
        merged_V = self.V | other.V
        merged_E = deepcopy(self.E)
        for k1, innerdict in other.E.items():
            for k2, v in innerdict.items():
                merged_E[k1][k2] += v
        g = GraphSnapshot(merged_V, merged_E)
        return g

    def delta(self, other):
        delta_V = self.V - other.V
        # TODO: how to handle difference btw edges?
        # might want to treat edges as binary rather than weighted 
        # for this purpose.
        delta_E = deepcopy(self.E)
        for k1, innerdict in other.E.items():
            for k2, v in innerdict.items():
                delta_E[k1][k2] -= v
        return GraphSnapshot(delta_V, delta_E)

    def save(self, path):
        filepath = "{}/{}-snapshot.json".format(path, self.section)
        data = dict()
        data["section_id"] = self.section
        data["section_length"] = self.section_length
        data["edges"] = self.E
        data["nodes"] = list(self.V) if type(self.V) is set else self.V
        with open(filepath, 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)

    def load(self, path):
        filepath = "{}/{}-snapshot.json".format(path, self.section)
        with open(filepath, 'r') as fp:
            data = json.load(fp)
            self.section = data["section_id"]
            self.section_length = data["section_length"]
            self.E = data["edges"]
            self.V = set(data["nodes"])

    def getNXGraph(self):
        G = nx.Graph()
        entities = get_entities()

        for entity in self.V:
            add_node_attributes(G, entities, entity)
        for node1, innerdict in self.E.items():
            for node2, v in innerdict.items():
                G.add_edge(node1, node2, weight=v)
        return G


def add_node_attributes(G, entities, entity):
    entity_attributes = deepcopy(entities[entity]['attributes'])
    entity_attributes['name'] = entity

    if entity not in G.nodes():
        G.add_node(entity, **entity_attributes)
    else:
        for attribute, value in entity_attributes.items():
            G.nodes[entity][attribute] = value


class Graphify:
    def __init__(self, edge_thresh=300, edge_repeat_thresh=50, data_path=SAVE_GRAPH_PATH, sections=range(1, 193)):
        self.G = nx.Graph()
        self.people = set()
        self.unused_id = 0
        self.edge_threshold = edge_thresh
        self.edge_repeat_threshold = edge_repeat_thresh
        self.entities = get_entities()

        self.sections = sections

        self.graph_sequence = [] # list of snapshots

        self.data_path = data_path

        if self.should_reload():
            self.process_book()
            self.save()
        else:
            self.load()

    def process_book(self):
        for section_num in self.sections:
            self.process_section(section_num)
        print_graph(self.G)

    def process_section(self, section_num):
        print("+-------------------------------------")
        print("| Processing section " + str(section_num))
        print("+-------------------------------------")
        section_text = text_io.interpolate_section_endnotes(text_io.get_section(section_num))

        doc = ner.tokenize(section_text)
        self.matcher, matches = ner.match_people(doc)
        if DEBUG > 1:
            print("MATCHES:")
            for m in matches:
                print("  '{}': ({}, {})".format(
                    self.get_match_entity(m), m[1], m[2]))
        missing, overlap, found = ner.find_missing_entities(doc)
        print("MISSING ENTITIES:")
        print_list(missing)
        print("FOUND ENTITIES:")
        print_list(found)
        entity_matches = [Match(match, self.matcher, doc) for match in matches]
        # 1. recognize entities
        added_V = self.make_nodes(entity_matches)
        print(added_V)
        # 2. link entities. (rule?)
        added_E = self.make_edges(entity_matches)
        # 3. graph.
        snapshot = GraphSnapshot(V=added_V, E=added_E, section=section_num, section_length=len(doc))
        self.graph_sequence.append(snapshot)
        return snapshot

    def make_nodes(self, entity_matches):
        print_debug(1, "NODES:")
        section_people = set([match.key for match in entity_matches])
        new_people = section_people - self.people
        # keep node ids in same order each run by sorting here.
        for key in sorted(list(new_people)):
            self.people.add(key)
            print_debug(1, "  New node: ({})".format(key))

            add_node_attributes(self.G, self.entities, key)
        return section_people

    def graph_by_sections(self, sequence, aggregate=False, decay_weights=False, decay_factor=2):
        g0 = GraphSnapshot()
        for section_num in sequence:
            section_snapshot = self.graph_sequence[section_num-1]
            if aggregate:
                if decay_weights:
                    scale = self.forgetting_curve(section_snapshot.section_length, S=decay_factor)
                    self.decay_weights(g0.E, scale)
                g0 = g0.merge(section_snapshot)
                yield g0.getNXGraph()
            else:
                yield section_snapshot

    def decay_weights(self, edges, scale):
        for k1, innerdict in edges.items():
            for k2, v in innerdict.items():
                edges[k1][k2] += v * scale

    def forgetting_curve(self, length, S=2):
        return math.e**(-1 * length / S)

    def get_match_entity(self, match):
        return self.matcher.vocab.strings[match[0]]

    def add_edge_from_matches(self, first, second):
        if first.key == second.key:
            print_debug(3, "  - Skipped match b/c same entity")
            return False

        if first.start > second.start:
            first, second = second, first

        if second.start - first.start > self.edge_threshold:
            print_debug(3, "  - Skipped match b/c outside edge thresh")
            return False

        if self.G.has_edge(first.key, second.key):
            self.G[first.key][second.key]['weight'] += 1
        else:
            self.G.add_edge(first.key, second.key, weight=1)
        if DEBUG > 1:
            print("  - Incr weight ({},{}), pos=({},{})".format(
                first.key, second.key,
                first.start, second.start))
        return True

    def make_edges(self, entity_matches):
        # dict for counting weights
        new_edges = defaultdict(lambda: defaultdict(int))
        # dict for tracking edge thresholds for smoothing.
        # heuristic to avoid multi-counting
        edge_block_threshs = defaultdict(lambda: defaultdict(int))
        # dumbest way possible: link if within THRESHOLD tokens of eachother.
        # note: this adds 1 edges per match pair, only in one direction.
        for i, first in enumerate(entity_matches[:-1]):
            for second in entity_matches[i + 1:]:
                print_debug(3, "[Process match:{}, {}]".format(str(first), str(second)))
                if first.key > second.key:
                    first, second = second, first
                match_start = min(first.start, second.start)
                match_end = max(first.end, second.end)
                if match_start > edge_block_threshs[first.key][second.key]:
                    # don't add a new edge if we're within the blocking 
                    # threshold from the previous edge.
                    new_edge = self.add_edge_from_matches(first, second)
                    if new_edge:
                        new_edges[first.key][second.key] += 1
                        edge_block_threshs[first.key][second.key] = match_end + self.edge_repeat_threshold
                else:
                    print_debug(3, "  - Skipped match b/c within thresh ({})"
                        .format(edge_block_threshs[first.key][second.key]))
        print_debug(1, "EDGES:")
        for key1, inner_dict in new_edges.items():
            for key2, weight in inner_dict.items():
                print_debug(1, "  {} <--> {}, weight:+{}".format(key1, key2, weight))
        return new_edges

    def save(self):
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

        # write aggregate list of vertices (keys + ids) to file
        with open(self.aggregate_nodes_path, 'w') as f:
            for i, key in enumerate(self.people):
                f.write("{}\t{}\n".format(i, key))
        # write complete graph
        nx.write_weighted_edgelist(self.G, self.aggregate_edgelist_path)

        # write each section snapshot to file
        sect_path = self.data_path + '/sections'

        if not os.path.exists(sect_path):
            os.mkdir(sect_path)

        # write each snapshot to a file
        for snap in self.graph_sequence:
            snap.save(sect_path)

        # save entities hash to later determine if we need to rerun
        with open(self.entities_hash_path, 'w') as f:
            f.write(get_entities_hash())

    @property
    def aggregate_nodes_path(self):
        return os.path.join(self.data_path, 'aggregate_nodes.txt')

    @property
    def aggregate_edgelist_path(self):
        return os.path.join(self.data_path, 'aggregate_edgelist.txt')

    @property
    def entities_hash_path(self):
        return os.path.join(self.data_path, 'entities_hash.txt')

    def should_reload(self):
        # going to assume we have a path here
        entities_hash_path = self.entities_hash_path
        if os.path.exists(entities_hash_path):
            with open(entities_hash_path, 'r') as f:
                content = f.read().strip()

            # we should reload if the new hash is different from the old one
            if content == get_entities_hash():
                return False

        return True
    
    def load(self):
        # load graph from edgelist
        # load vertices
        self.people = set()
        self.G = nx.read_edgelist(self.aggregate_edgelist_path, nodetype=str, data=(('weight', int),))
        with open(self.aggregate_nodes_path, 'r') as f:
            for line in f:
                node_id, key = line.split()
                node_id = int(node_id)
                add_node_attributes(self.G, self.entities, key)

                if key not in self.people:
                    self.people.add(key)

        self.graph_sequence = []
        sect_path = self.data_path + '/sections'
        for i in self.sections:
            snap = GraphSnapshot(section=i)
            snap.load(sect_path)
            self.graph_sequence.append(snap)

    def print_graph_edgelist(self):
        print("Graph edges & weights")
        for n, nbrsdict in self.G.adjacency():
            for nbr, eattr in nbrsdict.items():
                print((n, nbr, eattr['weight']))

if __name__ == "__main__":
    # build a graph per section.
    gg = Graphify()
